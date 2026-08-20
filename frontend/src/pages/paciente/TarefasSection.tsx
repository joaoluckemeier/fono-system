import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { tarefasApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { EstadoVazio } from "../../components/EstadoVazio";
import { BotaoRemoverComConfirmacao } from "../../components/BotaoRemoverComConfirmacao";
import { TarefaItem } from "../../components/tarefas/TarefaItem";
import { EditarTarefaDialog } from "../../components/tarefas/EditarTarefaDialog";
import type { Prioridade, Tarefa } from "../../types/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

function hoje(): string {
  return new Date().toISOString().slice(0, 10);
}

export function TarefasSection({ pacienteId }: { pacienteId: string }) {
  const [tarefas, setTarefas] = useState<Tarefa[]>([]);
  const [data, setData] = useState(hoje());
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [prioridade, setPrioridade] = useState<Prioridade>("media");
  const [emEdicao, setEmEdicao] = useState<Tarefa | null>(null);

  function recarregar() {
    tarefasApi
      .listar(pacienteId)
      .then((lista) => setTarefas([...lista].sort((a, b) => a.data.localeCompare(b.data))));
  }

  useEffect(recarregar, [pacienteId]);

  async function handleAdicionar(e: FormEvent) {
    e.preventDefault();
    try {
      await tarefasApi.criar(pacienteId, { data, titulo, descricao: descricao || null, prioridade });
      setTitulo("");
      setDescricao("");
      setPrioridade("media");
      setData(hoje());
      recarregar();
      toast.success("Tarefa adicionada");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível adicionar a tarefa");
    }
  }

  async function handleToggleConcluido(tarefa: Tarefa, concluido: boolean) {
    setTarefas((atual) =>
      atual.map((t) =>
        t.id === tarefa.id
          ? { ...t, concluido, concluido_em: concluido ? new Date().toISOString() : null }
          : t,
      ),
    );
    try {
      await tarefasApi.marcarConcluido(pacienteId, tarefa.id, concluido);
    } catch (err) {
      setTarefas((atual) => atual.map((t) => (t.id === tarefa.id ? tarefa : t)));
      toast.error(err instanceof ApiError ? err.message : "Não foi possível atualizar a tarefa");
    }
  }

  async function handleExcluir(tarefa: Tarefa) {
    try {
      await tarefasApi.deletar(pacienteId, tarefa.id);
      recarregar();
      toast.success("Tarefa excluída");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível excluir a tarefa");
    }
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Planejamento terapêutico</h2>

      {tarefas.length === 0 ? (
        <EstadoVazio icone="🗓️" texto="Nenhuma tarefa planejada ainda." />
      ) : (
        <ul className="mb-5 flex flex-col">
          {tarefas.map((tarefa) => (
            <TarefaItem
              key={tarefa.id}
              tarefa={tarefa}
              onToggleConcluido={(concluido) => handleToggleConcluido(tarefa, concluido)}
              acoes={
                <>
                  <button
                    type="button"
                    className="text-xs font-medium text-primary hover:underline"
                    onClick={() => setEmEdicao(tarefa)}
                  >
                    editar
                  </button>
                  <BotaoRemoverComConfirmacao
                    titulo="Excluir esta tarefa?"
                    descricao="O registro sai das listagens, mas o histórico é mantido no banco (soft delete) para auditoria."
                    onConfirmar={() => handleExcluir(tarefa)}
                    rotulo="excluir"
                  />
                </>
              }
            />
          ))}
        </ul>
      )}

      <form onSubmit={handleAdicionar} className="flex max-w-lg flex-col gap-3.5">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="data-tarefa">Data</Label>
          <Input
            id="data-tarefa"
            type="date"
            value={data}
            onChange={(e) => setData(e.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="titulo-tarefa">Título</Label>
          <Input id="titulo-tarefa" value={titulo} onChange={(e) => setTitulo(e.target.value)} required />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="descricao-tarefa">Descrição (opcional)</Label>
          <Textarea
            id="descricao-tarefa"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            rows={2}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="prioridade-tarefa">Prioridade</Label>
          <Select value={prioridade} onValueChange={(v) => setPrioridade(v as Prioridade)}>
            <SelectTrigger id="prioridade-tarefa" className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="alta">Alta</SelectItem>
              <SelectItem value="media">Média</SelectItem>
              <SelectItem value="baixa">Baixa</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button type="submit" variant="outline" className="self-start">
          Adicionar tarefa
        </Button>
      </form>

      <EditarTarefaDialog
        tarefa={emEdicao}
        onClose={() => setEmEdicao(null)}
        onSalvo={() => {
          setEmEdicao(null);
          recarregar();
        }}
      />
    </Card>
  );
}
