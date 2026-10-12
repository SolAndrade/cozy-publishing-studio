const books = [
  { n: 1, title: "Cozy Little Rooms", state: "PUBLICADO", progress: 100 },
  { n: 2, title: "Cozy Little Shops", state: "PUBLICADO", progress: 100 },
  { n: 3, title: "Cozy Little Cafés", state: "GENERATING", progress: 8 },
  { n: 4, title: "Cozy Little Kitchens", state: "PLANNED", progress: 0 },
  { n: 5, title: "Por decidir", state: "IDEA", progress: 0 }
];

const labels = {
  PUBLICADO: "Publicado",
  GENERATING: "En producción",
  PLANNED: "Planificado",
  IDEA: "Por definir"
};

function bookCard(book) {
  return `
    <article class="book-card">
      <div class="book-top">
        <span class="book-number">Libro ${book.n}</span>
        <span class="pill ${book.state.toLowerCase()}">${labels[book.state]}</span>
      </div>
      <h3>${book.title}</h3>
      <div class="progress"><span style="width:${book.progress}%"></span></div>
      <div class="book-footer">
        <span>${book.progress}%</span>
        <button type="button" data-book="${book.n}">Ver libro</button>
      </div>
    </article>`;
}

document.querySelector("#app").innerHTML = `
  <div class="shell">
    <aside>
      <div class="brand"><div class="mark">C</div><div><strong>Cozy</strong><span>Publishing Studio</span></div></div>
      <nav>
        <button class="active">⌂ <span>Dashboard</span></button>
        <button>▣ <span>Mis series</span></button>
        <button>✦ <span>Producción</span></button>
        <button>□ <span>Biblioteca</span></button>
        <button>↑ <span>Publicación</span></button>
      </nav>
      <div class="aside-note"><b>Automatización</b><span>Solo te avisaremos cuando haga falta una decisión real.</span></div>
    </aside>
    <main>
      <header><div><span class="eyebrow">COZY PUBLISHING STUDIO</span><h1>Tu editorial, de un vistazo.</h1><p>Series, producción y publicación sin copiar prompts entre chats.</p></div><button class="primary" id="newSeries">+ Nueva serie</button></header>
      <section class="stats">
        <div><span>Series activas</span><strong>1</strong></div>
        <div><span>Libros</span><strong>5</strong></div>
        <div><span>En producción</span><strong>1</strong></div>
        <div><span>Esperando tu aprobación</span><strong>0</strong></div>
      </section>
      <section class="section-head"><div><span class="eyebrow">SERIE ACTIVA</span><h2>Cozy Little Worlds</h2><p>5 libros · Producción automatizada con control de calidad.</p></div><button class="ghost">Gestionar serie</button></section>
      <section class="books">${books.map(bookCard).join("")}</section>
      <section class="activity">
        <div><span class="eyebrow">AHORA</span><h2>Cozy Little Cafés</h2><p>Producción artística en curso. Las escenas aprobadas quedan bloqueadas automáticamente.</p></div>
        <div class="activity-right"><strong>03 / 40</strong><span>ART LOCKED</span><div class="progress big"><span style="width:7.5%"></span></div></div>
      </section>
      <footer>v0.1 · Human approval stays final.</footer>
    </main>
  </div>
  <dialog id="modal"><h2>Nueva serie</h2><p>En la siguiente versión, este botón lanzará el planificador que propondrá y evaluará exactamente cinco libros.</p><button id="closeModal" class="primary">Entendido</button></dialog>
`;

const modal = document.querySelector("#modal");
document.querySelector("#newSeries").addEventListener("click", () => modal.showModal());
document.querySelector("#closeModal").addEventListener("click", () => modal.close());
document.querySelectorAll("[data-book]").forEach(btn => btn.addEventListener("click", () => {
  const book = books.find(b => b.n === Number(btn.dataset.book));
  alert(`${book.title}\nEstado: ${labels[book.state]}`);
}));
