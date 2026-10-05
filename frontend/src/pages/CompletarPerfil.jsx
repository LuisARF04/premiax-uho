import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function CompletarPerfil() {
  const { usuario, actualizarUsuario } = useAuth();
  const navigate = useNavigate();
  const [areas, setAreas] = useState([]);
  const [categoriasDocentes, setCategoriasDocentes] = useState([]);
  const [categoriasCientificas, setCategoriasCientificas] = useState([]);
  const [form, setForm] = useState({ area: '', departamento: '', categoria_docente: '', categoria_cientifica: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    if (usuario?.perfil_completo) navigate('/app/dashboard');
    api.get('/areas/').then((r) => setAreas(r.data.results || r.data));
    api.get('/categorias-docentes/').then((r) => setCategoriasDocentes(r.data.results || r.data));
    api.get('/categorias-cientificas/').then((r) => setCategoriasCientificas(r.data.results || r.data));
  }, []);

  const areaSel = areas.find((a) => String(a.id) === String(form.area));

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (!form.area || !form.departamento) {
      setError('Debe seleccionar área y departamento.');
      return;
    }
    try {
      const payload = {
        ...form,
        categoria_docente: form.categoria_docente || null,
        categoria_cientifica: form.categoria_cientifica || null,
      };
      const { data } = await api.post('/auth/completar-perfil/', payload);
      actualizarUsuario(data);
      navigate('/app/dashboard');
    } catch (err) {
      setError('No se pudo guardar el perfil.');
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--pale)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div className="card" style={{ maxWidth: 520, width: '100%', overflow: 'hidden' }}>
        <div style={{ background: 'linear-gradient(90deg,var(--blue),var(--blue2))', padding: '22px 26px', color: '#fff' }}>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 3 }}>¡Bienvenido/a, {usuario?.nombre_completo}!</div>
          <div style={{ fontSize: '.81rem', opacity: .8 }}>Es tu primer acceso. Por favor completa tu perfil.</div>
        </div>
        <div className="cb">
          <div className="al-info"><span>👤</span><div>Datos cargados de AGA_AUTH: <strong>{usuario?.nombre_completo} · {usuario?.tipo_aga}</strong></div></div>
          {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
          <form onSubmit={handleSubmit}>
            <div className="fg2">
              <div className="fg">
                <label className="req">Área de la Universidad</label>
                <select className="fc" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value, departamento: '' })} required>
                  <option value="">Seleccionar área...</option>
                  {areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
                </select>
              </div>
              <div className="fg">
                <label className="req">Departamento</label>
                <select className="fc" value={form.departamento} onChange={(e) => setForm({ ...form, departamento: e.target.value })} required disabled={!areaSel}>
                  <option value="">Seleccionar...</option>
                  {(areaSel?.departamentos || []).map((d) => <option key={d.id} value={d.id}>{d.nombre}</option>)}
                </select>
              </div>
              <div className="fg">
                <label>Categoría Docente</label>
                <select className="fc" value={form.categoria_docente} onChange={(e) => setForm({ ...form, categoria_docente: e.target.value })}>
                  <option value="">No aplica</option>
                  {categoriasDocentes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </div>
              <div className="fg">
                <label>Categoría Científica</label>
                <select className="fc" value={form.categoria_cientifica} onChange={(e) => setForm({ ...form, categoria_cientifica: e.target.value })}>
                  <option value="">No aplica</option>
                  {categoriasCientificas.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </div>
            </div>
            <button className="bp wf jc mt16" style={{ padding: 11 }} type="submit">✅ Guardar y Continuar</button>
          </form>
        </div>
      </div>
    </div>
  );
}
