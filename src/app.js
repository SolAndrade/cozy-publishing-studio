const labels = { PUBLISHED:"Publicado", GENERATING:"En producción", PLANNED:"Planificado", IDEA:"Por definir" };

async function loadData() {
  const response = await fetch("./data/demo.json", { cache: "no-store" });
  if (!response.ok) throw new Error("No se pudo cargar el estado editorial");
  return response.json();
}

function bookCard(book) {
  const state = book.status || "IDEA";
  return `<article class="book-card">
    <div class="book-top"><span class="book-number">Libro ${book.position}</span><span class="pill ${state.toLowerCase()}">${labels[state] || state}</span></div>
    <h3>${book.title}</h3>
    <div class="progress"><span style="width:${book.progress || 0}%"></span></div>
    <div class="book-footer"><span>${book.progress || 0}%</span><button type="button" data-book="${book.position}">Ver libro</button></div>
  </article>`;
}

function render(data) {
  const series=data.series, books=series.books;
  const producing=books.filter(b=>b.status==="GENERATING").length;
  const active=books.find(b=>b.status==="GENERATING");
  document.querySelector("#app").innerHTML=`
  <div class="shell"><aside>
    <div class="brand"><div class="mark">C</div><div><strong>Cozy</strong><span>Publishing Studio</span></div></div>
    <nav><button class="active">⌂ <span>Dashboard</span></button><button>▣ <span>Mis series</span></button><button>✦ <span>Producción</span></button><button>□ <span>Biblioteca</span></button><button>↑ <span>Publicación</span></button></nav>
    <div class="aside-note"><b>Automatización</b><span>Solo te avisaremos cuando haga falta una decisión real.</span></div>
  </aside><main>
    <header><div><span class="eyebrow">COZY PUBLISHING STUDIO</span><h1>Tu editorial, de un vistazo.</h1><p>Series, producción y publicación sin copiar prompts entre chats.</p></div><button class="primary" id="newSeries">+ Nueva serie</button></header>
    <section class="stats"><div><span>Series activas</span><strong>1</strong></div><div><span>Libros</span><strong>${books.length}</strong></div><div><span>En producción</span><strong>${producing}</strong></div><div><span>Esperando tu aprobación</span><strong>0</strong></div></section>
    <section class="section-head"><div><span class="eyebrow">SERIE ACTIVA</span><h2>${series.name}</h2><p>${series.targetBooks} libros · Producción automatizada con control de calidad.</p></div><button class="ghost">Gestionar serie</button></section>
    <section class="books">${books.map(bookCard).join("")}</section>
    ${active ? `<section class="activity"><div><span class="eyebrow">AHORA</span><h2>${active.title}</h2><p>Producción artística en curso. Las escenas aprobadas quedan bloqueadas automáticamente.</p></div><div class="activity-right"><strong>${String(active.lockedScenes).padStart(2,"0")} / ${active.totalScenes}</strong><span>ART LOCKED</span><div class="progress big"><span style="width:${active.progress}%"></span></div></div></section>` : ""}
    <footer>v0.2 · La aprobación humana final permanece obligatoria.</footer>
  </main></div>
  <dialog id="modal"><h2>Nueva serie</h2><p>El motor está preparado para trabajar con series de exactamente cinco libros. La conexión con IA y persistencia privada será el siguiente backend.</p><button id="closeModal" class="primary">Entendido</button></dialog>`;
  const modal=document.querySelector("#modal");
  document.querySelector("#newSeries").addEventListener("click",()=>modal.showModal());
  document.querySelector("#closeModal").addEventListener("click",()=>modal.close());
  document.querySelectorAll("[data-book]").forEach(btn=>btn.addEventListener("click",()=>{
    const b=books.find(x=>x.position===Number(btn.dataset.book));
    alert(`${b.title}\nEstado: ${labels[b.status] || b.status}\nProgreso: ${b.progress || 0}%`);
  }));
}

loadData().then(render).catch(error=>{
  document.querySelector("#app").innerHTML=`<main><h1>Cozy Publishing Studio</h1><p>No se pudo cargar el dashboard.</p><pre>${error.message}</pre></main>`;
});
