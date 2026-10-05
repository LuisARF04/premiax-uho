import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading } from '../components/ui';

export default function Notificaciones() {
  const [items, setItems] = useState(null);

  function cargar() {
    api.get('/notificaciones/', { params: { page_size: 100 } }).then((r) => setItems(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  async function marcarLeida(id) {
    await api.patch(`/notificaciones/${id}/marcar_leida/`);
    cargar();
  }

  async function marcarTodas() {
    await api.post('/notificaciones/marcar_todas_leidas/');
    cargar();
  }

  if (!items) return <Loading />;
  const noLeidas = items.filter((n) => !n.leida).length;

  return (
    <div>
      <PageHeader title="Notificaciones" subtitle={`${noLeidas} notificaciones sin leer`}
        actions={<button className="bs" onClick={marcarTodas}>Marcar todas como leídas</button>} />
      <div className="ca" style={{ maxWidth: 660 }}>
        <div className="card">
          {items.map((n) => (
            <div className={`ni ${!n.leida ? 'unr' : ''}`} key={n.id} onClick={() => !n.leida && marcarLeida(n.id)}>
              <div className={`ndot ${n.leida ? 'rd' : ''}`} />
              <div style={{ flex: 1 }}>
                <div className="ntit">{n.titulo}</div>
                <div className="nmsg">{n.mensaje}</div>
                <div className="ntm">{new Date(n.fecha).toLocaleString()}</div>
              </div>
            </div>
          ))}
          {!items.length && <div className="empty-state">No tienes notificaciones.</div>}
        </div>
      </div>
    </div>
  );
}
