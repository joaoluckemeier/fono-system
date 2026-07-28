import type { ReactNode } from "react";
import { useDroppable } from "@dnd-kit/core";
import { cn } from "@/lib/utils";

interface KanbanColumnProps {
  id: string;
  titulo: string;
  cor: string;
  quantidade: number;
  children: ReactNode;
}

export function KanbanColumn({ id, titulo, cor, quantidade, children }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-muted/40 p-3 transition-colors",
        isOver && "border-primary/40 bg-accent",
      )}
    >
      <div className="flex items-center gap-2 px-1 pb-3">
        <span className="size-2 rounded-full" style={{ background: cor }} aria-hidden="true" />
        <h3 className="flex-1 text-[13px] font-semibold text-foreground">{titulo}</h3>
        <span className="rounded-full border border-border bg-card px-2 text-xs font-semibold text-muted-foreground">
          {quantidade}
        </span>
      </div>
      <div ref={setNodeRef} className="flex min-h-16 flex-col gap-2">
        {children}
      </div>
    </div>
  );
}
