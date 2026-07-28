import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { pacientesApi } from "../api/endpoints";
import { COR_STATUS_PACIENTE, LABEL_STATUS_PACIENTE } from "../constants/status";
import { StatusBadge } from "../components/StatusBadge";
import { EstadoVazio } from "../components/EstadoVazio";
import { ListSkeleton } from "../components/PageSkeleton";
import type { Paciente } from "../types/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export function PacientesListPage() {
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [busca, setBusca] = useState("");

  useEffect(() => {
    pacientesApi
      .listar()
      .then(setPacientes)
      .catch(() => toast.error("Não foi possível carregar os pacientes"))
      .finally(() => setCarregando(false));
  }, []);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    if (!termo) return pacientes;
    return pacientes.filter((p) => p.nome_completo.toLowerCase().includes(termo));
  }, [pacientes, busca]);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Pacientes</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link to="/pacientes/kanban">Ver como quadro</Link>
          </Button>
          <Button asChild>
            <Link to="/pacientes/novo">+ Novo paciente</Link>
          </Button>
        </div>
      </div>

      <Input
        placeholder="Buscar por nome..."
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        className="max-w-xs"
      />

      {carregando && <ListSkeleton />}

      {!carregando && filtrados.length === 0 && (
        <Card className="p-2">
          <EstadoVazio
            icone="🗂️"
            texto={busca ? "Nenhum paciente encontrado." : "Nenhum paciente cadastrado ainda."}
          />
        </Card>
      )}

      {filtrados.length > 0 && (
        <Card className="overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-3 text-left text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Nome
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Data de nascimento
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Status
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {filtrados.map((paciente) => (
                <tr key={paciente.id} className="border-b border-border last:border-none hover:bg-accent/40">
                  <td className="px-4 py-3 font-medium text-foreground">{paciente.nome_completo}</td>
                  <td className="px-4 py-3 text-muted-foreground">{paciente.data_nascimento}</td>
                  <td className="px-4 py-3">
                    <StatusBadge
                      texto={LABEL_STATUS_PACIENTE[paciente.status]}
                      cor={COR_STATUS_PACIENTE[paciente.status]}
                    />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/pacientes/${paciente.id}`}
                      className="text-sm font-medium text-primary hover:underline"
                    >
                      Abrir
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
