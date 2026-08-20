import type { ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import type { Papel } from "../types/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const PAPEL_LABEL: Record<string, string> = {
  admin: "Administrador(a)",
  fono: "Fonoaudiólogo(a)",
  secretaria: "Secretaria",
};

function iniciais(nome: string | undefined): string {
  if (!nome) return "?";
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

function IconeDashboard() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </svg>
  );
}

function IconePacientes() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
      <circle cx="17.5" cy="8.5" r="2.3" />
      <path d="M15.8 14.2c2.5.3 4.5 2.6 4.5 5.3" />
    </svg>
  );
}

function IconePlanejamento() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="17" rx="2" />
      <path d="M8 2v4M16 2v4M3 10h18" />
      <path d="m8.5 15 2 2 4.5-4.5" />
    </svg>
  );
}

function IconeProtocolos() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 3h6a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
      <path d="M8 11h8M8 15h5" />
    </svg>
  );
}

function IconeTermos() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
      <path d="M14 3v4h4" />
      <path d="M8 13h8M8 17h5" />
    </svg>
  );
}

const navItems = [
  { to: "/", label: "Dashboard", icon: IconeDashboard, end: true, papeis: null },
  { to: "/pacientes", label: "Pacientes", icon: IconePacientes, end: false, papeis: null },
  {
    to: "/planejamento",
    label: "Planejamento",
    icon: IconePlanejamento,
    end: false,
    papeis: ["admin", "fono"] as Papel[],
  },
  { to: "/protocolos", label: "Protocolos", icon: IconeProtocolos, end: false, papeis: null },
  {
    to: "/modelos-termo",
    label: "Termos",
    icon: IconeTermos,
    end: false,
    papeis: ["admin", "fono"] as Papel[],
  },
];

export function Layout({ children }: { children: ReactNode }) {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="flex w-60 shrink-0 flex-col gap-2 bg-sidebar p-4 text-sidebar-foreground">
        <div className="flex items-center gap-2.5 px-2 pb-5">
          <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-base font-bold text-primary-foreground">
            +
          </span>
          <span className="text-[15px] font-bold tracking-tight text-white">Fono System</span>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5">
          {navItems
            .filter((item) => !item.papeis || (usuario && item.papeis.includes(usuario.papel)))
            .map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground/75 transition-colors hover:bg-white/5 hover:text-white",
                  isActive && "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground",
                )
              }
            >
              <Icon />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-2 flex items-center gap-2.5 border-t border-white/10 px-2 py-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-sidebar-accent text-xs font-bold text-sidebar-primary">
            {iniciais(usuario?.nome)}
          </div>
          <div className="flex min-w-0 flex-col leading-tight">
            <strong className="truncate text-[13px] text-white">{usuario?.nome}</strong>
            <small className="text-xs text-sidebar-foreground/60">
              {usuario ? (PAPEL_LABEL[usuario.papel] ?? usuario.papel) : ""}
            </small>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="mx-2 border-white/15 bg-transparent text-sidebar-foreground/80 hover:bg-white/10 hover:text-white"
          onClick={handleLogout}
        >
          Sair
        </Button>
      </aside>

      <main className="mx-auto w-full max-w-5xl flex-1 px-10 py-8">{children}</main>
    </div>
  );
}
