import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { planejamentoApi, tarefasApi } from "../api/endpoints";
import { ApiError } from "../api/client";
import { TarefaItem } from "../components/tarefas/TarefaItem";
import { EditarTarefaDialog } from "../components/tarefas/EditarTarefaDialog";
import { NovaTarefaDialog } from "../components/tarefas/NovaTarefaDialog";
import { BotaoRemoverComConfirmacao } from "../components/BotaoRemoverComConfirmacao";
import { EstadoVazio } from "../components/EstadoVazio";
import { ListSkeleton } from "../components/PageSkeleton";
import type { Tarefa, TarefasPorPaciente } from "../types/api";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

function paraISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function inicioDaSemana(base: Date): Date {
  const d = new Date(base);
  const diaSemana = d.getDay(); // 0 = domingo, 1 = segunda, ...
  const deslocamento = diaSemana === 0 ? -6 : 1 - diaSemana;
  d.setDate(d.getDate() + deslocamento);
  return d;
}

function semanaAtual(): { inicio: string; fim: string } {
  const inicio = inicioDaSemana(new Date());
  const fim = new Date(inicio);
  fim.setDate(fim.getDate() + 6);
  return { inicio: paraISO(inicio), fim: paraISO(fim) };
}

export function PlanejamentoSemanaPage() {
  const semanaInicial = semanaAtual();
  const [dataInicio, setDataInicio] = useState(semanaInicial.inicio);
  const [dataFim, setDataFim] = useState(semanaInicial.fim);
  const [cards, setCards] = useState<TarefasPorPaciente[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novaTarefaAberta, setNovaTarefaAberta] = useState(false);
  const [emEdicao, setEmEdicao] = useState<Tarefa | null>(null);

  function recarregar() {
    setCarregando(true);
    planejamentoApi
      .semana(dataInicio, dataFim)
      .then(setCards)
      .finally(() => setCarregando(false));
  }

  useEffect(recarregar, [dataInicio, dataFim]);

  function deslocarSemana(dias: number) {
    const novoInicio = new Date(`${dataInicio}T00:00:00`);
    novoInicio.setDate(novoInicio.getDate() + dias);
    const novoFim = new Date(novoInicio);
    novoFim.setDate(novoFim.getDate() + 6);
    setDataInicio(paraISO(novoInicio));
    setDataFim(paraISO(novoFim));
  }

  function irParaSemanaAtual() {
    const atual = semanaAtual();
    setDataInicio(atual.inicio);
    setDataFim(atual.fim);
  }

  async function handleToggleConcluido(pacienteId: string, tarefaId: string, concluido: boolean) {
    setCards((atual) =>
      atual.map((card) =>
        card.paciente_id !== pacienteId
          ? card
          : {
              ...card,
              tarefas: card.tarefas.map((t) =>
                t.id === tarefaId
                  ? { ...t, concluido, concluido_em: concluido ? new Date().toISOString() : null }
                  : t,
              ),
            },
      ),
    );
    try {
      await tarefasApi.marcarConcluido(pacienteId, tarefaId, concluido);
    } catch (err) {
      recarregar();
      toast.error(err instanceof ApiError ? err.message : "Não foi possível atualizar a tarefa");
    }
  }

  async function handleExcluir(tarefa: Tarefa) {
    try {
      await tarefasApi.deletar(tarefa.paciente_id, tarefa.id);
      recarregar();
      toast.success("Tarefa excluída");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível excluir a tarefa");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Planejamento da semana</h1>
        <Button type="button" onClick={() => setNovaTarefaAberta(true)}>
          + Nova tarefa
        </Button>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <Button type="button" variant="outline" size="sm" onClick={() => deslocarSemana(-7)}>
          ◀ Semana anterior
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={irParaSemanaAtual}>
          Semana atual
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => deslocarSemana(7)}>
          Próxima semana ▶
        </Button>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="data-inicio-semana">De</Label>
          <Input
            id="data-inicio-semana"
            type="date"
            value={dataInicio}
            onChange={(e) => setDataInicio(e.target.value)}
            className="w-40"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="data-fim-semana">Até</Label>
          <Input
            id="data-fim-semana"
            type="date"
            value={dataFim}
            onChange={(e) => setDataFim(e.target.value)}
            className="w-40"
          />
        </div>
      </div>

      {carregando ? (
        <ListSkeleton linhas={4} />
      ) : cards.length === 0 ? (
        <EstadoVazio icone="🗓️" texto="Nenhuma tarefa planejada para este período." />
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {cards.map((card) => (
            <Card key={card.paciente_id} className="p-6">
              <Link
                to={`/pacientes/${card.paciente_id}`}
                className="mb-3 block text-base font-semibold text-foreground hover:underline"
              >
                {card.paciente_nome}
              </Link>
              <ul className="flex flex-col">
                {card.tarefas.map((tarefa) => (
                  <TarefaItem
                    key={tarefa.id}
                    tarefa={tarefa}
                    onToggleConcluido={(concluido) =>
                      handleToggleConcluido(card.paciente_id, tarefa.id, concluido)
                    }
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
            </Card>
          ))}
        </div>
      )}

      <NovaTarefaDialog
        aberto={novaTarefaAberta}
        onClose={() => setNovaTarefaAberta(false)}
        onCriada={() => {
          setNovaTarefaAberta(false);
          recarregar();
        }}
      />

      <EditarTarefaDialog
        tarefa={emEdicao}
        onClose={() => setEmEdicao(null)}
        onSalvo={() => {
          setEmEdicao(null);
          recarregar();
        }}
      />
    </div>
  );
}
