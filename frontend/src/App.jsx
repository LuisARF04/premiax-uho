import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './layouts/AdminLayout';

import Landing from './pages/Landing';
import Login from './pages/Login';
import CompletarPerfil from './pages/CompletarPerfil';
import Dashboard from './pages/Dashboard';
import Usuarios from './pages/Usuarios';
import Areas from './pages/Areas';
import Premios from './pages/Premios';
import Etapas from './pages/Etapas';
import Reglamento from './pages/Reglamento';
import Nomencladores from './pages/Nomencladores';
import Comisiones from './pages/Comisiones';
import PanelComision from './pages/PanelComision';
import ProponerGanadores from './pages/ProponerGanadores';
import Propuestas from './pages/Propuestas';
import NuevaPropuesta from './pages/NuevaPropuesta';
import DetallePropuesta from './pages/DetallePropuesta';
import AprobacionFinal from './pages/AprobacionFinal';
import Ganadores from './pages/Ganadores';
import Estadisticas from './pages/Estadisticas';
import Notificaciones from './pages/Notificaciones';
import Perfil from './pages/Perfil';
import Auditoria from './pages/Auditoria';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/completar-perfil" element={<ProtectedRoute><CompletarPerfil /></ProtectedRoute>} />

          <Route path="/app" element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="propuestas" element={<Propuestas />} />
            <Route path="propuestas/nueva" element={<NuevaPropuesta />} />
            <Route path="propuestas/:id" element={<DetallePropuesta />} />
            <Route path="comisiones" element={<Comisiones />} />
            <Route path="comisiones/:id/panel" element={<PanelComision />} />
            <Route path="comisiones/:id/proponer-ganadores/:premioId" element={<ProponerGanadores />} />
            <Route path="notificaciones" element={<Notificaciones />} />
            <Route path="perfil" element={<Perfil />} />

            <Route path="usuarios" element={<ProtectedRoute rolMinimo="admin"><Usuarios /></ProtectedRoute>} />
            <Route path="areas" element={<ProtectedRoute rolMinimo="admin"><Areas /></ProtectedRoute>} />
            <Route path="premios" element={<ProtectedRoute rolMinimo="admin"><Premios /></ProtectedRoute>} />
            <Route path="etapas" element={<ProtectedRoute rolMinimo="admin"><Etapas /></ProtectedRoute>} />
            <Route path="reglamento" element={<ProtectedRoute rolMinimo="admin"><Reglamento /></ProtectedRoute>} />
            <Route path="nomencladores" element={<ProtectedRoute rolMinimo="admin"><Nomencladores /></ProtectedRoute>} />

            <Route path="estadisticas" element={<ProtectedRoute rolMinimo="jefe_comision"><Estadisticas /></ProtectedRoute>} />
            <Route path="aprobacion-final" element={<ProtectedRoute rolMinimo="gestor_global"><AprobacionFinal /></ProtectedRoute>} />
            <Route path="ganadores" element={<ProtectedRoute rolMinimo="gestor_global"><Ganadores /></ProtectedRoute>} />
            <Route path="auditoria" element={<ProtectedRoute rolMinimo="admin"><Auditoria /></ProtectedRoute>} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
