import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';
import { Loading, EstadoBadge } from '../components/ui';

export default function PanelComision() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [comision, setComision] = useState(null);
  const [propuestas, setPropuestas] = useState(null);

  useEffect(() => {
    api.get(`/comisiones/${id}/`).then((r) => setComision(r.data));
    api.get('/propuestas/', { params: { comision: id, page_size: 200 } }).then((r) => setPropuestas(r.data.results || r.data));
  }, [id]);

  if (!comision || !propuestas) return <Loading />;

  const porPremio = {};
  propuestas.forEach((p) => {
    if (!porPremio[p.premio]) porPremio[p.premio] = { nombre: p.premio_nombre, items: [] };
    porPremio[p.premio].items.push(p);
  });

  return (
    <div>
      <div className="ph">
        <div><h2>Comisión: {comision.nombre}</h2><div className="phs">Dirige: {comision.jefe_detalle?.nombre_completo || '—'} · {propuestas.length} propuestas para revisar</div></div>
      </div>
      <div className="ca">
        <div className="g2 mb20">
          <div className="kc go"><div className="ki">📝</div><div className="kv">{propuestas.length}</div><div className="kl">Propuestas recibidas</div></div>
          <div className="kc gr"><div className="ki">✅</div><div className="kv">{propuestas.filter((p) => p.estado !== 'en_comision').length}</div><div className="kl">Revisadas</div></div>
        </div>
        <div className="card">
          <div className="ch"><h3>Propuestas por Premio</h3></div>
          <table className="dt">
            <thead><tr><th>Premio</th><th>Propuestas</th><th>Estado</th><th>Acción</th></tr></thead>
            <tbody>
              {Object.entries(porPremio).map(([premioId, grupo]) => {
                const pendientes = grupo.items.filter((i) => i.estado === 'en_comision').length;
                return (
                  <tr key={premioId}>
                    <td><strong>{grupo.nombre}</strong></td>
                    <td>{grupo.items.length}</td>
                    <td>{pendientes > 0 ? <span className="bg bg-wn">En revisión</span> : <span className="bg bg-gr">Revisada</span>}</td>
                    <td>
                      <button className={pendientes > 0 ? 'bp' : 'bs'} style={{ fontSize: '.73rem', padding: '3px 8px' }}
                        onClick={() => navigate(`/app/comisiones/${id}/proponer-ganadores/${premioId}`)}>
                        {pendientes > 0 ? 'Revisar / Proponer' : 'Ver'}
                      </button>
                    </td>
                  </tr>
                );
              })}
              {!Object.keys(porPremio).length && <tr><td colSpan={4} className="tm">Sin propuestas asignadas a esta comisión aún.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
