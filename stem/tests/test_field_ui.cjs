/* Real HTTP + full client scripts in a small DOM harness. No rendered-browser claim. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),vm=require('node:vm'),{spawn}=require('node:child_process');
const root=path.resolve(process.argv[2]||'.'),stem=fs.existsSync(path.join(root,'adventure.py'));
class Storage{constructor(){this.items={};}getItem(k){return this.items[k]??null;}setItem(k,v){this.items[k]=String(v);}removeItem(k){delete this.items[k];}}
async function main(){
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'field-ui-'));
 const bootstrap=`import sys,copy\nsys.path.insert(0,${JSON.stringify(root)})\nimport server as s,field_rules as f\ns.init_db(${JSON.stringify(path.join(tmp,'test.sqlite3'))})\nf.die=lambda w,n,label:n\noriginal=s.${stem?'request':'mutate'}\ndef request(d):\n result=original(d)\n if d.get('op')=='create':\n  w=s.fetch(result['code']);p=w['players'][0];a=copy.deepcopy(f.PROFILES['FOE01']);a.update(instance_id='ui:FOE01',max_health=8,health=8,hex=[3,0],state='present',disposition='wary',variant='typical',morale_tested=False,energy=100,injuries=[],ailments=[],initiative=0,present_need='a clear return route')\n  e=dict(id='ui:scene',watch=0,habitat='needle',budget=2,actors=[a],resolved=False,combat=None,declined=[],events=[],loot_paid=False,event='Controlled interface scenario')\n  w['field_sites'][f.site_key(p)]={'encounter':e};s.save(w)\n return result\ns.${stem?'request':'mutate'}=request\nh=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler)\nprint(h.server_port,flush=True)\nh.serve_forever()\n`;
 const host=spawn(process.env.PYTHON||'python3',['-c',bootstrap],{cwd:root});let errors='';host.stderr.on('data',b=>errors+=b);
 try{
  const port=await new Promise((res,rej)=>{host.stdout.once('data',b=>res(Number(String(b).trim())));host.once('error',rej);host.once('exit',c=>rej(Error('host '+c+' '+errors)));});
  const all=[];
  class Element{
   constructor(tag,text=''){this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;this.dataset={};this.attrs={};this.hidden=false;this.disabled=false;this.value='';this.className='';this.style={};this.id='';this.name='';this._text=text;this.checked=false;this.classList={toggle:(x,v)=>{},add:()=>{},remove:()=>{}};all.push(this);}
   get textContent(){return this._text+this.children.map(c=>c.textContent??'').join('');}
   set textContent(v){this._text=String(v);this.children=[];}
   append(...nodes){for(const n of nodes){if(n&&typeof n==='object')n.parentElement=this;this.children.push(n);if(this.tagName==='SELECT'&&!this.value&&n.tagName==='OPTION')this.value=n.value;}}
   replaceChildren(...nodes){this.children=[];this._text='';this.append(...nodes);}
   setAttribute(k,v){this.attrs[k]=String(v);if(k==='class')this.className=v;}
   removeAttribute(k){delete this.attrs[k];}
   after(n){const parent=this.parentElement;if(parent){const i=parent.children.indexOf(this);parent.children.splice(i+1,0,n);n.parentElement=parent;}}
   add(n){this.append(n);if(!this.value)this.value=n.value;}
   get options(){return this.children;}
   click(){assert.equal(this.disabled,false,'click disabled '+this.textContent);return this.onclick?.({preventDefault(){},target:this});}
   requestSubmit(){return this.onsubmit?.({preventDefault(){},target:this});}
  }
  const doc={createElement:tag=>new Element(tag),createElementNS:(ns,tag)=>new Element(tag),createTextNode:s=>new Element('#text',s),getElementById:id=>all.find(n=>n.id===id)||null,querySelectorAll:s=>all.filter(n=>s==='button'?n.tagName==='BUTTON':s==='[data-command]'?!!n.dataset.command:s.startsWith('.')?n.className.split(/\s+/).includes(s.slice(1)):false)};
  const documentRoot=new Element('document'),stack=[documentRoot],voids=new Set(['meta','link','input','img','br','hr','source']);
  const html=fs.readFileSync(path.join(root,'static/index.html'),'utf8');
  for(const m of html.matchAll(/<(\/?)([a-zA-Z][\w:-]*)\b([^>]*)>/g)){
   const [,close,tag,attrs]=m;if(close){if(stack.length>1)stack.pop();continue;}
   const e=new Element(tag);for(const a of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)){const k=a[1],v=a[2]??'';if(k==='class')e.className=v;else if(k.startsWith('data-'))e.dataset[k.slice(5)]=v;else if(['hidden','checked','disabled','required'].includes(k))e[k]=true;else e[k]=v;}
   stack.at(-1).append(e);if(tag==='body')doc.body=e;if(!voids.has(tag))stack.push(e);
  }
  const ids=id=>{const e=doc.getElementById(id);assert.ok(e,'missing '+id);return e;};
  const storage=new Storage();
  function FormData(form){this[Symbol.iterator]=function*(){for(const e of all)if(e.name){let p=e.parentElement;while(p){if(p===form){yield[e.name,e.value];break;}p=p.parentElement;}}};}
  const ctx={document:doc,sessionStorage:storage,localStorage:new Storage(),FormData,Option:function(t,v){const e=new Element('option',t);e.value=v;return e;},fetch:(url,opts)=>fetch(`http://127.0.0.1:${port}${url}`,opts),AbortSignal,Blob,URL,console,setTimeout,clearTimeout,setInterval:()=>0,addEventListener:()=>{}};ctx.window=ctx;
  vm.createContext(ctx);
  const run=name=>vm.runInContext(fs.readFileSync(path.join(root,'static',name),'utf8'),ctx,{filename:name});
  run('creator.js');run('field-guide.js');run('app.js');if(!stem)run('openworld.js');
  if(stem){for(let i=0;i<100&&!ctx.StemCreator.ready;i++)await new Promise(r=>setTimeout(r,10));assert.ok(ctx.StemCreator.ready);ids('name').value='Stem UI Witness';ids('seed').value='field-ui';await ids('join-form').requestSubmit();}
  else{await ctx.Creator.init;const form=ids('create');const name=all.find(e=>e.name==='name'&&e.parentElement?.parentElement===form);assert.ok(name);name.value='Thorns UI Witness';const mode=all.find(e=>e.name==='mode');mode.value='open';await form.requestSubmit();}
  assert.equal(ids('game').hidden,false,'game visible: '+ids('error').textContent);assert.ok(ids('field-guide-panel').textContent.includes('FIELD GUIDE'));
  await ids('start').click();
  const panel=()=>ids('field-guide-panel');
  function findButton(text){const walk=n=>{if(n.tagName==='BUTTON'&&n._text===text)return n;for(const c of n.children){const found=walk(c);if(found)return found;}return null;};const e=walk(panel());assert.ok(e,'missing button '+text+' '+panel().textContent);return e;}
  assert.ok(panel().textContent.includes('Controlled interface scenario'));
  await findButton('DRINK / 1 WATER').click();assert.ok(panel().textContent.includes('ACTIVE CYCLE 1'));
  await findButton('BEGIN LOCAL TURNS').click();assert.ok(panel().textContent.includes('ROUND 1'));
  await findButton('APPROACH / 1 AP').click();await findButton('APPROACH / 1 AP').click();
  await findButton('STAFF / 3 AP').click();assert.ok(panel().textContent.includes('ENCOUNTER CLOSED'));
  await findButton('RECOVER ABANDONED MATERIAL / ONCE').click();
  assert.ok(!panel().textContent.includes('RECOVER ABANDONED MATERIAL / ONCE'));
  assert.ok(panel().textContent.includes('staff')&&panel().textContent.includes('98/100'));
  await findButton('REPAIR FIELD STAFF / 1 SCRAP').click();assert.ok(panel().textContent.includes('100/100'));
  await findButton('SPEND A WATCH / 4 CYCLES').click();assert.ok(panel().textContent.includes('ACTIVE CYCLE 8'));
  await vm.runInContext('poll()',ctx);assert.equal(ids('error').textContent,'');
  console.log(JSON.stringify({game:stem?'Stem':'Thorns',ui_flows:10,checks:['creator','start','provision cycle','fixed turn order','hex approach','AP attack','finite salvage','wear and repair','shared watch','poll persistence'],renderer:'DOM harness with real HTTP; graphical browser unavailable'}));
 }finally{host.kill('SIGTERM');fs.rmSync(tmp,{recursive:true,force:true});}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
