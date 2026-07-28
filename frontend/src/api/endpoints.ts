import { apiFetch } from "./client";
import type {
  Anexo,
  CaaDados,
  CaaDadosInput,
  Evolucao,
  EvolucaoInput,
  Paciente,
  PacienteInput,
  ProfissionalCaso,
  ProfissionalCasoInput,
  Protocolo,
  ProtocoloInput,
  ProtocoloPaciente,
  ProtocoloPacienteInput,
  StatusPaciente,
  StatusProtocoloPaciente,
  TokenPar,
  UsuarioAutenticado,
} from "../types/api";

export const authApi = {
  login: (email: string, senha: string) =>
    apiFetch<TokenPar>("/auth/login", { method: "POST", body: { email, senha }, semAutenticacao: true }),
  me: () => apiFetch<UsuarioAutenticado>("/auth/me"),
};

export const pacientesApi = {
  listar: () => apiFetch<Paciente[]>("/pacientes"),
  buscar: (id: string) => apiFetch<Paciente>(`/pacientes/${id}`),
  criar: (dados: PacienteInput) => apiFetch<Paciente>("/pacientes", { method: "POST", body: dados }),
  atualizar: (id: string, dados: PacienteInput) =>
    apiFetch<Paciente>(`/pacientes/${id}`, { method: "PUT", body: dados }),
  atualizarStatus: (id: string, status: StatusPaciente) =>
    apiFetch<Paciente>(`/pacientes/${id}/status`, { method: "PATCH", body: { status } }),
  deletar: (id: string) => apiFetch<void>(`/pacientes/${id}`, { method: "DELETE" }),
};

export const profissionaisApi = {
  listar: (pacienteId: string) =>
    apiFetch<ProfissionalCaso[]>(`/pacientes/${pacienteId}/profissionais`),
  criar: (pacienteId: string, dados: ProfissionalCasoInput) =>
    apiFetch<ProfissionalCaso>(`/pacientes/${pacienteId}/profissionais`, {
      method: "POST",
      body: dados,
    }),
  deletar: (id: string) => apiFetch<void>(`/profissionais/${id}`, { method: "DELETE" }),
};

export const protocolosApi = {
  listar: () => apiFetch<Protocolo[]>("/protocolos"),
  criar: (dados: ProtocoloInput) => apiFetch<Protocolo>("/protocolos", { method: "POST", body: dados }),
  listarPorPaciente: (pacienteId: string) =>
    apiFetch<ProtocoloPaciente[]>(`/pacientes/${pacienteId}/protocolos`),
  associarPaciente: (pacienteId: string, dados: ProtocoloPacienteInput) =>
    apiFetch<ProtocoloPaciente>(`/pacientes/${pacienteId}/protocolos`, {
      method: "POST",
      body: dados,
    }),
  atualizarStatusPaciente: (
    pacienteId: string,
    id: string,
    status: StatusProtocoloPaciente,
    dataRealizacao?: string | null,
  ) =>
    apiFetch<ProtocoloPaciente>(`/pacientes/${pacienteId}/protocolos/${id}`, {
      method: "PATCH",
      body: { status, data_realizacao: dataRealizacao ?? null },
    }),
  removerPaciente: (pacienteId: string, id: string) =>
    apiFetch<void>(`/pacientes/${pacienteId}/protocolos/${id}`, { method: "DELETE" }),
};

export const caaApi = {
  buscar: (pacienteId: string) => apiFetch<CaaDados>(`/pacientes/${pacienteId}/caa`),
  atualizar: (pacienteId: string, dados: CaaDadosInput) =>
    apiFetch<CaaDados>(`/pacientes/${pacienteId}/caa`, { method: "PUT", body: dados }),
};

export const evolucoesApi = {
  listar: (pacienteId: string) => apiFetch<Evolucao[]>(`/pacientes/${pacienteId}/evolucoes`),
  criar: (pacienteId: string, dados: EvolucaoInput) =>
    apiFetch<Evolucao>(`/pacientes/${pacienteId}/evolucoes`, { method: "POST", body: dados }),
  ultima: (pacienteId: string) => apiFetch<Evolucao>(`/pacientes/${pacienteId}/evolucoes/ultima`),
  gerarRascunho: (pacienteId: string, arquivo: File) => {
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    return apiFetch<Evolucao>(`/pacientes/${pacienteId}/evolucoes/gerar-rascunho`, {
      method: "POST",
      body: formData,
      isFormData: true,
    });
  },
  confirmar: (pacienteId: string, id: string, textoFinal?: string) =>
    apiFetch<Evolucao>(`/pacientes/${pacienteId}/evolucoes/${id}/confirmar`, {
      method: "PATCH",
      body: { texto_final: textoFinal ?? null },
    }),
  deletar: (pacienteId: string, id: string) =>
    apiFetch<void>(`/pacientes/${pacienteId}/evolucoes/${id}`, { method: "DELETE" }),
};

export const anexosApi = {
  listar: (entidadeTipo: string, entidadeId: string) =>
    apiFetch<Anexo[]>(`/anexos?entidade_tipo=${entidadeTipo}&entidade_id=${entidadeId}`),
  criar: (entidadeTipo: string, entidadeId: string, tipoArquivo: string, arquivo: File) => {
    const formData = new FormData();
    formData.append("entidade_tipo", entidadeTipo);
    formData.append("entidade_id", entidadeId);
    formData.append("tipo_arquivo", tipoArquivo);
    formData.append("arquivo", arquivo);
    return apiFetch<Anexo>("/anexos", { method: "POST", body: formData, isFormData: true });
  },
  deletar: (id: string) => apiFetch<void>(`/anexos/${id}`, { method: "DELETE" }),
};
