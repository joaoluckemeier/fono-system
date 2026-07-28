export function EstadoVazio({ icone, texto }: { icone: string; texto: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center text-muted-foreground">
      <span className="text-3xl leading-none" aria-hidden="true">
        {icone}
      </span>
      <p className="text-sm">{texto}</p>
    </div>
  );
}
