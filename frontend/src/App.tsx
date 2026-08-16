import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PacientesListPage } from "./pages/PacientesListPage";
import { PacientesKanbanPage } from "./pages/PacientesKanbanPage";
import { PacienteFormPage } from "./pages/PacienteFormPage";
import { PacienteDetailPage } from "./pages/PacienteDetailPage";
import { ProtocolosPage } from "./pages/ProtocolosPage";
import { ModelosTermoPage } from "./pages/ModelosTermoPage";
import { Toaster } from "@/components/ui/sonner";

function ComLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route path="/" element={<ComLayout><DashboardPage /></ComLayout>} />

            <Route path="/pacientes" element={<ComLayout><PacientesListPage /></ComLayout>} />
            <Route path="/pacientes/kanban" element={<ComLayout><PacientesKanbanPage /></ComLayout>} />
            <Route path="/pacientes/novo" element={<ComLayout><PacienteFormPage /></ComLayout>} />
            <Route path="/pacientes/:id" element={<ComLayout><PacienteDetailPage /></ComLayout>} />
            <Route path="/pacientes/:id/editar" element={<ComLayout><PacienteFormPage /></ComLayout>} />

            <Route path="/protocolos" element={<ComLayout><ProtocolosPage /></ComLayout>} />
            <Route path="/modelos-termo" element={<ComLayout><ModelosTermoPage /></ComLayout>} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
      <Toaster position="top-right" richColors closeButton />
    </ThemeProvider>
  );
}
