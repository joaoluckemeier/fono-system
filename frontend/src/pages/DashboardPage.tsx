import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { pacientesApi } from "../api/endpoints";
import { useAuth } from "../auth/AuthContext";
import { COR_STATUS_PACIENTE, LABEL_STATUS_PACIENTE } from "../constants/status";
import type { Paciente, StatusPaciente } from "../types/api";
import { StatusBadge } from "../components/StatusBadge";
import { EstadoVazio } from "../components/EstadoVazio";
import { CardsSkeleton, ListSkeleton } from "../components/PageSkeleton";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function DashboardPage() {
  const { usuario } = useAuth();
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    pacientesApi
      .listar()
      .then(setPacientes)
      .finally(() => setCarregando(false));
  }, []);

  const contagemPorStatus = useMemo(() => {
    const base: Record<StatusPaciente, number> = { em_avaliacao: 0, em_acompanhamento: 0, alta: 0 };
    for (const p of pacientes) base[p.status] += 1;
    return base;
  }, [pacientes]);

  const ultimosPacientes = useMemo(
    () => [...pacientes].sort((a, b) => b.criado_em.localeCompare(a.criado_em)).slice(0, 5),
    [pacientes],
  );

  const primeiroNome = usuario?.nome.split(" ")[0];

  return (
    <div className="flex flex-col gap-7">
      <h1 className="text-2xl font-bold tracking-tight text-foreground">Olá, {primeiroNome}</h1>

      {carregando ? (
        <>
          <CardsSkeleton />
          <ListSkeleton linhas={5} />
        </>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
            <Card className="gap-1 p-4">
              <span className="text-3xl font-bold tracking-tight text-foreground">
                {pacientes.length}
              </span>
              <span className="text-[13px] text-muted-foreground">Pacientes no total</span>
            </Card>
            {(Object.keys(LABEL_STATUS_PACIENTE) as StatusPaciente[]).map((status) => (
              <Card className="gap-1 p-4" key={status}>
                <span
                  className="text-3xl font-bold tracking-tight"
                  style={{ color: COR_STATUS_PACIENTE[status] }}
                >
                  {contagemPorStatus[status]}
                </span>
                <span className="text-[13px] text-muted-foreground">
                  {LABEL_STATUS_PACIENTE[status]}
                </span>
              </Card>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-foreground">Últimos pacientes cadastrados</h2>
            <div className="flex gap-2">
              <Button asChild variant="outline">
                <Link to="/pacientes">Ver todos</Link>
              </Button>
              <Button asChild>
                <Link to="/pacientes/novo">+ Novo paciente</Link>
              </Button>
            </div>
          </div>

          <Card className="p-2">
            {ultimosPacientes.length === 0 ? (
              <EstadoVazio icone="🗂️" texto="Nenhum paciente cadastrado ainda." />
            ) : (
              <ul className="flex flex-col">
                {ultimosPacientes.map((p) => (
                  <li
                    key={p.id}
                    className="flex items-center justify-between border-b border-border px-3 py-3 last:border-none"
                  >
                    <Link
                      to={`/pacientes/${p.id}`}
                      className="text-sm font-medium text-foreground hover:text-primary"
                    >
                      {p.nome_completo}
                    </Link>
                    <StatusBadge
                      texto={LABEL_STATUS_PACIENTE[p.status]}
                      cor={COR_STATUS_PACIENTE[p.status]}
                    />
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
