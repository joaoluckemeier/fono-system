import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { pacientesApi } from "../api/endpoints";
import { COLUNAS_STATUS_PACIENTE } from "../constants/status";
import type { Paciente, StatusPaciente } from "../types/api";
import { KanbanBoard } from "../components/kanban/KanbanBoard";
import { EstadoVazio } from "../components/EstadoVazio";
import { CardsSkeleton } from "../components/PageSkeleton";
import { Button } from "@/components/ui/button";

function idade(dataNascimento: string): number {
  const nascimento = new Date(dataNascimento);
  const hoje = new Date();
  let anos = hoje.getFullYear() - nascimento.getFullYear();
  const aindaNaoFezAniversario =
    hoje.getMonth() < nascimento.getMonth() ||
    (hoje.getMonth() === nascimento.getMonth() && hoje.getDate() < nascimento.getDate());
  if (aindaNaoFezAniversario) anos -= 1;
  return anos;
}

export function PacientesKanbanPage() {
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    pacientesApi
      .listar()
      .then(setPacientes)
      .finally(() => setCarregando(false));
  }, []);

  async function handleMover(paciente: Paciente, novoStatus: string) {
    const anterior = pacientes;
    setPacientes((atual) =>
      atual.map((p) => (p.id === paciente.id ? { ...p, status: novoStatus as StatusPaciente } : p)),
    );
    try {
      await pacientesApi.atualizarStatus(paciente.id, novoStatus as StatusPaciente);
    } catch {
      setPacientes(anterior);
      toast.error("Não foi possível mover o paciente");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Pacientes — quadro</h1>
        <Button asChild>
          <Link to="/pacientes/novo">+ Novo paciente</Link>
        </Button>
      </div>

      {carregando && <CardsSkeleton quantidade={3} />}

      {!carregando && pacientes.length === 0 && (
        <EstadoVazio icone="🗂️" texto="Nenhum paciente cadastrado ainda." />
      )}

      {!carregando && pacientes.length > 0 && (
        <KanbanBoard
          colunas={COLUNAS_STATUS_PACIENTE}
          itens={pacientes}
          status={(p) => p.status}
          onMover={handleMover}
          renderCard={(p) => (
            <Link to={`/pacientes/${p.id}`} className="flex flex-col gap-1 p-3.5 text-sm">
              <strong className="font-semibold text-foreground">{p.nome_completo}</strong>
              <span className="text-xs text-muted-foreground">{idade(p.data_nascimento)} anos</span>
            </Link>
          )}
        />
      )}
    </div>
  );
}
