const C='mcp-v3';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys()
    .then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET' || new URL(req.url).origin!==location.origin) return;
  e.respondWith(
    fetch(req).then(res=>{ const cl=res.clone(); caches.open(C).then(c=>c.put(req,cl)); return res; })
      .catch(()=>caches.match(req).then(r=>r||caches.match('index.html')))
  );
});
