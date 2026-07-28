import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { evolucoesApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { GravadorEvolucaoIA } from "./GravadorEvolucaoIA";
import { COLUNAS_STATUS_EVOLUCAO } from "../../constants/status";
import { KanbanBoard } from "../../components/kanban/KanbanBoard";
import { EstadoVazio } from "../../components/EstadoVazio";
import type { Evolucao } from "../../types/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

function hoje(): string {
  return new Date().toISOString().slice(0, 10);
}

export function EvolucoesSection({ pacienteId }: { pacienteId: string }) {
  const [evolucoes, setEvolucoes] = useState<Evolucao[]>([]);
  const [ultima, setUltima] = useState<Evolucao | null>(null);
  const [data, setData] = useState(hoje());
  const [texto, setTexto] = useState("");
  const [emRevisao, setEmRevisao] = useState<Evolucao | null>(null);
  const [textoRevisado, setTextoRevisado] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [emExclusao, setEmExclusao] = useState<Evolucao | null>(null);

  function recarregar() {
    evolucoesApi.listar(pacienteId).then(setEvolucoes);
    evolucoesApi
      .ultima(pacienteId)
      .then(setUltima)
      .catch(() => setUltima(null));
  }

  useEffect(recarregar, [pacienteId]);

  async function handleAdicionar(e: FormEvent) {
    e.preventDefault();
    try {
      await evolucoesApi.criar(pacienteId, { data, texto });
      setTexto("");
      setData(hoje());
      recarregar();
      toast.success("Evolução registrada");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível registrar a evolução");
    }
  }

  function handleMover(item: Evolucao, novoStatus: string) {
    if (item.status === "pendente_revisao" && novoStatus === "confirmada") {
      setTextoRevisado(item.texto);
      setEmRevisao(item);
    }
    // confirmada -> pendente_revisao nao tem suporte no backend; ignorado (card volta sozinho).
  }

  async function handleConfirmar(e: FormEvent) {
    e.preventDefault();
    if (!emRevisao) return;
    setConfirmando(true);
    try {
      await evolucoesApi.confirmar(pacienteId, emRevisao.id, textoRevisado);
      setEmRevisao(null);
      recarregar();
      toast.success("Evolução confirmada");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível confirmar a evolução");
    } finally {
      setConfirmando(false);
    }
  }

  async function handleExcluir() {
    if (!emExclusao) return;
    try {
      await evolucoesApi.deletar(pacienteId, emExclusao.id);
      setEmExclusao(null);
      recarregar();
      toast.success("Evolução excluída");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível excluir a evolução");
    }
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Evoluções</h2>

      {ultima && (
        <p className="mb-4 rounded-lg border border-accent bg-accent/50 px-3.5 py-2.5 text-sm text-accent-foreground">
          Última devolutiva: <strong>{ultima.data}</strong> — {ultima.texto}
        </p>
      )}

      <div className="mb-5">
        <GravadorEvolucaoIA pacienteId={pacienteId} onRascunhoGerado={recarregar} />
      </div>

      {evolucoes.length === 0 ? (
        <EstadoVazio icone="📝" texto="Nenhuma evolução registrada ainda." />
      ) : (
        <div className="mb-5">
          <KanbanBoard
            colunas={COLUNAS_STATUS_EVOLUCAO}
            itens={evolucoes}
            status={(e) => e.status}
            onMover={handleMover}
            renderCard={(ev) => (
              <div className="group relative flex flex-col gap-1 p-3.5 text-sm">
                <button
                  type="button"
                  onClick={() => {
                    if (ev.status === "pendente_revisao") {
                      setTextoRevisado(ev.texto);
                      setEmRevisao(ev);
                    }
                  }}
                  className="flex flex-col gap-1 pr-6 text-left"
                >
                  <strong className="font-semibold text-foreground">{ev.data}</strong>
                  <span className="line-clamp-2 text-xs text-muted-foreground">{ev.texto}</span>
                  {ev.status === "pendente_revisao" && (
                    <Badge
                      variant="outline"
                      className="mt-1 w-fit border-amber-300 bg-amber-50 text-amber-700"
                    >
                      Revisar rascunho da IA
                    </Badge>
                  )}
                </button>
                <button
                  type="button"
                  aria-label="Excluir evolução"
                  title="Excluir evolução"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEmExclusao(ev);
                  }}
                  className="absolute top-2.5 right-2.5 rounded-md p-1 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive"
                >
                  ✕
                </button>
              </div>
            )}
          />
        </div>
      )}

      <form onSubmit={handleAdicionar} className="flex max-w-lg flex-col gap-3.5">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="data-evolucao">Data</Label>
          <Input
            id="data-evolucao"
            type="date"
            value={data}
            onChange={(e) => setData(e.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="texto-evolucao">Texto</Label>
          <Textarea
            id="texto-evolucao"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            required
            rows={4}
          />
        </div>
        <Button type="submit" variant="outline" className="self-start">
          Registrar evolução manualmente
        </Button>
      </form>

      <Dialog open={emRevisao !== null} onOpenChange={(open) => !open && setEmRevisao(null)}>
        <DialogContent className="sm:max-w-lg">
          <form onSubmit={handleConfirmar} className="flex flex-col gap-4">
            <DialogHeader>
              <DialogTitle>Revisar rascunho da IA</DialogTitle>
              <DialogDescription>
                Edite o texto se necessário antes de confirmar como evolução oficial.
              </DialogDescription>
            </DialogHeader>
            <Textarea
              value={textoRevisado}
              onChange={(e) => setTextoRevisado(e.target.value)}
              rows={8}
              autoFocus
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setEmRevisao(null)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={confirmando}>
                {confirmando ? "Salvando..." : "Confirmar e salvar evolução"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={emExclusao !== null} onOpenChange={(open) => !open && setEmExclusao(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir esta evolução?</AlertDialogTitle>
            <AlertDialogDescription>
              Útil quando uma evolução foi confirmada por engano. O registro sai das listagens,
              mas o histórico é mantido no banco (soft delete) para auditoria.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleExcluir}>Excluir</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
