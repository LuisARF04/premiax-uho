import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loading } from './ui';

export default function ProtectedRoute({ children, rolMinimo }) {
  const { usuario, cargando, tienePrivilegio } = useAuth();

  if (cargando) return <Loading />;
  if (!usuario) return <Navigate to="/login" replace />;
  if (!usuario.perfil_completo) return <Navigate to="/completar-perfil" replace />;
  if (rolMinimo && !tienePrivilegio(rolMinimo)) return <Navigate to="/app/dashboard" replace />;
  return children;
}
