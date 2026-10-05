import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading } from '../components/ui';

export default function Auditoria() {
  const [logs, setLogs] = useState(null);
  const [busqueda, setBusqueda] = useState('');
  const [modulo, setModulo] = useState('');

  useEffect(() => {
    api.get('/auditoria/', { params: { search: busqueda || undefined, modulo: modulo || undefined, page_size: 100 } })
      .then((r) => setLogs(r.data.results || r.data));
  }, [busqueda, modulo]);

  return (
    <div>
      <PageHeader title="Logs de Auditoría" subtitle="Registro completo de todas las acciones de usuarios"
        actions={<>
          <input className="fc" style={{ width: 210 }} placeholder="🔍 Buscar usuario o acción..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          <select className="fc" style={{ width: 170 }} value={modulo} onChange={(e) => setModulo(e.target.value)}>
            <option value="">Todos los módulos</option>
            {['propuestas', 'usuarios', 'comisiones', 'premios', 'organizacion', 'nomencladores', 'ganadores', 'auth'].map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </>} />
      <div className="ca">
        {!logs ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Fecha y Hora</th><th>Usuario</th><th>Módulo</th><th>Acción</th><th>Detalle</th><th>IP</th></tr></thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.id}>
                    <td className="tsm">{new Date(l.fecha).toLocaleString()}</td>
                    <td><strong>{l.usuario_nombre}</strong>{l.usuario_rol && <div className="tsm tm">{l.usuario_rol}</div>}</td>
                    <td><span className="bg bg-bl">{l.modulo}</span></td>
                    <td className="tsm">{l.accion}</td>
                    <td className="tsm tm">{l.detalle}</td>
                    <td className="tsm tm">{l.ip || '—'}</td>
                  </tr>
                ))}
                {!logs.length && <tr><td colSpan={6} className="tm">Sin registros para este filtro.</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
