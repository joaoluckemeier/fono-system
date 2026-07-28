import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { evolucoesApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { Button } from "@/components/ui/button";

interface Props {
  pacienteId: string;
  onRascunhoGerado: () => void;
}

type Estado = "ocioso" | "gravando" | "processando";

const NUM_BARRAS = 32;
const INTERVALO_AMOSTRA_MS = 80;

function formatarTempo(segundos: number): string {
  const m = Math.floor(segundos / 60)
    .toString()
    .padStart(2, "0");
  const s = (segundos % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function GravadorEvolucaoIA({ pacienteId, onRascunhoGerado }: Props) {
  const [estado, setEstado] = useState<Estado>("ocioso");
  const [segundos, setSegundos] = useState(0);
  const [niveis, setNiveis] = useState<number[]>(Array(NUM_BARRAS).fill(0.05));

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const ultimaAmostraRef = useRef(0);
  const cronometroRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      pararTudo();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    };
  }, []);

  function pararTudo() {
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    if (cronometroRef.current) clearInterval(cronometroRef.current);
    audioContextRef.current?.close().catch(() => {});
    audioContextRef.current = null;
  }

  function loopVisualizacao(timestamp: number) {
    const analyser = analyserRef.current;
    if (!analyser) return;

    if (timestamp - ultimaAmostraRef.current >= INTERVALO_AMOSTRA_MS) {
      ultimaAmostraRef.current = timestamp;
      const dados = new Uint8Array(analyser.fftSize);
      analyser.getByteTimeDomainData(dados);

      let somaAbs = 0;
      for (let i = 0; i < dados.length; i++) {
        somaAbs += Math.abs(dados[i] - 128);
      }
      const nivel = Math.min(1, (somaAbs / dados.length / 128) * 4.5);

      setNiveis((atual) => [...atual.slice(1), Math.max(0.05, nivel)]);
    }

    animationFrameRef.current = requestAnimationFrame(loopVisualizacao);
  }

  async function iniciarGravacao() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      const AudioContextCls =
        window.AudioContext ??
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioContext = new AudioContextCls();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        pararTudo();
        void processarGravacao();
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setEstado("gravando");
      setSegundos(0);
      setNiveis(Array(NUM_BARRAS).fill(0.05));

      cronometroRef.current = setInterval(() => setSegundos((s) => s + 1), 1000);
      ultimaAmostraRef.current = 0;
      animationFrameRef.current = requestAnimationFrame(loopVisualizacao);
    } catch {
      toast.error("Não foi possível acessar o microfone. Verifique a permissão do navegador.");
    }
  }

  function pararGravacao() {
    mediaRecorderRef.current?.stop();
  }

  async function processarGravacao() {
    setEstado("processando");
    try {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const arquivo = new File([blob], `sessao-${Date.now()}.webm`, { type: "audio/webm" });
      await evolucoesApi.gerarRascunho(pacienteId, arquivo);
      onRascunhoGerado();
      toast.success("Rascunho gerado — revise no quadro abaixo");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível gerar o rascunho da IA");
    } finally {
      setEstado("ocioso");
    }
  }

  if (estado === "ocioso") {
    return (
      <Button type="button" variant="outline" onClick={iniciarGravacao}>
        🎙️ Gravar áudio da sessão
      </Button>
    );
  }

  if (estado === "processando") {
    return <p className="text-sm text-muted-foreground">Transcrevendo e gerando rascunho...</p>;
  }

  return (
    <div className="flex items-center gap-3 rounded-full border border-border bg-card py-1.5 pr-1.5 pl-4 shadow-sm">
      <span className="size-2.5 shrink-0 animate-pulse rounded-full bg-destructive" aria-hidden="true" />
      <span className="w-10 shrink-0 font-mono text-sm tabular-nums text-foreground">
        {formatarTempo(segundos)}
      </span>
      <div className="flex h-8 flex-1 items-center gap-[3px] overflow-hidden">
        {niveis.map((nivel, i) => (
          <span
            key={i}
            className="w-[3px] shrink-0 rounded-full bg-primary transition-[height] duration-75"
            style={{ height: `${Math.max(8, nivel * 100)}%` }}
          />
        ))}
      </div>
      <Button
        type="button"
        variant="destructive"
        size="icon"
        onClick={pararGravacao}
        aria-label="Parar gravação"
      >
        ⏹
      </Button>
    </div>
  );
}
