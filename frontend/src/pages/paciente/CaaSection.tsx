import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { caaApi } from "../../api/endpoints";
import { ApiError } from "../../api/client";
import type { CaaDadosInput } from "../../types/api";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";

const VAZIO: CaaDadosInput = {
  usa_caa: false,
  protocolo_aip_aplicado: false,
  sistema_ajustado: false,
  observacoes: "",
};

export function CaaSection({ pacienteId }: { pacienteId: string }) {
  const [form, setForm] = useState<CaaDadosInput>(VAZIO);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    caaApi
      .buscar(pacienteId)
      .then((dados) =>
        setForm({
          usa_caa: dados.usa_caa,
          protocolo_aip_aplicado: dados.protocolo_aip_aplicado,
          sistema_ajustado: dados.sistema_ajustado,
          observacoes: dados.observacoes ?? "",
        }),
      )
      .catch(() => {
        // ainda nao existe registro de CAA para este paciente - fica no formulario vazio
      })
      .finally(() => setCarregando(false));
  }, [pacienteId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSalvando(true);
    try {
      await caaApi.atualizar(pacienteId, { ...form, observacoes: form.observacoes || null });
      toast.success("Dados de CAA salvos");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível salvar");
    } finally {
      setSalvando(false);
    }
  }

  if (carregando) return <Skeleton className="h-48 w-full rounded-xl" />;

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-base font-semibold text-foreground">
        Comunicação Aumentativa e Alternativa (CAA)
      </h2>
      <form onSubmit={handleSubmit} className="flex max-w-lg flex-col gap-3.5">
        <label className="flex items-center gap-2 text-sm font-medium text-foreground">
          <Checkbox
            checked={form.usa_caa}
            onCheckedChange={(c) => setForm({ ...form, usa_caa: c === true })}
          />
          Usa CAA
        </label>
        <label className="flex items-center gap-2 text-sm font-medium text-foreground">
          <Checkbox
            checked={form.protocolo_aip_aplicado}
            onCheckedChange={(c) => setForm({ ...form, protocolo_aip_aplicado: c === true })}
          />
          Protocolo AIP aplicado
        </label>
        <label className="flex items-center gap-2 text-sm font-medium text-foreground">
          <Checkbox
            checked={form.sistema_ajustado}
            onCheckedChange={(c) => setForm({ ...form, sistema_ajustado: c === true })}
          />
          Sistema ajustado
        </label>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="observacoes">Observações</Label>
          <Textarea
            id="observacoes"
            value={form.observacoes ?? ""}
            onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
          />
        </div>
        <Button type="submit" disabled={salvando} className="self-start">
          {salvando ? "Salvando..." : "Salvar"}
        </Button>
      </form>
    </Card>
  );
}
