const loginPanel = document.querySelector('#login-panel');
const workspace = document.querySelector('#workspace');
const form = document.querySelector('#record-form');
const records = document.querySelector('#records');
const feedback = document.querySelector('#feedback');
const tabs = document.querySelectorAll('[data-tab]');
let token = sessionStorage.getItem('staff-token');
let catalog = { developments: [], properties: [], faqs: [] };
let section = 'developments';
let editingId = null;

const fields = {
  developments: [
    ['nombre', 'Nombre', 'text', true], ['ciudad', 'Ciudad', 'text', true], ['estado', 'Estado', 'text', true],
    ['zona', 'Zona', 'text'], ['activo', 'Desarrollo activo', 'checkbox']
  ],
  properties: [
    ['codigo', 'Código', 'text', true], ['nombre', 'Nombre', 'text', true], ['tipo', 'Tipo', 'select', true],
    ['precio', 'Precio', 'number', true], ['recamaras', 'Recámaras', 'number'],
    ['banos', 'Baños', 'number'], ['construccion_m2', 'Construcción m²', 'number'],
    ['terreno_m2', 'Terreno m²', 'number'], ['descripcion', 'Descripción', 'textarea'],
    ['disponibilidad', 'Disponibilidad', 'select'], ['desarrollo_id', 'Desarrollo', 'select']
  ],
  faqs: [['categoria', 'Categoría', 'text', true], ['pregunta', 'Pregunta', 'text', true], ['respuesta', 'Respuesta', 'textarea', true], ['activo', 'Visible en el chat', 'checkbox']]
};
const titles = { developments: 'Desarrollo', properties: 'Propiedad', faqs: 'Pregunta frecuente' };
const singularRoutes = { developments: 'developments', properties: 'properties', faqs: 'faqs' };

function message(text, error = false) {
  feedback.textContent = text;
  feedback.classList.toggle('error', error);
}

async function api(path, options = {}) {
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) logout();
    throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la operación.');
  }
  return data;
}

function logout() {
  token = null;
  sessionStorage.removeItem('staff-token');
  loginPanel.hidden = false;
  workspace.hidden = true;
}

async function loadCatalog() {
  catalog = await api('/staff/catalog');
  loginPanel.hidden = true;
  workspace.hidden = false;
  render();
}

function render() {
  tabs.forEach(tab => tab.classList.toggle('active', tab.dataset.tab === section));
  document.querySelector('#form-title').textContent = `${editingId ? 'Editar' : 'Nuevo'} ${titles[section].toLowerCase()}`;
  const current = catalog[section].find(item => item.id === editingId) || {};
  form.replaceChildren();
  for (const [name, labelText, type, required] of fields[section]) {
    const label = document.createElement('label');
    label.textContent = labelText;
    let input;
    if (type === 'textarea') input = document.createElement('textarea');
    else if (type === 'select') {
      input = document.createElement('select');
      if (name === 'desarrollo_id') {
        input.add(new Option('Sin desarrollo', ''));
        catalog.developments.forEach(dev => input.add(new Option(dev.nombre, dev.id)));
      } else {
        const options = name === 'tipo' ? ['Casa', 'Departamento', 'Terreno'] : ['Disponible', 'Apartada', 'Vendida', 'No disponible'];
        options.forEach(option => input.add(new Option(option, option)));
      }
    } else {
      input = document.createElement('input');
      input.type = type;
      if (type === 'number') { input.min = '0'; input.step = name === 'recamaras' ? '1' : name === 'banos' ? '0.1' : '0.01'; }
    }
    input.name = name;
    input.required = Boolean(required);
    if (type === 'checkbox') input.checked = current[name] ?? true;
    else input.value = current[name] ?? (name === 'disponibilidad' ? 'Disponible' : name === 'tipo' ? 'Casa' : '');
    label.append(input);
    form.append(label);
  }
  const actions = document.createElement('div');
  actions.className = 'actions';
  const save = document.createElement('button');
  save.textContent = editingId ? 'Guardar cambios' : 'Crear registro';
  actions.append(save);
  if (editingId) {
    const cancel = document.createElement('button');
    cancel.type = 'button'; cancel.className = 'secondary'; cancel.textContent = 'Cancelar';
    cancel.addEventListener('click', () => { editingId = null; render(); });
    actions.append(cancel);
  }
  form.append(actions);

  records.replaceChildren();
  if (!catalog[section].length) records.textContent = 'Todavía no hay registros.';
  for (const item of catalog[section]) {
    const row = document.createElement('div'); row.className = 'row';
    const info = document.createElement('div');
    const name = document.createElement('strong');
    name.textContent = item.nombre || item.pregunta;
    const detail = document.createElement('small');
    detail.textContent = section === 'properties' ? `${item.codigo} · ${item.disponibilidad}` : section === 'faqs' ? (item.activo ? 'Visible' : 'Oculta') : (item.activo ? 'Activo' : 'Inactivo');
    info.append(name, detail);
    const edit = document.createElement('button'); edit.textContent = 'Editar';
    edit.addEventListener('click', () => { editingId = item.id; render(); form.scrollIntoView({ behavior: 'smooth' }); });
    row.append(info, edit); records.append(row);
  }
}

document.querySelector('#login-form').addEventListener('submit', async event => {
  event.preventDefault();
  const body = Object.fromEntries(new FormData(event.currentTarget));
  try {
    const data = await api('/auth/login', { method: 'POST', body: JSON.stringify(body) });
    if (!['agent', 'admin'].includes(data.user.role)) throw new Error('Esta cuenta no tiene acceso al panel.');
    token = data.access_token;
    sessionStorage.setItem('staff-token', token);
    loginPanel.hidden = true; workspace.hidden = false; render();
    try { await loadCatalog(); message('Sesión iniciada.'); }
    catch { message('Acceso concedido, pero no se pudo conectar al catálogo. Revisa la conexión a MySQL.', true); }
  } catch (error) { message(error.message, true); }
});

tabs.forEach(tab => tab.addEventListener('click', () => { section = tab.dataset.tab; editingId = null; message(''); render(); }));
document.querySelector('#logout').addEventListener('click', () => { logout(); message('Sesión cerrada.'); });
form.addEventListener('submit', async event => {
  event.preventDefault();
  const body = {};
  for (const [name, , type] of fields[section]) {
    const input = form.elements[name];
    body[name] = type === 'checkbox' ? input.checked : type === 'number' ? (input.value === '' ? (['precio', 'banos', 'recamaras'].includes(name) ? 0 : null) : Number(input.value)) : name === 'desarrollo_id' ? (input.value ? Number(input.value) : null) : input.value.trim();
  }
  const button = form.querySelector('button[type=submit], .actions button'); button.disabled = true;
  try {
    await api(`/staff/${singularRoutes[section]}${editingId ? `/${editingId}` : ''}`, { method: editingId ? 'PUT' : 'POST', body: JSON.stringify(body) });
    const saved = editingId ? 'actualizado' : 'creado';
    editingId = null; await loadCatalog(); message(`Registro ${saved} correctamente.`);
  } catch (error) { message(error.message, true); }
  finally { button.disabled = false; }
});

if (token) loadCatalog().catch(error => message(error.message, true));
