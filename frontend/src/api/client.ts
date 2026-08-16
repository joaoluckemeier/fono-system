import { tokenStore } from "./tokenStore";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export class SessaoExpiradaError extends Error {}

let refreshEmAndamento: Promise<boolean> | null = null;

async function tentarRenovarToken(): Promise<boolean> {
  const refreshToken = tokenStore.getRefreshToken();
  if (!refreshToken) return false;

  if (!refreshEmAndamento) {
    refreshEmAndamento = (async () => {
      try {
        const response = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!response.ok) return false;
        const data = await response.json();
        tokenStore.setTokens(data.access_token, data.refresh_token);
        return true;
      } catch {
        return false;
      } finally {
        refreshEmAndamento = null;
      }
    })();
  }
  return refreshEmAndamento;
}

function paraMensagemLegivel(valor: unknown, status: number): string {
  if (typeof valor === "string") return valor;
  if (Array.isArray(valor)) {
    // Erro de validacao do FastAPI/Pydantic: lista de { msg, loc, ... }.
    const mensagens = valor
      .map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : null))
      .filter((m): m is string => m !== null);
    if (mensagens.length > 0) return mensagens.join("; ");
  }
  return `Erro ${status}`;
}

async function extrairMensagemDeErro(response: Response): Promise<string> {
  try {
    const data = await response.json();
    return paraMensagemLegivel(data.detail ?? data.error, response.status);
  } catch {
    return `Erro ${response.status}`;
  }
}

interface ApiFetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  isFormData?: boolean;
  semAutenticacao?: boolean;
}

async function fetchComAuth(path: string, options: ApiFetchOptions): Promise<Response> {
  const { body, isFormData, semAutenticacao, headers, ...rest } = options;

  const montarHeaders = (): HeadersInit => {
    const h: Record<string, string> = { ...(headers as Record<string, string>) };
    if (!isFormData) h["Content-Type"] = "application/json";
    if (!semAutenticacao) {
      const token = tokenStore.getAccessToken();
      if (token) h["Authorization"] = `Bearer ${token}`;
    }
    return h;
  };

  const montarBody = () => {
    if (body === undefined) return undefined;
    return isFormData ? (body as FormData) : JSON.stringify(body);
  };

  let response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: montarHeaders(),
    body: montarBody(),
  });

  if (response.status === 401 && !semAutenticacao) {
    const renovou = await tentarRenovarToken();
    if (renovou) {
      response = await fetch(`${API_URL}${path}`, {
        ...rest,
        headers: montarHeaders(),
        body: montarBody(),
      });
    } else {
      tokenStore.clear();
      throw new SessaoExpiradaError("Sessao expirada");
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, await extrairMensagemDeErro(response));
  }

  return response;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const response = await fetchComAuth(path, options);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function apiFetchBlob(path: string, options: ApiFetchOptions = {}): Promise<Blob> {
  const response = await fetchComAuth(path, options);
  return response.blob();
}
