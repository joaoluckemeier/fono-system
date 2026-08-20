import type { KanbanColunaConfig } from "../components/kanban/KanbanBoard";
import type { Prioridade, StatusEvolucao, StatusPaciente, StatusProtocoloPaciente } from "../types/api";

export const COLUNAS_STATUS_PACIENTE: KanbanColunaConfig[] = [
  { id: "em_avaliacao", titulo: "Em avaliação", cor: "#2563eb" },
  { id: "em_acompanhamento", titulo: "Em acompanhamento", cor: "#d97706" },
  { id: "alta", titulo: "Alta", cor: "#15803d" },
];

export const LABEL_STATUS_PACIENTE: Record<StatusPaciente, string> = {
  em_avaliacao: "Em avaliação",
  em_acompanhamento: "Em acompanhamento",
  alta: "Alta",
};

export const COR_STATUS_PACIENTE: Record<StatusPaciente, string> = {
  em_avaliacao: "#2563eb",
  em_acompanhamento: "#d97706",
  alta: "#15803d",
};

export const COLUNAS_STATUS_PROTOCOLO: KanbanColunaConfig[] = [
  { id: "planejado", titulo: "Planejado", cor: "#6b7280" },
  { id: "realizado", titulo: "Realizado", cor: "#15803d" },
];

export const LABEL_STATUS_PROTOCOLO: Record<StatusProtocoloPaciente, string> = {
  planejado: "Planejado",
  realizado: "Realizado",
};

export const COLUNAS_STATUS_EVOLUCAO: KanbanColunaConfig[] = [
  { id: "pendente_revisao", titulo: "Pendente de revisão", cor: "#d97706" },
  { id: "confirmada", titulo: "Confirmada", cor: "#15803d" },
];

export const LABEL_STATUS_EVOLUCAO: Record<StatusEvolucao, string> = {
  pendente_revisao: "Pendente de revisão",
  confirmada: "Confirmada",
};

export const LABEL_PRIORIDADE_TAREFA: Record<Prioridade, string> = {
  alta: "Alta",
  media: "Média",
  baixa: "Baixa",
};

export const CLASSE_BADGE_PRIORIDADE: Record<Prioridade, string> = {
  alta: "border-red-300 bg-red-50 text-red-700",
  media: "border-amber-300 bg-amber-50 text-amber-700",
  baixa: "border-slate-300 bg-slate-50 text-slate-600",
};
