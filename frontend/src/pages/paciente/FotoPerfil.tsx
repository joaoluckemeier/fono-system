import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { anexosApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";

function iniciais(nomeCompleto: string): string {
  const partes = nomeCompleto.trim().split(/\s+/);
  const primeira = partes[0]?.[0] ?? "";
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (primeira + ultima).toUpperCase();
}

export function FotoPerfil({
  pacienteId,
  nomeCompleto,
}: {
  pacienteId: string;
  nomeCompleto: string;
}) {
  const [url, setUrl] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function recarregar() {
    let ativo = true;
    anexosApi
      .listar("paciente", pacienteId)
      .then((anexos) => {
        const fotos = anexos
          .filter((a) => a.tipo_arquivo === "foto")
          .sort((a, b) => (a.criado_em < b.criado_em ? 1 : -1));
        const maisRecente = fotos[0];
        if (!maisRecente) {
          setUrl(null);
          return;
        }
        return anexosApi.obterUrl(maisRecente.id).then((res) => {
          if (ativo) setUrl(res.url);
        });
      })
      .catch(() => setUrl(null));
    return () => {
      ativo = false;
    };
  }

  useEffect(() => recarregar(), [pacienteId]);

  async function handleTrocarFoto(arquivo: File) {
    setEnviando(true);
    try {
      await anexosApi.criar("paciente", pacienteId, "foto", arquivo);
      recarregar();
      toast.success("Foto atualizada");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível enviar a foto");
    } finally {
      setEnviando(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      disabled={enviando}
      title="Trocar foto do paciente"
      className="group relative h-12 w-12 shrink-0 rounded-full"
    >
      {url ? (
        <img
          src={url}
          alt={`Foto de ${nomeCompleto}`}
          className="h-12 w-12 rounded-full object-cover"
        />
      ) : (
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground">
          {iniciais(nomeCompleto)}
        </div>
      )}
      <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 text-[10px] font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
        {enviando ? "..." : "trocar"}
      </span>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => {
          const arquivo = e.target.files?.[0];
          if (arquivo) handleTrocarFoto(arquivo);
        }}
      />
    </button>
  );
}
