import type { KanbanColunaConfig } from "../components/kanban/KanbanBoard";
import type { StatusEvolucao, StatusPaciente, StatusProtocoloPaciente } from "../types/api";

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
