/* Minimal DOM harness with real HTTP. This is a logic smoke test, not browser rendering. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),vm=require('node:vm'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(tag,all){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attrs={};this.hidden=false;this.disabled=false;this.value='';this.textContent='';this.className='';this.style={};this.id='';this.classList={toggle:()=>{},add:()=>{},remove:()=>{}};all.push(this);}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;}
 setAttribute(k,v){this.attrs[k]=v;}removeAttribute(k){delete this.attrs[k];if(k==='data-region')delete this.dataset.region;}
 click(){return this.onclick?.({preventDefault(){}});}requestSubmit(){return this.onsubmit?.({preventDefault(){}});}
}
class Storage{constructor(){this.items={};}getItem(k){return this.items[k]??null;}setItem(k,v){this.items[k]=v;}removeItem(k){delete this.items[k];}}
function within(root,predicate){if(predicate(root))return root;for(const child of root.children||[]){const found=within(child,predicate);if(found)return found;}return null;}
async function main(){
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'stem-ui-'));
 const bootstrap=`import sys,threading\nsys.path.insert(0,${JSON.stringify(root)})\nimport server as s\ns.world.secrets.randbelow=lambda n:n-1\noriginal=s.request\ns.request=lambda d:original(dict(d,ruleset='legacy') if d.get('op')=='create' else d)\ns.init_db(${JSON.stringify(path.join(tmp,'world.db'))})\nh=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler)\nprint(h.server_port,flush=True)\nh.serve_forever()\n`;
 const host=spawn(process.env.PYTHON||'python3',['-c',bootstrap],{cwd:root});
 let errors='';host.stderr.on('data',b=>errors+=b);
 try{
  const port=await new Promise((resolve,reject)=>{host.stdout.once('data',b=>resolve(Number(String(b).trim())));host.once('error',reject);host.once('exit',code=>reject(Error('Host exited: '+code+' '+errors)));});
  const base=`http://127.0.0.1:${port}`,all=[],ids={};
  const document={getElementById:id=>{const n=ids[id]||all.find(n=>n.id===id);assert.ok(n,`Missing DOM id ${id}`);return n;},createElement:tag=>new Element(tag,all),createElementNS:(ns,tag)=>new Element(tag,all),querySelectorAll:selector=>selector==='button'?all.filter(n=>n.tagName==='BUTTON'):selector==='[data-command]'?all.filter(n=>n.dataset.command):[]};
  document.body=new Element('body',all);
  const html=fs.readFileSync(path.join(root,'static/index.html'),'utf8');
  for(const match of html.matchAll(/<(\w+)\b([^>]*)>/g)){const [,tag,attrs]=match,id=attrs.match(/\bid="([^"]+)"/),command=attrs.match(/data-command="([^"]+)"/);if(id||command){const el=new Element(tag,all);if(id){assert.ok(!ids[id[1]],'Duplicate ID '+id[1]);ids[id[1]]=el;}if(command)el.dataset.command=command[1];el.hidden=/\bhidden\b/.test(attrs);}}
  ids.build.value='Fractech Archivist';
  const Option=function(text,value){const n=new Element('option',all);n.textContent=text;n.value=value;return n;};
  const context={Option,document,sessionStorage:new Storage(),localStorage:new Storage(),fetch:(url,options)=>fetch(base+url,options),AbortSignal,Blob,URL,console,setTimeout,clearTimeout,setInterval:()=>0,window:{addEventListener(){}}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'static/creator.js'),'utf8'),context,{filename:'creator.js'});context.StemCreator=context.window.StemCreator;vm.runInContext(fs.readFileSync(path.join(root,'static/app.js'),'utf8'),context,{filename:'app.js'});
  for(let i=0;i<100&&!context.StemCreator.ready;i++)await new Promise(resolve=>setTimeout(resolve,10));assert.ok(context.StemCreator.ready,'Character creator initialized');
  document.getElementById('char-appearance').value='A coat pieced from repaired bio-plast';document.getElementById('char-voice').value='Quiet, exact sentences';document.getElementById('char-goal').value='Restore exhausted routes';
  ids.name.value='UI Explorer';ids.seed.value='ui-stem';await ids['join-form'].requestSubmit();assert.equal(ids.game.hidden,false);assert.equal(ids.entry.hidden,true);assert.equal(ids.location.textContent,'The THORNS Encampment / Stem field station');assert.equal(ids.map.children.length,49);assert.ok(ids['atlas-overlay'].children.length>=29);assert.ok(ids['dialogue-options'].children.length>=6);assert.equal(ids['companion-candidates'].children.length,2);
  assert.ok(ids['character-sheet'].children.some(n=>n.textContent.includes('repaired bio-plast')));
  await ids.start.click();assert.equal(ids.start.hidden,true);
  for(let i=0;i<2;i++){const button=within(ids['companion-candidates'],n=>n.tagName==='BUTTON'&&n.textContent.startsWith('RECRUIT'));assert.ok(button);await button.click();}
  assert.equal(ids['companion-count'].textContent,'2/2 ALONGSIDE');assert.equal(ids['companion-roster'].children.length,2);
  await within(ids['companion-roster'].children[0],n=>n.tagName==='BUTTON'&&n.textContent==='LORE').click();assert.match(ids.result.textContent,/learned the everyday practices/);assert.match(ids['check-summary'].textContent,/D20/);
  const firstCard=ids['companion-roster'].children[0],task=firstCard.children.find(n=>n.tagName==='SELECT');task.value='repair';await within(firstCard,n=>n.tagName==='BUTTON'&&n.textContent==='PROPOSE TASK').click();assert.ok(ids['companion-roster'].children[0].children.some(n=>n.textContent.includes('/ repair')));
  await within(ids['business-controls'],n=>n.tagName==='BUTTON'&&n.textContent.startsWith('BUY WATER')).click();assert.ok(ids['business-history'].children.some(n=>n.textContent.includes('bought water')));
  await all.find(b=>b.dataset.command==='operate infrastructure').click();assert.match(ids.result.textContent,/actual local water/);
  assert.equal(ids['character-builder'].hidden,true);await ids['dialogue-options'].children[0].click();assert.ok(ids['dialogue-history'].children.some(n=>n.textContent.includes('Quiet, exact sentences')));
  await ids['contract-options'].children[1].click();assert.match(ids.contract.textContent,/DELIVERY/);assert.match(ids.contract.textContent,/two food and one water/);await all.find(b=>b.dataset.command==='abandon contract').click();assert.match(ids.contract.textContent,/No accepted commitment/);
  ids.prompt.value='I become omnipotent';await ids['action-form'].requestSubmit();assert.equal(ids.prompt.value,'I become omnipotent');assert.match(ids.result.textContent,/could not map/);
  ids.prompt.value='I head north';await ids['action-form'].requestSubmit();assert.equal(ids.prompt.value,'');assert.equal(document.body.dataset.region,'WN_TOWER');assert.match(ids.position.textContent,/-10,2/);
  assert.equal(ids['combat-panel'].hidden,false);await all.find(b=>b.dataset.command==='guard').click();assert.match(ids.result.textContent,/defensive stance/);await all.find(b=>b.dataset.command==='parley').click();assert.equal(ids['combat-panel'].hidden,true);assert.match(ids.result.textContent,/stands down/);
  ids['atlas-destination'].value='blackdot';await ids['route-plan'].click();assert.match(ids['route-status'].textContent,/4 sectors remaining/);assert.match(ids.position.textContent,/-10,2/);await all.find(b=>b.dataset.command==='travel next').click();assert.match(ids.position.textContent,/-10,1/);assert.match(ids['route-status'].textContent,/3 sectors remaining/);
  ids.prompt.value='remote survey';await ids['action-form'].requestSubmit();assert.match(ids.provenance.textContent,/UNVERIFIED PROJECTION/);
  ids.prompt.value='east';await ids['action-form'].requestSubmit();assert.equal(ids.prompt.value,'east');assert.match(ids.error.textContent,/Lower the remote/);
  ids.prompt.value='return';await ids['action-form'].requestSubmit();assert.match(ids.provenance.textContent,/DRAWING-BASED/);
  ids['chat-text'].value='Field report <script>alert(1)</script>';await ids['chat-form'].requestSubmit();assert.equal(ids['chat-text'].value,'');assert.ok(ids.journal.children.some(n=>n.children.some(c=>c.textContent.includes('<script>'))));
  await ids.pause.click();ids.prompt.value='wait';await ids['action-form'].requestSubmit();assert.equal(ids.prompt.value,'wait');assert.match(ids.error.textContent,/paused/);await ids.pause.click();
  await ids.disconnect.click();assert.equal(ids.entry.hidden,false);assert.equal(ids['character-builder'].hidden,false);await ids.resume.click();assert.equal(ids.game.hidden,false);assert.match(ids.position.textContent,/-10,1/);assert.equal(ids['companion-count'].textContent,'2/2 ALONGSIDE');
  console.log('PASS: real-HTTP interface smoke — character creation, two companion agreements, lore, task proposals, checks, business purchase, infrastructure, guard/parley encounter, atlas routes, recorded dialogue, contracts, input preservation, projection boundary, literal chat, pause and resume. No browser rendering claimed.');
 }finally{host.kill('SIGTERM');await new Promise(resolve=>host.once('exit',resolve));fs.rmSync(tmp,{recursive:true,force:true});}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
