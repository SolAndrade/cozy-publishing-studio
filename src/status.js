import { api } from "./api.js";

export async function backendStatus(){
  if(!api.enabled) return {connected:false,label:"Backend no conectado",providers:[],secrets:[]};
  try{
    const data=await api.request("/api/status");
    return {connected:true,label:data.production_ready?"Producción real lista":"Backend conectado · configuración pendiente",...data};
  }catch(error){
    return {connected:false,label:"Backend inaccesible",error:error.message,providers:[],secrets:[]};
  }
}

export function statusPanel(status){
  const rows=(status.providers||[]).map(p=>`<div class="status-row"><span>${p.role}</span><b class="status-${p.state.toLowerCase()}">${p.state}</b><small>${p.provider}</small></div>`).join("");
  const missing=(status.secrets||[]).filter(s=>!s.configured);
  return `<section class="system-status"><div><span class="eyebrow">SISTEMA</span><h2>${status.label}</h2></div>${rows||'<p>Configura la URL privada del backend para ver el estado real.</p>'}${missing.length?`<p class="status-warning">Faltan ${missing.length} secret(s) de producción en el backend.</p>`:""}</section>`;
}
