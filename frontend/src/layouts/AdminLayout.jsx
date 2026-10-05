import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const MENU = [
  { grupo: 'Principal', items: [
    { to: '/app/dashboard', icon: '📊', label: 'Dashboard', rol: 'usuario' },
    { to: '/app/propuestas', icon: '📝', label: 'Propuestas', rol: 'usuario' },
    { to: '/app/comisiones', icon: '🏛️', label: 'Comisiones', rol: 'miembro_comision' },
    { to: '/app/notificaciones', icon: '🔔', label: 'Notificaciones', rol: 'usuario' },
  ]},
  { grupo: 'Administración', items: [
    { to: '/app/usuarios', icon: '👥', label: 'Usuarios y Roles', rol: 'admin' },
    { to: '/app/areas', icon: '🏢', label: 'Áreas y Deptos.', rol: 'admin' },
    { to: '/app/premios', icon: '🏆', label: 'Categorías y Premios', rol: 'admin' },
    { to: '/app/etapas', icon: '📅', label: 'Etapas del Proceso', rol: 'admin' },
    { to: '/app/nomencladores', icon: '📋', label: 'Nomencladores', rol: 'admin' },
  ]},
  { grupo: 'Reportes', items: [
    { to: '/app/estadisticas', icon: '📈', label: 'Estadísticas', rol: 'gestor_global' },
    { to: '/app/aprobacion-final', icon: '✅', label: 'Aprobación Final', rol: 'gestor_global' },
    { to: '/app/ganadores', icon: '🎖️', label: 'Ganadores / Retroactivos', rol: 'gestor_global' },
    { to: '/app/auditoria', icon: '🔎', label: 'Logs de Auditoría', rol: 'admin' },
  ]},
  { grupo: 'Cuenta', items: [
    { to: '/app/perfil', icon: '👤', label: 'Mi Perfil', rol: 'usuario' },
  ]},
];

export default function AdminLayout() {
  const { usuario, logout, tienePrivilegio } = useAuth();
  const navigate = useNavigate();
  // Estado exclusivo para alternar Drawer (móvil/tablet) vs Sidebar fijo (desktop).
  // No decide layout por tamaño de pantalla: eso lo resuelven las media queries en index.css;
  // esto solo controla si el drawer está abierto o cerrado.
  const [menuAbierto, setMenuAbierto] = useState(false);

  function irA(ruta) {
    setMenuAbierto(false);
    navigate(ruta);
  }

  return (
    <div className="al">
      <div className="mobile-topbar">
        <button className="hamburger" onClick={() => setMenuAbierto(true)} aria-label="Abrir menú">☰</button>
        <div className="sbn">PREMIAX·UHO</div>
      </div>
      <div className={`sb-overlay${menuAbierto ? ' open' : ''}`} onClick={() => setMenuAbierto(false)} />
      <aside className={`sb${menuAbierto ? ' open' : ''}`}>
        <div className="sb-br">
          <div className="sbn">PREMIAX·UHO</div>
          <div className="sbr">{usuario?.rol_display} · {usuario?.nombre_completo}</div>
        </div>
        {MENU.map((grupo) => {
          const visibles = grupo.items.filter((i) => tienePrivilegio(i.rol));
          if (!visibles.length) return null;
          return (
            <div key={grupo.grupo}>
              <div className="sbs">{grupo.grupo}</div>
              {visibles.map((item) => (
                <NavLink key={item.to} to={item.to} className={({ isActive }) => `sbi${isActive ? ' on' : ''}`} onClick={() => setMenuAbierto(false)}>
                  <span className="ic">{item.icon}</span>{item.label}
                </NavLink>
              ))}
            </div>
          );
        })}
        <div className="sbs">Otros</div>
        <div className="sbi" onClick={() => irA('/')}> <span className="ic">🌐</span>Ver Landing Page</div>
        <div className="sbi" onClick={() => { setMenuAbierto(false); logout(); navigate('/login'); }}><span className="ic">🚪</span>Cerrar Sesión</div>
      </aside>
      <main className="mc">
        <Outlet />
      </main>
    </div>
  );
}
