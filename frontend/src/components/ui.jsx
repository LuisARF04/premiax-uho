export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="ph">
      <div>
        <h2>{title}</h2>
        {subtitle && <div className="phs">{subtitle}</div>}
      </div>
      {actions && <div className="ha">{actions}</div>}
    </div>
  );
}

export function Loading() {
  return <div className="spinner" />;
}

export function EmptyState({ text = 'No hay datos para mostrar.' }) {
  return <div className="empty-state">{text}</div>;
}

const ESTADO_BADGES = {
  pendiente_departamento: ['bg-gy', 'Pendiente Dpto.'],
  pendiente_area: ['bg-bl', 'Pendiente Área'],
  en_comision: ['bg-wn', 'En Comisión'],
  ganadora_propuesta: ['bg-go', 'Ganadora Propuesta'],
  aprobada: ['bg-gr', '✅ Aprobada'],
  rechazada: ['bg-re', '✗ Rechazada'],
  proxima: ['bg-gy', 'Próxima'],
  en_curso: ['bg-wn', '▶ En Curso'],
  finalizada: ['bg-gr', '✅ Finalizada'],
};

export function EstadoBadge({ estado }) {
  const [cls, label] = ESTADO_BADGES[estado] || ['bg-gy', estado];
  return <span className={`bg ${cls}`}>{label}</span>;
}

export function KpiCard({ icon, value, label, color = 'bl', trend }) {
  return (
    <div className={`kc ${color}`}>
      <div className="ki">{icon}</div>
      <div className="kv">{value}</div>
      <div className="kl">{label}</div>
      {trend && <div className="kt up">{trend}</div>}
    </div>
  );
}

export function Modal({ title, onClose, children, width = 520 }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="card modal-box" style={{ maxWidth: width }} onClick={(e) => e.stopPropagation()}>
        <div className="ch">
          <h3>{title}</h3>
          <button className="bs" onClick={onClose}>✕</button>
        </div>
        <div className="cb">{children}</div>
      </div>
    </div>
  );
}

export function Avatar({ nombre, size = 30 }) {
  const iniciales = (nombre || '?').split(' ').filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase();
  return (
    <div className="av" style={{ width: size, height: size, fontSize: size * 0.35 }}>{iniciales}</div>
  );
}
