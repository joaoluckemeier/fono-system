import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { protocolosApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { COLUNAS_STATUS_PROTOCOLO } from "../../constants/status";
import { KanbanBoard } from "../../components/kanban/KanbanBoard";
import { EstadoVazio } from "../../components/EstadoVazio";
import type { Protocolo, ProtocoloPaciente, StatusProtocoloPaciente } from "../../types/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
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

export function ProtocolosSection({ pacienteId }: { pacienteId: string }) {
  const [protocolos, setProtocolos] = useState<Protocolo[]>([]);
  const [aplicados, setAplicados] = useState<ProtocoloPaciente[]>([]);
  const [protocoloId, setProtocoloId] = useState("");
  const [pendenteData, setPendenteData] = useState<ProtocoloPaciente | null>(null);
  const [dataRealizacaoInput, setDataRealizacaoInput] = useState("");
  const [emExclusao, setEmExclusao] = useState<ProtocoloPaciente | null>(null);

  function recarregar() {
    protocolosApi.listarPorPaciente(pacienteId).then(setAplicados);
  }

  useEffect(() => {
    protocolosApi.listar().then((lista) => {
      setProtocolos(lista);
      if (lista.length > 0) setProtocoloId(lista[0].id);
    });
    recarregar();
  }, [pacienteId]);

  const nomePorId = new Map(protocolos.map((p) => [p.id, p.nome]));

  async function handleAssociar(e: FormEvent) {
    e.preventDefault();
    if (!protocoloId) {
      toast.error("Cadastre um protocolo no catálogo primeiro");
      return;
    }
    try {
      await protocolosApi.associarPaciente(pacienteId, { protocolo_id: protocoloId, status: "planejado" });
      recarregar();
      toast.success("Protocolo associado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível associar");
    }
  }

  async function moverParaStatus(item: ProtocoloPaciente, novoStatus: string, dataRealizacao?: string) {
    const anterior = aplicados;
    setAplicados((atual) =>
      atual.map((a) =>
        a.id === item.id
          ? { ...a, status: novoStatus as StatusProtocoloPaciente, data_realizacao: dataRealizacao ?? a.data_realizacao }
          : a,
      ),
    );
    try {
      await protocolosApi.atualizarStatusPaciente(
        pacienteId,
        item.id,
        novoStatus as StatusProtocoloPaciente,
        dataRealizacao,
      );
    } catch (err) {
      setAplicados(anterior);
      toast.error(err instanceof ApiError ? err.message : "Não foi possível mover o protocolo");
    }
  }

  function handleMover(item: ProtocoloPaciente, novoStatus: string) {
    if (novoStatus === "realizado" && !item.data_realizacao) {
      setDataRealizacaoInput(new Date().toISOString().slice(0, 10));
      setPendenteData(item);
      return;
    }
    moverParaStatus(item, novoStatus);
  }

  function confirmarDataRealizacao(e: FormEvent) {
    e.preventDefault();
    if (!pendenteData) return;
    moverParaStatus(pendenteData, "realizado", dataRealizacaoInput);
    setPendenteData(null);
  }

  async function handleExcluir() {
    if (!emExclusao) return;
    try {
      await protocolosApi.removerPaciente(pacienteId, emExclusao.id);
      setEmExclusao(null);
      recarregar();
      toast.success("Protocolo removido do paciente");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível remover o protocolo");
    }
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Protocolos</h2>

      {aplicados.length === 0 ? (
        <EstadoVazio icone="📋" texto="Nenhum protocolo associado a este paciente ainda." />
      ) : (
        <div className="mb-4">
          <KanbanBoard
            colunas={COLUNAS_STATUS_PROTOCOLO}
            itens={aplicados}
            status={(a) => a.status}
            onMover={handleMover}
            renderCard={(a) => (
              <div className="group relative flex flex-col gap-1 p-3.5 pr-6 text-sm">
                <strong className="font-semibold text-foreground">
                  {nomePorId.get(a.protocolo_id) ?? "Protocolo"}
                </strong>
                {a.data_realizacao && (
                  <span className="text-xs text-muted-foreground">Realizado em {a.data_realizacao}</span>
                )}
                <button
                  type="button"
                  aria-label="Remover protocolo"
                  title="Remover protocolo"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEmExclusao(a);
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

      <form onSubmit={handleAssociar} className="flex flex-wrap items-center gap-2.5">
        <Select value={protocoloId} onValueChange={setProtocoloId}>
          <SelectTrigger className="w-56">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {protocolos.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.nome}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button type="submit">Associar protocolo</Button>
      </form>
      {protocolos.length === 0 && (
        <p className="mt-3 text-xs text-muted-foreground">
          Nenhum protocolo no catálogo ainda — cadastre em "Protocolos" no menu.
        </p>
      )}

      <Dialog open={pendenteData !== null} onOpenChange={(open) => !open && setPendenteData(null)}>
        <DialogContent className="sm:max-w-80">
          <form onSubmit={confirmarDataRealizacao} className="flex flex-col gap-4">
            <DialogHeader>
              <DialogTitle>Data de realização</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="data-realizacao">Quando o protocolo foi realizado?</Label>
              <Input
                id="data-realizacao"
                type="date"
                required
                value={dataRealizacaoInput}
                onChange={(e) => setDataRealizacaoInput(e.target.value)}
                autoFocus
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setPendenteData(null)}>
                Cancelar
              </Button>
              <Button type="submit">Confirmar</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={emExclusao !== null} onOpenChange={(open) => !open && setEmExclusao(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remover este protocolo do paciente?</AlertDialogTitle>
            <AlertDialogDescription>
              O protocolo continua no catálogo da clínica — só a associação com este paciente é
              removida (soft delete, mantido no banco para auditoria).
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleExcluir}>Remover</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
