import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { pacientesApi } from "../api/endpoints";
import { useAuth } from "../auth/AuthContext";
import { temAcessoClinico } from "../auth/permissions";
import { LABEL_STATUS_PACIENTE } from "../constants/status";
import { DetalheSkeleton } from "../components/PageSkeleton";
import type { Paciente, StatusPaciente } from "../types/api";
import { ProfissionaisSection } from "./paciente/ProfissionaisSection";
import { ProtocolosSection } from "./paciente/ProtocolosSection";
import { CaaSection } from "./paciente/CaaSection";
import { EvolucoesSection } from "./paciente/EvolucoesSection";
import { TarefasSection } from "./paciente/TarefasSection";
import { TermosSection } from "./paciente/TermosSection";
import { AnexosSection } from "./paciente/AnexosSection";
import { FotoPerfil } from "./paciente/FotoPerfil";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export function PacienteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [paciente, setPaciente] = useState<Paciente | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!id) return;
    pacientesApi
      .buscar(id)
      .then(setPaciente)
      .finally(() => setCarregando(false));
  }, [id]);

  async function handleMudarStatus(novoStatus: StatusPaciente) {
    if (!id) return;
    const atualizado = await pacientesApi.atualizarStatus(id, novoStatus);
    setPaciente(atualizado);
    toast.success("Status atualizado");
  }

  async function handleExcluir() {
    if (!id) return;
    await pacientesApi.deletar(id);
    toast.success("Paciente excluído");
    navigate("/pacientes", { replace: true });
  }

  if (carregando) return <DetalheSkeleton />;
  if (!paciente || !id) return <p className="text-muted-foreground">Paciente não encontrado.</p>;

  const acessoClinico = temAcessoClinico(usuario?.papel);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FotoPerfil pacienteId={id} nomeCompleto={paciente.nome_completo} />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{paciente.nome_completo}</h1>
        </div>
        <div className="flex items-center gap-2">
          <Select value={paciente.status} onValueChange={(v) => handleMudarStatus(v as StatusPaciente)}>
            <SelectTrigger className="w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {(Object.keys(LABEL_STATUS_PACIENTE) as StatusPaciente[]).map((status) => (
                <SelectItem key={status} value={status}>
                  {LABEL_STATUS_PACIENTE[status]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {acessoClinico && (
            <Button asChild variant="outline">
              <Link to={`/pacientes/${id}/editar`}>Editar</Link>
            </Button>
          )}
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive">Excluir</Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Excluir este paciente?</AlertDialogTitle>
                <AlertDialogDescription>
                  O registro sai das listagens, mas o histórico é mantido no banco (soft delete) e
                  pode ser restaurado por um administrador.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction onClick={handleExcluir}>Excluir</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Tabs defaultValue="visao-geral">
        <TabsList>
          <TabsTrigger value="visao-geral">Visão geral</TabsTrigger>
          {acessoClinico && <TabsTrigger value="planejamento">Planejamento</TabsTrigger>}
          <TabsTrigger value="protocolos">Protocolos</TabsTrigger>
          {acessoClinico && <TabsTrigger value="clinico">Clínico</TabsTrigger>}
          <TabsTrigger value="anexos">Anexos</TabsTrigger>
        </TabsList>

        <TabsContent value="visao-geral">
          <Card className="p-6">
            <h2 className="mb-4 text-base font-semibold text-foreground">Dados cadastrais</h2>
            <dl className="grid grid-cols-[max-content_1fr] gap-x-5 gap-y-2.5 text-sm">
              <dt className="font-medium text-muted-foreground">Data de nascimento</dt>
              <dd>{paciente.data_nascimento} ({paciente.idade} anos)</dd>
              <dt className="font-medium text-muted-foreground">Nome da mãe</dt>
              <dd>{paciente.nome_mae}</dd>
              <dt className="font-medium text-muted-foreground">Nome do pai</dt>
              <dd>{paciente.nome_pai}</dd>
              <dt className="font-medium text-muted-foreground">Tem irmãos</dt>
              <dd>{paciente.tem_irmaos ? paciente.nome_irmaos || "Sim" : "Não"}</dd>
              <dt className="font-medium text-muted-foreground">Observações</dt>
              <dd>{paciente.observacoes || "-"}</dd>
              {acessoClinico && (
                <>
                  <dt className="font-medium text-muted-foreground">Queixa principal da família</dt>
                  <dd>{paciente.queixa_principal || "-"}</dd>
                  <dt className="font-medium text-muted-foreground">Diagnóstico</dt>
                  <dd>{paciente.diagnostico || "-"}</dd>
                  <dt className="font-medium text-muted-foreground">Faz uso de medicamento</dt>
                  <dd>{paciente.faz_uso_medicamento || "-"}</dd>
                  <dt className="font-medium text-muted-foreground">Início</dt>
                  <dd>{paciente.data_inicio || "-"}</dd>
                  <dt className="font-medium text-muted-foreground">Informações ao nascer</dt>
                  <dd>{paciente.informacoes_nascimento || "-"}</dd>
                </>
              )}
            </dl>
          </Card>

          <ProfissionaisSection pacienteId={id} />
        </TabsContent>

        {acessoClinico && (
          <TabsContent value="planejamento">
            <TarefasSection pacienteId={id} />
          </TabsContent>
        )}

        <TabsContent value="protocolos">
          <ProtocolosSection pacienteId={id} />
        </TabsContent>

        {acessoClinico && (
          <TabsContent value="clinico">
            <CaaSection pacienteId={id} />
            <EvolucoesSection pacienteId={id} />
            <TermosSection pacienteId={id} />
          </TabsContent>
        )}

        <TabsContent value="anexos">
          <AnexosSection pacienteId={id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
