import { Badge } from "@/components/ui/badge";

export function StatusBadge({ texto, cor }: { texto: string; cor: string }) {
  return (
    <Badge
      variant="outline"
      className="border-transparent font-semibold"
      style={{ color: cor, background: `color-mix(in oklch, ${cor} 14%, transparent)` }}
    >
      {texto}
    </Badge>
  );
}
