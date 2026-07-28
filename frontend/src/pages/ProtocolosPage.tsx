import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { protocolosApi } from "../api/endpoints";
import { ApiError } from "../api/client";
import type { Protocolo } from "../types/api";
import { EstadoVazio } from "../components/EstadoVazio";
import { ListSkeleton } from "../components/PageSkeleton";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

export function ProtocolosPage() {
  const [protocolos, setProtocolos] = useState<Protocolo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [busca, setBusca] = useState("");
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");

  function recarregar() {
    protocolosApi.listar().then(setProtocolos);
  }

  useEffect(() => {
    recarregar();
    setCarregando(false);
  }, []);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    if (!termo) return protocolos;
    return protocolos.filter((p) => p.nome.toLowerCase().includes(termo));
  }, [protocolos, busca]);

  async function handleCriar(e: FormEvent) {
    e.preventDefault();
    try {
      await protocolosApi.criar({ nome, descricao: descricao || null });
      setNome("");
      setDescricao("");
      recarregar();
      toast.success("Protocolo cadastrado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível criar o protocolo");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <h1 className="text-2xl font-bold tracking-tight text-foreground">Catálogo de protocolos</h1>

      <Input
        placeholder="Buscar por nome..."
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        className="max-w-xs"
      />

      <Card className="p-6">
        {carregando ? (
          <ListSkeleton linhas={3} />
        ) : filtrados.length === 0 ? (
          <EstadoVazio
            icone="📋"
            texto={busca ? "Nenhum protocolo encontrado." : "Nenhum protocolo cadastrado ainda."}
          />
        ) : (
          <ul className="flex flex-col">
            {filtrados.map((p) => (
              <li key={p.id} className="border-b border-border py-2.5 text-sm last:border-none">
                <strong className="font-medium text-foreground">{p.nome}</strong>
                {p.descricao && <span className="text-muted-foreground"> — {p.descricao}</span>}
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="max-w-md p-6">
        <h2 className="mb-4 text-base font-semibold text-foreground">Novo protocolo</h2>
        <form onSubmit={handleCriar} className="flex flex-col gap-3.5">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="nome-protocolo">Nome</Label>
            <Input
              id="nome-protocolo"
              placeholder="ex: ABFW"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="descricao-protocolo">Descrição (opcional)</Label>
            <Input
              id="descricao-protocolo"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
            />
          </div>
          <Button type="submit" className="self-start">
            Adicionar
          </Button>
        </form>
      </Card>
    </div>
  );
}
