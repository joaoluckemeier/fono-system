import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { anexosApi, modelosTermoApi, termosApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { EstadoVazio } from "../../components/EstadoVazio";
import { DocumentoPreviewDialog } from "../../components/DocumentoPreviewDialog";
import { LABEL_TIPO_MODELO_TERMO, type ModeloTermo, type TermoGerado } from "../../types/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface PreviewState {
  url: string | null;
  titulo: string;
  nomeArquivo: string;
  ehObjectUrl: boolean;
}

export function TermosSection({ pacienteId }: { pacienteId: string }) {
  const [modelos, setModelos] = useState<ModeloTermo[]>([]);
  const [termosGerados, setTermosGerados] = useState<TermoGerado[]>([]);
  const [modeloId, setModeloId] = useState("");
  const [gerando, setGerando] = useState(false);
  const [preview, setPreview] = useState<PreviewState | null>(null);

  function fecharPreview() {
    if (preview?.ehObjectUrl && preview.url) URL.revokeObjectURL(preview.url);
    setPreview(null);
  }

  const ativos = modelos.filter((m) => m.ativo);
  const nomePorModeloId = new Map(modelos.map((m) => [m.id, m]));

  function recarregarGerados() {
    termosApi.listar(pacienteId).then(setTermosGerados);
  }

  useEffect(() => {
    modelosTermoApi.listar().then((lista) => {
      setModelos(lista);
      const primeiroAtivo = lista.find((m) => m.ativo);
      if (primeiroAtivo) setModeloId(primeiroAtivo.id);
    });
    recarregarGerados();
  }, [pacienteId]);

  async function handleGerar(e: FormEvent) {
    e.preventDefault();
    if (!modeloId) return;
    setGerando(true);
    try {
      const blob = await termosApi.gerar(pacienteId, modeloId);
      const modelo = nomePorModeloId.get(modeloId);
      const nomeArquivo = `${modelo?.nome ?? "termo"}.pdf`;
      setPreview({
        url: URL.createObjectURL(blob),
        titulo: modelo?.nome ?? "Documento gerado",
        nomeArquivo,
        ehObjectUrl: true,
      });
      recarregarGerados();
      toast.success("Documento gerado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível gerar o documento");
    } finally {
      setGerando(false);
    }
  }

  async function handleAbrirHistorico(t: TermoGerado) {
    const modelo = nomePorModeloId.get(t.modelo_id);
    setPreview({
      url: null,
      titulo: modelo?.nome ?? "Documento gerado",
      nomeArquivo: `${modelo?.nome ?? "termo"}.pdf`,
      ehObjectUrl: false,
    });
    try {
      const { url } = await anexosApi.obterUrl(t.anexo_id);
      setPreview((atual) => (atual ? { ...atual, url } : atual));
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível abrir o documento");
      setPreview(null);
    }
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Termos e encaminhamentos</h2>

      {termosGerados.length === 0 ? (
        <EstadoVazio icone="📄" texto="Nenhum documento gerado ainda." />
      ) : (
        <ul className="mb-4 flex flex-col">
          {termosGerados.map((t) => {
            const modelo = nomePorModeloId.get(t.modelo_id);
            return (
              <li key={t.id} className="border-b border-border last:border-none">
                <button
                  type="button"
                  onClick={() => handleAbrirHistorico(t)}
                  className="flex w-full items-center justify-between py-2.5 text-left text-sm hover:opacity-70"
                >
                  <span className="flex items-center gap-2.5">
                    <strong className="font-medium text-foreground">{modelo?.nome ?? "Modelo removido"}</strong>
                    {modelo && <Badge variant="outline">{LABEL_TIPO_MODELO_TERMO[modelo.tipo]}</Badge>}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(t.criado_em).toLocaleDateString("pt-BR")}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {ativos.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          Nenhum modelo ativo no catálogo ainda — cadastre em "Termos" no menu.
        </p>
      ) : (
        <form onSubmit={handleGerar} className="flex flex-wrap items-center gap-2.5">
          <Select value={modeloId} onValueChange={setModeloId}>
            <SelectTrigger className="w-64">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ativos.map((m) => (
                <SelectItem key={m.id} value={m.id}>
                  {m.nome} ({LABEL_TIPO_MODELO_TERMO[m.tipo]})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button type="submit" disabled={gerando}>
            {gerando ? "Gerando..." : "Gerar documento"}
          </Button>
        </form>
      )}

      <DocumentoPreviewDialog
        aberto={preview !== null}
        onFechar={fecharPreview}
        url={preview?.url ?? null}
        titulo={preview?.titulo ?? ""}
        nomeArquivo={preview?.nomeArquivo ?? "documento.pdf"}
      />
    </Card>
  );
}
