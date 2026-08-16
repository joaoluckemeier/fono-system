import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { pacientesApi } from "../api/endpoints";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { temAcessoClinico } from "../auth/permissions";
import { DetalheSkeleton } from "../components/PageSkeleton";
import type { PacienteInput } from "../types/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Card } from "@/components/ui/card";

const VAZIO: PacienteInput = {
  nome_completo: "",
  data_nascimento: "",
  nome_mae: "",
  nome_pai: "",
  tem_irmaos: false,
  nome_irmaos: "",
  faz_uso_medicamento: "",
  diagnostico: "",
  data_inicio: "",
  queixa_principal: "",
  informacoes_nascimento: "",
  observacoes: "",
};

export function PacienteFormPage() {
  const { id } = useParams<{ id: string }>();
  const editando = Boolean(id);
  const navigate = useNavigate();
  const { usuario } = useAuth();

  const [form, setForm] = useState<PacienteInput>(VAZIO);
  const [carregando, setCarregando] = useState(editando);
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!id) return;
    pacientesApi
      .buscar(id)
      .then((paciente) =>
        setForm({
          nome_completo: paciente.nome_completo,
          data_nascimento: paciente.data_nascimento,
          nome_mae: paciente.nome_mae,
          nome_pai: paciente.nome_pai,
          tem_irmaos: paciente.tem_irmaos,
          nome_irmaos: paciente.nome_irmaos ?? "",
          faz_uso_medicamento: paciente.faz_uso_medicamento ?? "",
          diagnostico: paciente.diagnostico ?? "",
          data_inicio: paciente.data_inicio ?? "",
          queixa_principal: paciente.queixa_principal ?? "",
          informacoes_nascimento: paciente.informacoes_nascimento ?? "",
          observacoes: paciente.observacoes ?? "",
        }),
      )
      .catch(() => toast.error("Não foi possível carregar o paciente"))
      .finally(() => setCarregando(false));
  }, [id]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSalvando(true);
    try {
      const payload: PacienteInput = {
        ...form,
        nome_irmaos: form.nome_irmaos || null,
        diagnostico: form.diagnostico || null,
        data_inicio: form.data_inicio || null,
        queixa_principal: form.queixa_principal || null,
        informacoes_nascimento: form.informacoes_nascimento || null,
        observacoes: form.observacoes || null,
      };
      const salvo = id
        ? await pacientesApi.atualizar(id, payload)
        : await pacientesApi.criar(payload);
      toast.success(editando ? "Paciente atualizado" : "Paciente cadastrado");
      navigate(`/pacientes/${salvo.id}`, { replace: true });
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível salvar");
    } finally {
      setSalvando(false);
    }
  }

  if (editando && !temAcessoClinico(usuario?.papel)) {
    // secretaria nao ve campos clinicos (ex: faz_uso_medicamento) - editar clonaria o
    // formulario com esses campos vazios e apagaria o dado existente no backend.
    return <Navigate to={`/pacientes/${id}`} replace />;
  }

  if (carregando) return <DetalheSkeleton />;

  return (
    <div className="flex flex-col gap-5">
      <h1 className="text-2xl font-bold tracking-tight text-foreground">
        {editando ? "Editar paciente" : "Novo paciente"}
      </h1>
      <Card className="max-w-lg p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="nome_completo">Nome completo</Label>
            <Input
              id="nome_completo"
              required
              value={form.nome_completo}
              onChange={(e) => setForm({ ...form, nome_completo: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="data_nascimento">Data de nascimento</Label>
            <Input
              id="data_nascimento"
              type="date"
              required
              value={form.data_nascimento}
              onChange={(e) => setForm({ ...form, data_nascimento: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="nome_mae">Nome da mãe</Label>
            <Input
              id="nome_mae"
              required
              value={form.nome_mae}
              onChange={(e) => setForm({ ...form, nome_mae: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="nome_pai">Nome do pai</Label>
            <Input
              id="nome_pai"
              required
              value={form.nome_pai}
              onChange={(e) => setForm({ ...form, nome_pai: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            <Checkbox
              checked={form.tem_irmaos}
              onCheckedChange={(checked) => setForm({ ...form, tem_irmaos: checked === true })}
            />
            Tem irmãos
          </label>
          {form.tem_irmaos && (
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="nome_irmaos">Nome dos irmãos</Label>
              <Input
                id="nome_irmaos"
                value={form.nome_irmaos ?? ""}
                onChange={(e) => setForm({ ...form, nome_irmaos: e.target.value })}
              />
            </div>
          )}
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="faz_uso_medicamento">Faz uso de medicamento</Label>
            <Input
              id="faz_uso_medicamento"
              required
              value={form.faz_uso_medicamento}
              onChange={(e) => setForm({ ...form, faz_uso_medicamento: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="queixa_principal">Queixa principal da família</Label>
            <Textarea
              id="queixa_principal"
              value={form.queixa_principal ?? ""}
              onChange={(e) => setForm({ ...form, queixa_principal: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="diagnostico">Diagnóstico</Label>
            <Textarea
              id="diagnostico"
              value={form.diagnostico ?? ""}
              onChange={(e) => setForm({ ...form, diagnostico: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="data_inicio">Data de início</Label>
            <Input
              id="data_inicio"
              type="date"
              value={form.data_inicio ?? ""}
              onChange={(e) => setForm({ ...form, data_inicio: e.target.value })}
            />
          </div>

          <Button type="submit" disabled={salvando} className="mt-2 h-10">
            {salvando ? "Salvando..." : "Salvar"}
          </Button>
        </form>
      </Card>

      <Card className="max-w-lg p-6">
        <h2 className="mb-4 text-base font-semibold text-foreground">Informações ao nascer</h2>
        <Textarea
          aria-label="Informações ao nascer"
          value={form.informacoes_nascimento ?? ""}
          onChange={(e) =>
            setForm({ ...form, informacoes_nascimento: e.target.value })
          }
        />
      </Card>

      <Card className="max-w-lg p-6">
        <h2 className="mb-4 text-base font-semibold text-foreground">Observações</h2>
        <Textarea
          aria-label="Observações"
          value={form.observacoes ?? ""}
          onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
        />
      </Card>
    </div>
  );
}
