import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface Props {
  aberto: boolean;
  onFechar: () => void;
  url: string | null;
  titulo: string;
  nomeArquivo: string;
}

export function DocumentoPreviewDialog({ aberto, onFechar, url, titulo, nomeArquivo }: Props) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  function handleImprimir() {
    iframeRef.current?.contentWindow?.print();
  }

  return (
    <Dialog open={aberto} onOpenChange={(open) => !open && onFechar()}>
      <DialogContent className="flex h-[85vh] w-full max-w-3xl flex-col sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle>{titulo}</DialogTitle>
        </DialogHeader>
        <div className="min-h-0 flex-1 overflow-hidden rounded-lg border border-border bg-muted">
          {url && (
            <iframe ref={iframeRef} src={url} title={titulo} className="h-full w-full" />
          )}
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onFechar}>
            Fechar
          </Button>
          <Button type="button" variant="outline" onClick={handleImprimir} disabled={!url}>
            Imprimir
          </Button>
          {url ? (
            <Button type="button" asChild>
              <a href={url} download={nomeArquivo}>
                Baixar
              </a>
            </Button>
          ) : (
            <Button type="button" disabled>
              Baixar
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
