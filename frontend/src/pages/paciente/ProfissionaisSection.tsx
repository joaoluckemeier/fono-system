import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { profissionaisApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import { ESPECIALIDADES, type ProfissionalCaso } from "../../types/api";
import { EstadoVazio } from "../../components/EstadoVazio";
import { BotaoRemoverComConfirmacao } from "../../components/BotaoRemoverComConfirmacao";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function ProfissionaisSection({ pacienteId }: { pacienteId: string }) {
  const [profissionais, setProfissionais] = useState<ProfissionalCaso[]>([]);
  const [nome, setNome] = useState("");
  const [especialidade, setEspecialidade] = useState<string>(ESPECIALIDADES[0]);
  const [contato, setContato] = useState("");

  function recarregar() {
    profissionaisApi.listar(pacienteId).then(setProfissionais);
  }

  useEffect(recarregar, [pacienteId]);

  async function handleAdicionar(e: FormEvent) {
    e.preventDefault();
    try {
      await profissionaisApi.criar(pacienteId, { nome, especialidade, contato: contato || null });
      setNome("");
      setContato("");
      recarregar();
      toast.success("Profissional adicionado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível adicionar");
    }
  }

  async function handleRemover(id: string) {
    await profissionaisApi.deletar(id);
    recarregar();
    toast.success("Profissional removido");
  }

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">Profissionais do caso</h2>

      {profissionais.length === 0 ? (
        <EstadoVazio icone="🩺" texto="Nenhum profissional cadastrado." />
      ) : (
        <ul className="mb-4 flex flex-col">
          {profissionais.map((p) => (
            <li
              key={p.id}
              className="flex items-center justify-between border-b border-border py-2.5 text-sm last:border-none"
            >
              <span>
                <span className="font-medium text-foreground">{p.nome}</span>
                <span className="text-muted-foreground"> — {p.especialidade}</span>
                {p.contato && <span className="text-muted-foreground"> ({p.contato})</span>}
              </span>
              <BotaoRemoverComConfirmacao
                titulo="Remover este profissional do caso?"
                descricao={`"${p.nome}" será removido da lista de profissionais deste paciente (soft delete, mantido no banco para auditoria).`}
                onConfirmar={() => handleRemover(p.id)}
              />
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleAdicionar} className="flex flex-wrap items-end gap-2.5">
        <Input
          placeholder="Nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
          className="max-w-48"
        />
        <Select value={especialidade} onValueChange={setEspecialidade}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ESPECIALIDADES.map((e) => (
              <SelectItem key={e} value={e}>
                {e}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          placeholder="Contato (opcional)"
          value={contato}
          onChange={(e) => setContato(e.target.value)}
          className="max-w-48"
        />
        <Button type="submit">Adicionar</Button>
      </form>
    </Card>
  );
}
