import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading, Modal, Avatar } from '../components/ui';
import { useAuth } from '../context/AuthContext';

const ROLES = [
  ['superadmin', 'Superadmin'], ['admin', 'Admin'], ['gestor_global', 'Gestor Global'],
  ['jefe_comision', 'Jefe de Comisión'], ['miembro_comision', 'Miembro de Comisión'],
  ['jefe_area', 'Jefe de Área'], ['jefe_departamento', 'Jefe de Departamento'], ['usuario', 'Usuario'],
];

export default function Usuarios() {
  const { tienePrivilegio } = useAuth();
  const [usuarios, setUsuarios] = useState(null);
  const [busqueda, setBusqueda] = useState('');
  const [rolFiltro, setRolFiltro] = useState('');
  const [editando, setEditando] = useState(null);
  const [nuevoRol, setNuevoRol] = useState('');
  const [error, setError] = useState('');

  function cargar() {
    api.get('/usuarios/', { params: { search: busqueda || undefined, rol: rolFiltro || undefined, page_size: 100 } })
      .then((r) => setUsuarios(r.data.results || r.data));
  }

  useEffect(() => { cargar(); }, [busqueda, rolFiltro]);

  async function guardarRol() {
    setError('');
    try {
      await api.patch(`/usuarios/${editando.id}/cambiar_rol/`, { rol: nuevoRol });
      setEditando(null);
      cargar();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo cambiar el rol.');
    }
  }

  return (
    <div>
      <PageHeader
        title="Usuarios y Roles"
        subtitle={`${usuarios ? usuarios.length : '…'} usuarios registrados`}
        actions={<>
          <input className="fc" style={{ width: 210 }} placeholder="🔍 Buscar usuario..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          <select className="fc" style={{ width: 170 }} value={rolFiltro} onChange={(e) => setRolFiltro(e.target.value)}>
            <option value="">Todos los roles</option>
            {ROLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </>}
      />
      <div className="ca">
        {!usuarios ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Usuario</th><th>Correo</th><th>Área</th><th>Rol</th><th>Último Acceso</th><th>Acciones</th></tr></thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id}>
                    <td><div className="flex ic g8"><Avatar nombre={u.nombre_completo} /><div><div className="tb">{u.nombre_completo}</div><div className="tsm tm">{u.username}</div></div></div></td>
                    <td className="tsm">{u.email}</td>
                    <td className="tsm">{u.area_nombre || '—'}</td>
                    <td><span className="rc">{u.rol_display}</span></td>
                    <td className="tsm tm">{u.last_login ? new Date(u.last_login).toLocaleString() : 'Nunca'}</td>
                    <td>
                      {tienePrivilegio('admin') && (
                        <button className="bs" style={{ fontSize: '.73rem', padding: '4px 9px' }}
                          onClick={() => { setEditando(u); setNuevoRol(u.rol); }}>Editar Rol</button>
                      )}
                    </td>
                  </tr>
                ))}
                {!usuarios.length && <tr><td colSpan={6} className="tm">No se encontraron usuarios.</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {editando && (
        <Modal title={`Editar rol: ${editando.nombre_completo}`} onClose={() => setEditando(null)}>
          {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
          <div className="fg mb16">
            <label>Rol</label>
            <select className="fc" value={nuevoRol} onChange={(e) => setNuevoRol(e.target.value)}>
              {ROLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <button className="bp wf jc" onClick={guardarRol}>Guardar</button>
        </Modal>
      )}
    </div>
  );
}
