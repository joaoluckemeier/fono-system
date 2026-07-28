import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { anexosApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { TIPOS_ARQUIVO, type Anexo } from "../../types/api";
import { EstadoVazio } from "../../components/EstadoVazio";
import { BotaoRemoverComConfirmacao } from "../../components/BotaoRemoverComConfirmacao";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function AnexosSection({ pacienteId }: { pacienteId: string }) {
  const [anexos, setAnexos] = useState<Anexo[]>([]);
  const [tipoArquivo, setTipoArquivo] = useState<string>(TIPOS_ARQUIVO[0]);
  const [enviando, setEnviando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function recarregar() {
    anexosApi.listar("paciente", pacienteId).then(setAnexos);
  }

  useEffect(recarregar, [pacienteId]);

  async function handleEnviar(e: FormEvent) {
    e.preventDefault();
    const arquivo = inputRef.current?.files?.[0];
    if (!arquivo) {
      toast.error("Selecione um arquivo");
      return;
    }
    setEnviando(true);
    try {
      await anexosApi.criar("paciente", pacienteId, tipoArquivo, arquivo);
      if (inputRef.current) inputRef.current.value = "";
      recarregar();
      toast.success("Anexo enviado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível enviar o anexo");
    } finally {
      setEnviando(false);
    }
  }

  async function handleRemover(id: string) {
    await anexosApi.deletar(id);
    recarregar();
    toast.success("Anexo removido");
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Anexos</h2>

      {anexos.length === 0 ? (
        <EstadoVazio icone="📎" texto="Nenhum anexo enviado." />
      ) : (
        <ul className="mb-4 flex flex-col">
          {anexos.map((a) => (
            <li
              key={a.id}
              className="flex items-center justify-between border-b border-border py-2.5 text-sm last:border-none"
            >
              <span>
                <span className="font-medium text-foreground">{a.nome_arquivo}</span>
                <span className="text-muted-foreground"> ({a.tipo_arquivo})</span>
              </span>
              <BotaoRemoverComConfirmacao
                titulo="Remover este anexo?"
                descricao={`"${a.nome_arquivo}" será removido (soft delete, mantido no banco para auditoria).`}
                onConfirmar={() => handleRemover(a.id)}
              />
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleEnviar} className="flex flex-wrap items-center gap-2.5">
        <Select value={tipoArquivo} onValueChange={setTipoArquivo}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TIPOS_ARQUIVO.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input ref={inputRef} type="file" required className="max-w-64" />
        <Button type="submit" disabled={enviando}>
          {enviando ? "Enviando..." : "Enviar"}
        </Button>
      </form>
    </Card>
  );
}
