export type Papel = "admin" | "fono" | "secretaria";

export interface UsuarioAutenticado {
  id: string;
  clinica_id: string;
  papel: Papel;
  nome: string;
  email: string;
}

export interface TokenPar {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type StatusPaciente = "em_avaliacao" | "em_acompanhamento" | "alta";

export interface Paciente {
  id: string;
  clinica_id: string;
  nome_completo: string;
  data_nascimento: string;
  nome_mae: string;
  nome_pai: string;
  tem_irmaos: boolean;
  status: StatusPaciente;
  nome_irmaos: string | null;
  consentimento_lgpd_assinado_em: string | null;
  idade: number;
  observacoes: string | null;
  criado_em: string;
  atualizado_em: string;
  // presentes so quando o papel tem acesso clinico (admin/fono)
  diagnostico?: string | null;
  data_inicio?: string | null;
  faz_uso_medicamento?: string;
  informacoes_nascimento?: string | null;
  queixa_principal?: string | null;
}

export interface PacienteInput {
  nome_completo: string;
  data_nascimento: string;
  nome_mae: string;
  nome_pai: string;
  tem_irmaos: boolean;
  faz_uso_medicamento: string;
  nome_irmaos?: string | null;
  diagnostico?: string | null;
  data_inicio?: string | null;
  consentimento_lgpd_assinado_em?: string | null;
  informacoes_nascimento?: string | null;
  queixa_principal?: string | null;
  observacoes?: string | null;
}

export const ESPECIALIDADES = [
  "nutricionista",
  "fisioterapeuta",
  "psicologo",
  "terapeuta_ocupacional",
  "atendente_terapeutica",
  "pediatra",
  "neuropediatra",
  "psiquiatra",
  "outro",
] as const;

export interface ProfissionalCaso {
  id: string;
  clinica_id: string;
  paciente_id: string;
  nome: string;
  especialidade: string;
  contato: string | null;
  criado_em: string;
  atualizado_em: string;
}

export interface ProfissionalCasoInput {
  nome: string;
  especialidade: string;
  contato?: string | null;
}

export interface Protocolo {
  id: string;
  clinica_id: string;
  nome: string;
  descricao: string | null;
  criado_em: string;
  atualizado_em: string;
}

export interface ProtocoloInput {
  nome: string;
  descricao?: string | null;
}

export type StatusProtocoloPaciente = "realizado" | "planejado";

export interface ProtocoloPaciente {
  id: string;
  clinica_id: string;
  paciente_id: string;
  protocolo_id: string;
  status: StatusProtocoloPaciente;
  data_realizacao: string | null;
  observacao: string | null;
  criado_em: string;
  atualizado_em: string;
}

export interface ProtocoloPacienteInput {
  protocolo_id: string;
  status: StatusProtocoloPaciente;
  data_realizacao?: string | null;
  observacao?: string | null;
}

export interface CaaDados {
  id: string;
  clinica_id: string;
  paciente_id: string;
  usa_caa: boolean;
  protocolo_aip_aplicado: boolean;
  sistema_ajustado: boolean;
  observacoes: string | null;
  criado_em: string;
  atualizado_em: string;
}

export interface CaaDadosInput {
  usa_caa: boolean;
  protocolo_aip_aplicado: boolean;
  sistema_ajustado: boolean;
  observacoes?: string | null;
}

export type StatusEvolucao = "pendente_revisao" | "confirmada";

export interface Evolucao {
  id: string;
  clinica_id: string;
  paciente_id: string;
  usuario_id: string;
  data: string;
  texto: string;
  status: StatusEvolucao;
  criado_em: string;
  atualizado_em: string;
}

export interface EvolucaoInput {
  data: string;
  texto: string;
}

export const TIPOS_ARQUIVO = ["pdf", "foto", "audio", "video", "outro"] as const;
export type EntidadeAnexavel = "paciente" | "evolucao" | "protocolo_paciente";

export interface Anexo {
  id: string;
  clinica_id: string;
  entidade_tipo: EntidadeAnexavel;
  entidade_id: string;
  tipo_arquivo: string;
  nome_arquivo: string;
  storage_ref: string;
  criado_por: string;
  criado_em: string;
  atualizado_em: string;
}
