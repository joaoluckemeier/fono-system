import type { Papel } from "../types/api";

const PAPEIS_COM_ACESSO_CLINICO = new Set<Papel>(["admin", "fono"]);

export function temAcessoClinico(papel: Papel | undefined): boolean {
  return papel !== undefined && PAPEIS_COM_ACESSO_CLINICO.has(papel);
}
