const express=require('express'),http=require('http'),{Server}=require('socket.io');
const app=express(),srv=http.createServer(app),io=new Server(srv);
app.get('/', (q, r) => r.sendFile(__dirname + '/public/crash.html'));
app.use(express.static('public'));
const peers={},events=[],R=+process.env.RADIUS||500; // geofence radius (m)
const hav=(a,b)=>{const r=Math.PI/180,x=Math.sin((b.lat-a.lat)*r/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin((b.lon-a.lon)*r/2)**2;return 12742000*Math.asin(Math.sqrt(x))};
io.on('connection',s=>{
  s.on('telemetry',t=>{peers[s.id]={...peers[s.id],...t,id:s.id}});
  s.on('brake',e=>{
    peers[s.id]={...peers[s.id],...e,id:s.id};let n=0;
    for(const [id,p] of Object.entries(peers)){if(id===s.id)continue;const d=hav(e,p);if(d<=R){io.to(id).emit('alert',{...e,dist:d});n++}}
    events.push({t:new Date().toISOString(),from:e.name,prob:e.prob,decel:e.decel,notified:n});
    console.log(`BRAKE from ${e.name} p=${e.prob.toFixed(2)} decel=${e.decel.toFixed(1)} -> ${n} vehicle(s)`);
  });
  s.on('crash',e=>{peers[s.id]={...peers[s.id],...e,id:s.id};let n=0;
    for(const [id,p] of Object.entries(peers)){if(id===s.id)continue;const d=hav(e,p);if(d<=R){io.to(id).emit('crash',{...e,dist:d,cid:s.id});n++}}
    events.push({t:new Date().toISOString(),type:'CRASH',from:e.name,g:e.g,lat:e.lat,lon:e.lon,notified:n});console.log(`CRASH from ${e.name} g=${(e.g/9.8).toFixed(1)} -> ${n} vehicle(s)`)});
  s.on('clear',()=>{io.emit('cleared',{cid:s.id});console.log('crash cleared by victim')});
  s.on('disconnect',()=>delete peers[s.id]);
});
setInterval(()=>io.emit('peers',Object.values(peers)),1000);
app.get('/api/events',(q,r)=>r.json(events));
srv.listen(process.env.PORT||3000,()=>console.log('BrakeAlert on :'+(process.env.PORT||3000)));
