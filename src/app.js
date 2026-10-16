import { api } from "./api.js";
import { sceneGrid } from "./production.js";

const labels={PUBLISHED:"Publicado",GENERATING:"En producción",PLANNED:"Planificado",IDEA:"Por definir"};
let data;
const DEMO_KEY="cozy-publishing-studio-demo-v1";

function saveDemo(){localStorage.setItem(DEMO_KEY,JSON.stringify(data))}
async function loadData(){
  const saved=localStorage.getItem(DEMO_KEY);
  if(saved) return JSON.parse(saved);
  const r=await fetch("./data/demo.json",{cache:"no-store"});
  if(!r.ok)throw new Error("No se pudo cargar el estado editorial");
  return r.json()
}
function demoBook(input,position){
  return {position,title:input.title,subtitle:input.subtitle||"",lockedBrief:input.locked_brief||"",status:"PLANNED",progress:0,lockedScenes:0,totalScenes:40,scenes:Array.from({length:40},(_,i)=>({number:i+1,title:`Escena ${i+1}: ${input.title}`,state:"PENDING"}))}
}
function createDemoSeries(payload){
  data={series:{name:payload.name,targetBooks:5,books:payload.books.map((b,i)=>demoBook(b,i+1))}};
  saveDemo();
  renderDashboard();
}
function startDemoProduction(book,complete=false){
  if(!book.lockedBrief?.trim()) throw new Error("Añade una identidad visual bloqueada antes de producir.");
  book.status="GENERATING";
  book.lockedScenes=complete?40:Math.min(40,(book.lockedScenes||0)+1);
  book.progress=Math.round(book.lockedScenes/40*100);
  book.scenes=book.scenes||Array.from({length:40},(_,i)=>({number:i+1,title:`Escena ${i+1}: ${book.title}`,state:"PENDING"}));
  book.scenes.slice(0,book.lockedScenes).forEach(s=>s.state="LOCKED");
  if(book.lockedScenes===40) book.status="ART_LOCKED";
  saveDemo();
}
function card(b){return `<article class="book-card"><div class="book-top"><span class="book-number">Libro ${b.position}</span><span class="pill ${(b.status||"IDEA").toLowerCase()}">${labels[b.status]||b.status}</span></div><h3>${b.title}</h3><div class="progress"><span style="width:${b.progress||0}%"></span></div><div class="book-footer"><span>${b.progress||0}%</span><button data-book="${b.position}">Ver libro</button></div></article>`}
function shell(content,active="Dashboard"){return `<div class="shell"><aside><div class="brand"><div class="mark">C</div><div><strong>Cozy</strong><span>Publishing Studio</span></div></div><nav>${["Dashboard","Mis series","Producción","Biblioteca","Publicación"].map(x=>`<button data-nav="${x}" class="${x===active?"active":""}"><span>${x}</span></button>`).join("")}</nav><div class="aside-note"><b>Automatización</b><span>Solo se detiene por un defecto material o una decisión humana real.</span></div></aside><main>${content}<footer>v0.3 · Publicación final siempre requiere aprobación humana.</footer></main></div>`}
function bindNav(){document.querySelectorAll("[data-nav]").forEach(b=>b.onclick=()=>b.dataset.nav==="Producción"?renderProduction():renderDashboard())}
function renderDashboard(){const s=data.series,books=s.books,active=books.find(b=>b.status==="GENERATING");document.querySelector("#app").innerHTML=shell(`<header><div><span class="eyebrow">COZY PUBLISHING STUDIO</span><h1>Tu editorial, de un vistazo.</h1><p>Series, producción y publicación sin copiar prompts entre chats.</p></div><button class="primary" id="newSeries">+ Nueva serie</button></header><section class="stats"><div><span>Series activas</span><strong>1</strong></div><div><span>Libros</span><strong>${books.length}</strong></div><div><span>En producción</span><strong>${books.filter(b=>b.status==="GENERATING").length}</strong></div><div><span>Esperando aprobación</span><strong>0</strong></div></section><section class="section-head"><div><span class="eyebrow">SERIE ACTIVA</span><h2>${s.name}</h2><p>${s.targetBooks} libros · Producción automatizada con control de calidad.</p></div></section><section class="books">${books.map(card).join("")}</section>${active?`<section class="activity"><div><span class="eyebrow">AHORA</span><h2>${active.title}</h2><p>Las escenas aprobadas quedan bloqueadas automáticamente.</p></div><div class="activity-right"><strong>${String(active.lockedScenes).padStart(2,"0")} / ${active.totalScenes}</strong><span>ART LOCKED</span></div></section>`:""}<dialog id="modal"><h2>Nueva serie</h2><form id="seriesForm"><label>Nombre<input name="name" required placeholder="Cozy Little Worlds II"></label>${[1,2,3,4,5].map(i=>`<fieldset><legend>Libro ${i}</legend><label>Título<input name="book${i}" required placeholder="Título del libro ${i}"></label><label>Subtítulo<input name="subtitle${i}" placeholder="Subtítulo editorial"></label><label>Identidad visual bloqueada<textarea name="brief${i}" rows="3" required placeholder="Rasgos visuales que deben mantenerse en las 40 escenas"></textarea></label></fieldset>`).join("")}<div class="dialog-actions"><button type="button" class="ghost" id="cancel">Cancelar</button><button class="primary">Crear serie</button></div><p id="formStatus"></p></form></dialog>`,"Dashboard");bindNav();document.querySelector("#newSeries").onclick=()=>document.querySelector("#modal").showModal();document.querySelector("#cancel").onclick=()=>document.querySelector("#modal").close();document.querySelector("#seriesForm").onsubmit=submitSeries;document.querySelectorAll("[data-book]").forEach(b=>b.onclick=()=>renderBook(Number(b.dataset.book)))}
async function submitSeries(e){e.preventDefault();const f=new FormData(e.currentTarget),status=document.querySelector("#formStatus");try{status.textContent="Creando…";const payload={name:f.get("name"),books:[1,2,3,4,5].map(i=>({title:f.get(`book${i}`),subtitle:f.get(`subtitle${i}`)||"",locked_brief:f.get(`brief${i}`)||""}))};if(!api.enabled){createDemoSeries(payload);return}const r=await api.createSeries(payload);status.textContent=`Serie creada: ${r.name}`}catch(err){status.textContent=err.message}}
function renderBook(pos){const b=data.series.books.find(x=>x.position===pos);document.querySelector("#app").innerHTML=shell(`<button class="ghost" id="back">← Dashboard</button><section class="book-detail"><span class="eyebrow">LIBRO ${b.position}</span><h1>${b.title}</h1><p>${b.subtitle||""}</p><p><strong>Identidad visual:</strong> ${b.lockedBrief||"Pendiente"}</p><p>Estado: ${labels[b.status]||b.status}</p><div class="dialog-actions"><button class="primary" id="advanceDemo">${b.status==="PLANNED"?"Iniciar producción demo":"Procesar siguiente escena"}</button><button class="ghost" id="completeDemo">Completar 40 escenas demo</button></div><p id="bookStatus"></p>${sceneGrid(b)}</section>`,"Producción");bindNav();document.querySelector("#back").onclick=renderDashboard;document.querySelector("#advanceDemo").onclick=()=>{try{startDemoProduction(b);renderBook(pos)}catch(err){document.querySelector("#bookStatus").textContent=err.message}};document.querySelector("#completeDemo").onclick=()=>{try{startDemoProduction(b,true);renderBook(pos)}catch(err){document.querySelector("#bookStatus").textContent=err.message}}}
function renderProduction(){const b=data.series.books.find(x=>x.status==="GENERATING")||data.series.books[0];renderBook(b.position)}
loadData().then(x=>{data=x;renderDashboard()}).catch(e=>document.querySelector("#app").innerHTML=`<main><h1>Cozy Publishing Studio</h1><p>${e.message}</p></main>`);
