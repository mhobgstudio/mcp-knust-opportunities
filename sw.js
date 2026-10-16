const C='mcp-v1';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET' || new URL(req.url).origin!==location.origin) return;
  e.respondWith(caches.open(C).then(c=>c.match(req).then(r=>r||fetch(req).then(res=>{c.put(req,res.clone());return res;}).catch(()=>c.match('index.html')))));
});
