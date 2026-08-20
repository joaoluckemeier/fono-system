import { useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { tarefasApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import type { Prioridade, Tarefa } from "../../types/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface Props {
  tarefa: Tarefa | null;
  onClose: () => void;
  onSalvo: () => void;
}

export function EditarTarefaDialog({ tarefa, onClose, onSalvo }: Props) {
  const [salvando, setSalvando] = useState(false);
  const [campos, setCampos] = useState<Tarefa | null>(tarefa);

  if (tarefa && campos?.id !== tarefa.id) {
    setCampos(tarefa);
  }

  async function handleSalvar(e: FormEvent) {
    e.preventDefault();
    if (!campos) return;
    setSalvando(true);
    try {
      await tarefasApi.atualizar(campos.paciente_id, campos.id, {
        data: campos.data,
        titulo: campos.titulo,
        descricao: campos.descricao,
        prioridade: campos.prioridade,
      });
      onSalvo();
      toast.success("Tarefa atualizada");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível atualizar a tarefa");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <Dialog open={tarefa !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg">
        {campos && (
          <form onSubmit={handleSalvar} className="flex flex-col gap-4">
            <DialogHeader>
              <DialogTitle>Editar tarefa</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="data-edicao">Data</Label>
              <Input
                id="data-edicao"
                type="date"
                value={campos.data}
                onChange={(e) => setCampos({ ...campos, data: e.target.value })}
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="titulo-edicao">Título</Label>
              <Input
                id="titulo-edicao"
                value={campos.titulo}
                onChange={(e) => setCampos({ ...campos, titulo: e.target.value })}
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="descricao-edicao">Descrição</Label>
              <Textarea
                id="descricao-edicao"
                value={campos.descricao ?? ""}
                onChange={(e) => setCampos({ ...campos, descricao: e.target.value || null })}
                rows={3}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="prioridade-edicao">Prioridade</Label>
              <Select
                value={campos.prioridade}
                onValueChange={(v) => setCampos({ ...campos, prioridade: v as Prioridade })}
              >
                <SelectTrigger id="prioridade-edicao" className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="alta">Alta</SelectItem>
                  <SelectItem value="media">Média</SelectItem>
                  <SelectItem value="baixa">Baixa</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancelar
              </Button>
              <Button type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
