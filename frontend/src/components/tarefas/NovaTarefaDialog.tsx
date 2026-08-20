import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { pacientesApi, tarefasApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import type { Paciente, Prioridade } from "../../types/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

function hoje(): string {
  return new Date().toISOString().slice(0, 10);
}

interface Props {
  aberto: boolean;
  onClose: () => void;
  onCriada: () => void;
}

export function NovaTarefaDialog({ aberto, onClose, onCriada }: Props) {
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [buscaPaciente, setBuscaPaciente] = useState("");
  const [pacienteSelecionado, setPacienteSelecionado] = useState<Paciente | null>(null);
  const [data, setData] = useState(hoje());
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [prioridade, setPrioridade] = useState<Prioridade>("media");
  const [criando, setCriando] = useState(false);

  useEffect(() => {
    if (aberto) pacientesApi.listar().then(setPacientes);
  }, [aberto]);

  const resultadosBusca = useMemo(() => {
    const termo = buscaPaciente.trim().toLowerCase();
    if (!termo || pacienteSelecionado) return [];
    return pacientes.filter((p) => p.nome_completo.toLowerCase().includes(termo)).slice(0, 8);
  }, [buscaPaciente, pacientes, pacienteSelecionado]);

  function selecionarPaciente(p: Paciente) {
    setPacienteSelecionado(p);
    setBuscaPaciente(p.nome_completo);
  }

  function limparPaciente() {
    setPacienteSelecionado(null);
    setBuscaPaciente("");
  }

  function limparFormulario() {
    limparPaciente();
    setData(hoje());
    setTitulo("");
    setDescricao("");
    setPrioridade("media");
  }

  function handleFechar() {
    limparFormulario();
    onClose();
  }

  async function handleCriar(e: FormEvent) {
    e.preventDefault();
    if (!pacienteSelecionado) return;
    setCriando(true);
    try {
      await tarefasApi.criar(pacienteSelecionado.id, {
        data,
        titulo,
        descricao: descricao || null,
        prioridade,
      });
      toast.success(`Tarefa adicionada para ${pacienteSelecionado.nome_completo}`);
      limparFormulario();
      onCriada();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível adicionar a tarefa");
    } finally {
      setCriando(false);
    }
  }

  return (
    <Dialog open={aberto} onOpenChange={(open) => !open && handleFechar()}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleCriar} className="flex flex-col gap-4">
          <DialogHeader>
            <DialogTitle>Nova tarefa</DialogTitle>
          </DialogHeader>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="busca-paciente-tarefa">Paciente</Label>
            <div className="relative">
              <Input
                id="busca-paciente-tarefa"
                placeholder="Buscar por nome..."
                value={buscaPaciente}
                onChange={(e) => {
                  setBuscaPaciente(e.target.value);
                  if (pacienteSelecionado) setPacienteSelecionado(null);
                }}
                autoComplete="off"
                required
              />
              {resultadosBusca.length > 0 && (
                <ul className="absolute z-10 mt-1 w-full rounded-lg border border-border bg-popover shadow-md">
                  {resultadosBusca.map((p) => (
                    <li key={p.id}>
                      <button
                        type="button"
                        onClick={() => selecionarPaciente(p)}
                        className="w-full px-3 py-2 text-left text-sm hover:bg-muted"
                      >
                        {p.nome_completo}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {pacienteSelecionado && (
              <Badge variant="outline" className="w-fit gap-1.5">
                {pacienteSelecionado.nome_completo}
                <button type="button" onClick={limparPaciente} className="text-muted-foreground hover:text-foreground">
                  ✕
                </button>
              </Badge>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="data-nova-tarefa">Data</Label>
            <Input
              id="data-nova-tarefa"
              type="date"
              value={data}
              onChange={(e) => setData(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="titulo-nova-tarefa">Título</Label>
            <Input
              id="titulo-nova-tarefa"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="descricao-nova-tarefa">Descrição (opcional)</Label>
            <Textarea
              id="descricao-nova-tarefa"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              rows={2}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="prioridade-nova-tarefa">Prioridade</Label>
            <Select value={prioridade} onValueChange={(v) => setPrioridade(v as Prioridade)}>
              <SelectTrigger id="prioridade-nova-tarefa" className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="alta">Alta</SelectItem>
                <SelectItem value="media">Média</SelectItem>
                <SelectItem value="baixa">Baixa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleFechar}>
              Cancelar
            </Button>
            <Button type="submit" disabled={!pacienteSelecionado || criando}>
              {criando ? "Adicionando..." : "Adicionar tarefa"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
