import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import { modelosTermoApi, pacientesApi, termosApi } from "../api/endpoints";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { LABEL_TIPO_MODELO_TERMO, type ModeloTermo, type Paciente, type TipoModeloTermo } from "../types/api";
import { EstadoVazio } from "../components/EstadoVazio";
import { ListSkeleton } from "../components/PageSkeleton";
import { BotaoRemoverComConfirmacao } from "../components/BotaoRemoverComConfirmacao";
import { DocumentoPreviewDialog } from "../components/DocumentoPreviewDialog";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

const TIPOS: TipoModeloTermo[] = ["termo", "encaminhamento"];

export function ModelosTermoPage() {
  const { usuario } = useAuth();
  const ehAdmin = usuario?.papel === "admin";
  const [aba, setAba] = useState<"modelos" | "gerar">(ehAdmin ? "modelos" : "gerar");

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Termos e encaminhamentos
        </h1>
        {ehAdmin && (
          <div className="flex gap-1 rounded-lg bg-muted p-1">
            <button
              type="button"
              onClick={() => setAba("modelos")}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                aba === "modelos" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground",
              )}
            >
              Modelos
            </button>
            <button
              type="button"
              onClick={() => setAba("gerar")}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                aba === "gerar" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground",
              )}
            >
              Gerar documento
            </button>
          </div>
        )}
      </div>

      {aba === "modelos" && ehAdmin ? <AbaModelos /> : <AbaGerarDocumento />}
    </div>
  );
}

function AbaGerarDocumento() {
  const [modelos, setModelos] = useState<ModeloTermo[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [buscaPaciente, setBuscaPaciente] = useState("");
  const [pacienteSelecionado, setPacienteSelecionado] = useState<Paciente | null>(null);
  const [modeloId, setModeloId] = useState("");
  const [gerando, setGerando] = useState(false);
  const [preview, setPreview] = useState<{ url: string; titulo: string; nomeArquivo: string } | null>(
    null,
  );

  useEffect(() => {
    modelosTermoApi.listar(true).then((lista) => {
      setModelos(lista);
      if (lista.length > 0) setModeloId(lista[0].id);
    });
    pacientesApi.listar().then(setPacientes);
  }, []);

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

  function fecharPreview() {
    if (preview) URL.revokeObjectURL(preview.url);
    setPreview(null);
  }

  async function handleGerar(e: FormEvent) {
    e.preventDefault();
    if (!pacienteSelecionado || !modeloId) return;
    setGerando(true);
    try {
      const blob = await termosApi.gerar(pacienteSelecionado.id, modeloId);
      const modelo = modelos.find((m) => m.id === modeloId);
      setPreview({
        url: URL.createObjectURL(blob),
        titulo: modelo?.nome ?? "Documento gerado",
        nomeArquivo: `${modelo?.nome ?? "termo"}.pdf`,
      });
      toast.success(`Documento gerado e anexado a ${pacienteSelecionado.nome_completo}`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível gerar o documento");
    } finally {
      setGerando(false);
    }
  }

  return (
    <Card className="max-w-lg p-6">
      <h2 className="mb-1 text-base font-semibold text-foreground">Gerar documento pra um paciente</h2>
      <p className="mb-4 text-xs text-muted-foreground">
        O documento gerado é salvo automaticamente nos anexos do paciente escolhido.
      </p>
      <form onSubmit={handleGerar} className="flex flex-col gap-3.5">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="busca-paciente">Paciente</Label>
          <div className="relative">
            <Input
              id="busca-paciente"
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

        {modelos.length === 0 ? (
          <p className="text-xs text-muted-foreground">
            Nenhum modelo ativo no catálogo ainda.
          </p>
        ) : (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="modelo-gerar">Modelo</Label>
            <Select value={modeloId} onValueChange={setModeloId}>
              <SelectTrigger id="modelo-gerar">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {modelos.map((m) => (
                  <SelectItem key={m.id} value={m.id}>
                    {m.nome} ({LABEL_TIPO_MODELO_TERMO[m.tipo]})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <Button type="submit" className="self-start" disabled={!pacienteSelecionado || !modeloId || gerando}>
          {gerando ? "Gerando..." : "Gerar documento"}
        </Button>
      </form>

      <DocumentoPreviewDialog
        aberto={preview !== null}
        onFechar={fecharPreview}
        url={preview?.url ?? null}
        titulo={preview?.titulo ?? ""}
        nomeArquivo={preview?.nomeArquivo ?? "documento.pdf"}
      />
    </Card>
  );
}

function AbaModelos() {
  const [modelos, setModelos] = useState<ModeloTermo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [nome, setNome] = useState("");
  const [tipo, setTipo] = useState<TipoModeloTermo>("termo");
  const [corpoTexto, setCorpoTexto] = useState("");
  const [emEdicao, setEmEdicao] = useState<ModeloTermo | null>(null);

  function recarregar() {
    modelosTermoApi.listar().then(setModelos);
  }

  useEffect(() => {
    recarregar();
    setCarregando(false);
  }, []);

  async function handleCriar(e: FormEvent) {
    e.preventDefault();
    try {
      await modelosTermoApi.criar({ nome, tipo, corpo_texto: corpoTexto });
      setNome("");
      setTipo("termo");
      setCorpoTexto("");
      recarregar();
      toast.success("Modelo cadastrado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível criar o modelo");
    }
  }

  async function handleSalvarEdicao(e: FormEvent) {
    e.preventDefault();
    if (!emEdicao) return;
    try {
      await modelosTermoApi.atualizar(emEdicao.id, {
        nome: emEdicao.nome,
        tipo: emEdicao.tipo,
        corpo_texto: emEdicao.corpo_texto,
        ativo: emEdicao.ativo,
      });
      setEmEdicao(null);
      recarregar();
      toast.success("Modelo atualizado");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível atualizar o modelo");
    }
  }

  async function handleExcluir(id: string) {
    try {
      await modelosTermoApi.deletar(id);
      recarregar();
      toast.success("Modelo removido");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Não foi possível remover o modelo");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <Card className="p-6">
        {carregando ? (
          <ListSkeleton linhas={3} />
        ) : modelos.length === 0 ? (
          <EstadoVazio icone="📄" texto="Nenhum modelo cadastrado ainda." />
        ) : (
          <ul className="flex flex-col">
            {modelos.map((m) => (
              <li
                key={m.id}
                className="flex items-center justify-between gap-3 border-b border-border py-2.5 text-sm last:border-none"
              >
                <div className="flex items-center gap-2.5">
                  <strong className="font-medium text-foreground">{m.nome}</strong>
                  <Badge variant="outline">{LABEL_TIPO_MODELO_TERMO[m.tipo]}</Badge>
                  {!m.ativo && (
                    <Badge variant="outline" className="border-amber-300 bg-amber-50 text-amber-700">
                      Inativo
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    className="text-xs font-medium text-primary hover:underline"
                    onClick={() => setEmEdicao(m)}
                  >
                    editar
                  </button>
                  <BotaoRemoverComConfirmacao
                    titulo="Remover este modelo?"
                    descricao={`"${m.nome}" será removido (soft delete, mantido no banco para auditoria). Termos já gerados a partir dele não são afetados.`}
                    onConfirmar={() => handleExcluir(m.id)}
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="max-w-lg p-6">
        <h2 className="mb-4 text-base font-semibold text-foreground">Novo modelo</h2>
        <form onSubmit={handleCriar} className="flex flex-col gap-3.5">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="nome-modelo">Nome</Label>
            <Input
              id="nome-modelo"
              placeholder="ex: Termo de consentimento — avaliação inicial"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="tipo-modelo">Tipo</Label>
            <Select value={tipo} onValueChange={(v) => setTipo(v as TipoModeloTermo)}>
              <SelectTrigger id="tipo-modelo" className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIPOS.map((t) => (
                  <SelectItem key={t} value={t}>
                    {LABEL_TIPO_MODELO_TERMO[t]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="corpo-modelo">Corpo do texto</Label>
            <Textarea
              id="corpo-modelo"
              value={corpoTexto}
              onChange={(e) => setCorpoTexto(e.target.value)}
              required
              rows={8}
            />
          </div>
          <Button type="submit" className="self-start">
            Adicionar
          </Button>
        </form>
      </Card>

      <Dialog open={emEdicao !== null} onOpenChange={(open) => !open && setEmEdicao(null)}>
        <DialogContent className="sm:max-w-lg">
          {emEdicao && (
            <form onSubmit={handleSalvarEdicao} className="flex flex-col gap-4">
              <DialogHeader>
                <DialogTitle>Editar modelo</DialogTitle>
              </DialogHeader>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="nome-edicao">Nome</Label>
                <Input
                  id="nome-edicao"
                  value={emEdicao.nome}
                  onChange={(e) => setEmEdicao({ ...emEdicao, nome: e.target.value })}
                  required
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="tipo-edicao">Tipo</Label>
                <Select
                  value={emEdicao.tipo}
                  onValueChange={(v) => setEmEdicao({ ...emEdicao, tipo: v as TipoModeloTermo })}
                >
                  <SelectTrigger id="tipo-edicao" className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TIPOS.map((t) => (
                      <SelectItem key={t} value={t}>
                        {LABEL_TIPO_MODELO_TERMO[t]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="corpo-edicao">Corpo do texto</Label>
                <Textarea
                  id="corpo-edicao"
                  value={emEdicao.corpo_texto}
                  onChange={(e) => setEmEdicao({ ...emEdicao, corpo_texto: e.target.value })}
                  required
                  rows={8}
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-foreground">
                <input
                  type="checkbox"
                  checked={emEdicao.ativo}
                  onChange={(e) => setEmEdicao({ ...emEdicao, ativo: e.target.checked })}
                />
                Ativo (disponível para gerar termos/encaminhamentos)
              </label>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setEmEdicao(null)}>
                  Cancelar
                </Button>
                <Button type="submit">Salvar</Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
