import { createContext, useContext, useEffect, useState } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

const ROL_ORDEN = [
  'superadmin', 'admin', 'gestor_global', 'jefe_comision',
  'miembro_comision', 'jefe_area', 'jefe_departamento', 'usuario',
];

export function nivelRol(rol) {
  const i = ROL_ORDEN.indexOf(rol);
  return i === -1 ? ROL_ORDEN.length : i;
}

export function tienePrivilegio(usuario, rolMinimo) {
  if (!usuario) return false;
  return nivelRol(usuario.rol) <= nivelRol(rolMinimo);
}

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => {
    const raw = localStorage.getItem('usuario');
    return raw ? JSON.parse(raw) : null;
  });
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) {
      setCargando(false);
      return;
    }
    api.get('/auth/me/')
      .then((res) => {
        setUsuario(res.data);
        localStorage.setItem('usuario', JSON.stringify(res.data));
      })
      .catch(() => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('usuario');
        setUsuario(null);
      })
      .finally(() => setCargando(false));
  }, []);

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password });
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    localStorage.setItem('usuario', JSON.stringify(data.usuario));
    setUsuario(data.usuario);
    return data.usuario;
  }

  function logout() {
    api.post('/auth/logout/').catch(() => {});
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('usuario');
    setUsuario(null);
  }

  function actualizarUsuario(nuevo) {
    setUsuario(nuevo);
    localStorage.setItem('usuario', JSON.stringify(nuevo));
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout, actualizarUsuario, tienePrivilegio: (r) => tienePrivilegio(usuario, r) }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
