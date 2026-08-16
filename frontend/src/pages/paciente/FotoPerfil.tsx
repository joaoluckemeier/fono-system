import { useEffect, useState } from "react";
import { anexosApi } from "../../api/endpoints";

function iniciais(nomeCompleto: string): string {
  const partes = nomeCompleto.trim().split(/\s+/);
  const primeira = partes[0]?.[0] ?? "";
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (primeira + ultima).toUpperCase();
}

export function FotoPerfil({
  pacienteId,
  nomeCompleto,
}: {
  pacienteId: string;
  nomeCompleto: string;
}) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    let ativo = true;
    anexosApi
      .listar("paciente", pacienteId)
      .then((anexos) => {
        const fotos = anexos
          .filter((a) => a.tipo_arquivo === "foto")
          .sort((a, b) => (a.criado_em < b.criado_em ? 1 : -1));
        const maisRecente = fotos[0];
        if (!maisRecente) return;
        return anexosApi.obterUrl(maisRecente.id).then((res) => {
          if (ativo) setUrl(res.url);
        });
      })
      .catch(() => setUrl(null));
    return () => {
      ativo = false;
    };
  }, [pacienteId]);

  if (url) {
    return (
      <img
        src={url}
        alt={`Foto de ${nomeCompleto}`}
        className="h-12 w-12 rounded-full object-cover"
      />
    );
  }

  return (
    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground">
      {iniciais(nomeCompleto)}
    </div>
  );
}
