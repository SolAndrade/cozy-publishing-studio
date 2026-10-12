export function sceneGrid(book) {
  const total = book.totalScenes || 40, locked = book.lockedScenes || 0;
  return `<div class="scene-grid">${Array.from({length: total}, (_, i) => {
    const n=i+1, state=n<=locked ? "locked" : "waiting";
    return `<button class="scene-tile ${state}" title="Escena ${n}"><span>${String(n).padStart(2,"0")}</span><small>${state==="locked" ? "ART LOCKED" : "PENDIENTE"}</small></button>`;
  }).join("")}</div>`;
}
