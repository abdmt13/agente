const $ = selector => document.querySelector(selector);
const loginPanel = $('#login-panel');
const workspace = $('#workspace');
const form = $('#record-form');
const records = $('#records');
const feedback = $('#feedback');
const editor = $('#editor');
const backdrop = $('#editor-backdrop');
const tabs = document.querySelectorAll('[data-tab]');
let token = sessionStorage.getItem('staff-token');
let catalog = { developments: [], properties: [], faqs: [] };
let section = 'developments';
let editingId = null;

const fields = {
  developments: [
    ['nombre','Nombre del desarrollo','text',true,'Ej. Torre del Mar'],['ciudad','Ciudad','text',true,'Ej. Cancún'],
    ['estado','Estado','text',true,'Ej. Quintana Roo'],['zona','Zona o colonia','text',false,'Ej. Zona Hotelera'],['activo','Desarrollo activo','checkbox']
  ],
  properties: [
    ['codigo','Código interno','text',true,'Ej. TM-1204'],['nombre','Nombre de la propiedad','text',true,'Ej. Departamento 1204'],
    ['tipo','Tipo de propiedad','select',true],['precio','Precio','number',true,'0.00'],['recamaras','Recámaras','number',false,'0'],
    ['banos','Baños','number',false,'0'],['construccion_m2','Construcción (m²)','number',false,'0'],['terreno_m2','Terreno (m²)','number',false,'0'],
    ['desarrollo_id','Desarrollo','select',false],['disponibilidad','Estado comercial','select',true],['descripcion','Descripción para el cliente','textarea',false,'Describe acabados, amenidades y atributos importantes']
  ],
  faqs: [
    ['categoria','Categoría','text',true,'Ej. Financiamiento'],['pregunta','Pregunta','text',true,'Ej. ¿Aceptan crédito bancario?'],
    ['respuesta','Respuesta para el cliente','textarea',true,'Escribe una respuesta clara y completa'],['activo','Mostrar esta respuesta','checkbox']
  ]
};
const ui = {
  developments:{title:'Desarrollos',singular:'desarrollo',list:'Desarrollos registrados',description:'Administra los desarrollos donde se encuentran tus propiedades.',placeholder:'Buscar desarrollo...',icon:'▦'},
  properties:{title:'Propiedades',singular:'propiedad',list:'Propiedades registradas',description:'Actualiza inventario, precios, características y disponibilidad.',placeholder:'Buscar propiedad o código...',icon:'⌂'},
  faqs:{title:'Preguntas frecuentes',singular:'pregunta frecuente',list:'Respuestas registradas',description:'Define respuestas claras para las dudas habituales de tus clientes.',placeholder:'Buscar pregunta o categoría...',icon:'?'}
};
const routes = {developments:'developments',properties:'properties',faqs:'faqs'};

function showMessage(text,error=false){feedback.textContent=text;feedback.classList.toggle('error',error);feedback.hidden=false;clearTimeout(showMessage.timer);showMessage.timer=setTimeout(()=>feedback.hidden=true,4500)}
async function request(path,options={}){const response=await fetch(`/api/v1${path}`,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{}) ,...options.headers}});const data=await response.json().catch(()=>({}));if(!response.ok){if(response.status===401)logout();throw new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación.')}return data}
function logout(){token=null;sessionStorage.removeItem('staff-token');closeEditor();loginPanel.hidden=false;workspace.hidden=true}
function transitionToWorkspace(){workspace.hidden=false;workspace.classList.add('entering');loginPanel.classList.add('leaving');setTimeout(()=>{loginPanel.hidden=true;loginPanel.classList.remove('leaving');workspace.classList.remove('entering')},420)}
async function loadCatalog(animate=false){catalog=await request('/staff/catalog');if(animate)transitionToWorkspace();else{loginPanel.hidden=true;workspace.hidden=false}render()}
function openEditor(id=null){editingId=id;buildForm();backdrop.hidden=false;editor.classList.add('open');editor.setAttribute('aria-hidden','false')}
function closeEditor(){editor.classList.remove('open');editor.setAttribute('aria-hidden','true');backdrop.hidden=true;editingId=null}
function developmentName(id){return catalog.developments.find(item=>item.id===id)?.nombre||'Sin desarrollo'}
function money(value){return new Intl.NumberFormat('es-MX',{maximumFractionDigits:2}).format(Number(value||0))}

function render(){
  const meta=ui[section];tabs.forEach(tab=>tab.classList.toggle('active',tab.dataset.tab===section));
  $('#page-title').textContent=meta.title;$('#page-description').textContent=meta.description;$('#new-label').textContent=`Nuevo ${meta.singular}`;
  $('#list-title').textContent=meta.list;$('#search').placeholder=meta.placeholder;
  $('#stat-developments').textContent=catalog.developments.length;$('#stat-properties').textContent=catalog.properties.length;
  $('#stat-available').textContent=catalog.properties.filter(x=>x.disponibilidad==='Disponible').length;$('#stat-faqs').textContent=catalog.faqs.filter(x=>x.activo).length;
  renderRecords();
}

function renderRecords(){
  const query=$('#search').value.trim().toLowerCase();
  const items=catalog[section].filter(item=>Object.values(item).some(value=>String(value??'').toLowerCase().includes(query)));
  $('#record-count').textContent=`${items.length} ${items.length===1?'registro':'registros'}`;records.replaceChildren();
  if(!items.length){const empty=document.createElement('div');empty.className='empty';empty.innerHTML=`<span>${ui[section].icon}</span>${query?'No encontramos coincidencias.':'Aún no hay registros. Usa el botón superior para agregar el primero.'}`;records.append(empty);return}
  for(const item of items){
    const card=document.createElement('article');card.className='record-card';
    const main=document.createElement('div');main.className='record-main';const avatar=document.createElement('span');avatar.className='record-avatar';avatar.textContent=ui[section].icon;
    const info=document.createElement('div');info.className='record-info';const title=document.createElement('strong');title.textContent=item.nombre||item.pregunta;
    const meta=document.createElement('div');meta.className='record-meta';
    if(section==='developments') meta.innerHTML=`<span>${[item.zona,item.ciudad,item.estado].filter(Boolean).join(' · ')}</span><span class="badge ${item.activo?'active':'inactive'}">${item.activo?'Activo':'Inactivo'}</span>`;
    if(section==='properties') meta.innerHTML=`<span>${item.codigo} · ${developmentName(item.desarrollo_id)} · $${money(item.precio)}</span><span class="badge ${item.disponibilidad==='Disponible'?'available':'sold'}">${item.disponibilidad}</span>`;
    if(section==='faqs') meta.innerHTML=`<span>${item.categoria}</span><span class="badge ${item.activo?'active':'inactive'}">${item.activo?'Visible':'Oculta'}</span>`;
    info.append(title,meta);main.append(avatar,info);const edit=document.createElement('button');edit.className='edit-button';edit.textContent='Editar';edit.addEventListener('click',()=>openEditor(item.id));card.append(main,edit);records.append(card)
  }
}

function buildForm(){
  const current=catalog[section].find(item=>item.id===editingId)||{};const meta=ui[section];
  $('#form-title').textContent=`${editingId?'Editar':'Nuevo'} ${meta.singular}`;$('#form-description').textContent=`Completa la información del ${meta.singular}. Los campos con * son obligatorios.`;form.replaceChildren();
  for(const [name,labelText,type,required,placeholder] of fields[section]){
    const label=document.createElement('label');label.append(document.createTextNode(`${labelText}${required?' *':''}`));let input;
    if(type==='textarea')input=document.createElement('textarea');
    else if(type==='select'){input=document.createElement('select');if(name==='desarrollo_id'){input.add(new Option('Sin desarrollo asignado',''));catalog.developments.forEach(dev=>input.add(new Option(dev.nombre,dev.id)))}else{const options=name==='tipo'?['Casa','Departamento','Terreno']:['Disponible','Apartada','Vendida','No disponible'];options.forEach(option=>input.add(new Option(option,option)))}}
    else{input=document.createElement('input');input.type=type;if(type==='number'){input.min='0';input.step=name==='recamaras'?'1':name==='banos'?'0.1':'0.01'}}
    input.name=name;input.required=Boolean(required);if(placeholder)input.placeholder=placeholder;
    if(type==='checkbox'){input.checked=current[name]??true;label.className='checkbox-label'}else input.value=current[name]??(name==='disponibilidad'?'Disponible':name==='tipo'?'Casa':'');
    label.append(input);form.append(label)
  }
  const actions=document.createElement('div');actions.className='form-actions';const cancel=document.createElement('button');cancel.type='button';cancel.className='secondary';cancel.textContent='Cancelar';cancel.addEventListener('click',closeEditor);const save=document.createElement('button');save.className='primary';save.textContent=editingId?'Guardar cambios':'Crear registro';actions.append(cancel,save);form.append(actions)
}

$('#login-form').addEventListener('submit',async event=>{event.preventDefault();const body=Object.fromEntries(new FormData(event.currentTarget));const button=event.currentTarget.querySelector('button');button.disabled=true;try{const data=await request('/auth/login',{method:'POST',body:JSON.stringify(body)});if(!['agent','admin'].includes(data.user.role))throw new Error('Esta cuenta no tiene acceso al panel.');token=data.access_token;sessionStorage.setItem('staff-token',token);await loadCatalog(true);showMessage('Sesión iniciada correctamente.')}catch(error){showMessage(error.message,true)}finally{button.disabled=false}});
tabs.forEach(tab=>tab.addEventListener('click',()=>{section=tab.dataset.tab;editingId=null;$('#search').value='';closeEditor();render()}));
$('#search').addEventListener('input',renderRecords);$('#new-record').addEventListener('click',()=>openEditor());$('#close-editor').addEventListener('click',closeEditor);backdrop.addEventListener('click',closeEditor);$('#logout').addEventListener('click',()=>{logout();showMessage('Sesión cerrada.')});
form.addEventListener('submit',async event=>{event.preventDefault();const body={};for(const [name,,type] of fields[section]){const input=form.elements[name];body[name]=type==='checkbox'?input.checked:type==='number'?(input.value===''?(['precio','banos','recamaras'].includes(name)?0:null):Number(input.value)):name==='desarrollo_id'?(input.value?Number(input.value):null):input.value.trim()}const button=form.querySelector('.primary');button.disabled=true;try{await request(`/staff/${routes[section]}${editingId?`/${editingId}`:''}`,{method:editingId?'PUT':'POST',body:JSON.stringify(body)});const changed=editingId?'actualizado':'creado';closeEditor();await loadCatalog();showMessage(`Registro ${changed} correctamente.`)}catch(error){showMessage(error.message,true)}finally{button.disabled=false}});
if(token)loadCatalog().catch(error=>{logout();showMessage(error.message,true)});
