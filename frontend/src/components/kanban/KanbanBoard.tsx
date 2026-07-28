import type { ReactNode } from "react";
import { DndContext, type DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { KanbanColumn } from "./KanbanColumn";
import { KanbanCard } from "./KanbanCard";

export interface KanbanColunaConfig {
  id: string;
  titulo: string;
  cor: string;
}

interface KanbanBoardProps<T extends { id: string }> {
  colunas: KanbanColunaConfig[];
  itens: T[];
  status: (item: T) => string;
  onMover: (item: T, novoStatus: string) => void;
  renderCard: (item: T) => ReactNode;
  vazio?: ReactNode;
}

export function KanbanBoard<T extends { id: string }>({
  colunas,
  itens,
  status,
  onMover,
  renderCard,
  vazio,
}: KanbanBoardProps<T>) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }));

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over) return;
    const item = itens.find((i) => i.id === active.id);
    if (!item) return;
    const novoStatus = String(over.id);
    if (status(item) !== novoStatus) {
      onMover(item, novoStatus);
    }
  }

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {colunas.map((coluna) => {
          const itensDaColuna = itens.filter((item) => status(item) === coluna.id);
          return (
            <KanbanColumn
              key={coluna.id}
              id={coluna.id}
              titulo={coluna.titulo}
              cor={coluna.cor}
              quantidade={itensDaColuna.length}
            >
              {itensDaColuna.length === 0 && vazio}
              {itensDaColuna.map((item) => (
                <KanbanCard key={item.id} id={item.id}>
                  {renderCard(item)}
                </KanbanCard>
              ))}
            </KanbanColumn>
          );
        })}
      </div>
    </DndContext>
  );
}
