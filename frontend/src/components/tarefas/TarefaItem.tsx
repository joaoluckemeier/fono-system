import type { ReactNode } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { CLASSE_BADGE_PRIORIDADE, LABEL_PRIORIDADE_TAREFA } from "../../constants/status";
import type { Tarefa } from "../../types/api";

interface Props {
  tarefa: Tarefa;
  onToggleConcluido: (concluido: boolean) => void;
  acoes?: ReactNode;
}

export function TarefaItem({ tarefa, onToggleConcluido, acoes }: Props) {
  return (
    <li className="group flex items-start gap-3 border-b border-border py-2.5 text-sm last:border-none">
      <Checkbox
        checked={tarefa.concluido}
        onCheckedChange={(checked) => onToggleConcluido(checked === true)}
        className="mt-0.5"
        aria-label={tarefa.concluido ? "Marcar como não concluída" : "Marcar como concluída"}
      />
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "font-medium text-foreground",
              tarefa.concluido && "text-muted-foreground line-through",
            )}
          >
            {tarefa.titulo}
          </span>
          <Badge variant="outline" className={CLASSE_BADGE_PRIORIDADE[tarefa.prioridade]}>
            {LABEL_PRIORIDADE_TAREFA[tarefa.prioridade]}
          </Badge>
          <span className="text-xs text-muted-foreground">{tarefa.data}</span>
        </div>
        {tarefa.descricao && <span className="text-xs text-muted-foreground">{tarefa.descricao}</span>}
      </div>
      {acoes && <div className="flex shrink-0 items-center gap-3">{acoes}</div>}
    </li>
  );
}
