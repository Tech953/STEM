'use strict';
const $=id=>document.getElementById(id);
const make=(tag,text='',cls='')=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
let session=null,state=null,busy=false,suggestion=null,catalog=null,loadedCharacterId=null;
try{session=JSON.parse(sessionStorage.getItem('stem-session'));$('resume').hidden=!localStorage.getItem('stem-session');}catch{}
let crt=localStorage.getItem('stem-crt')!=='off';
function showCRT(){document.body.classList.toggle('no-crt',!crt);$('crt').textContent=`CRT ${crt?'ON':'OFF'}`;}showCRT();
$('crt').onclick=()=>{crt=!crt;localStorage.setItem('stem-crt',crt?'on':'off');showCRT();};
function error(msg){$('error').textContent=msg||'';}
async function api(op,data={}){const response=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...session,op,...data}),signal:AbortSignal.timeout(op==='narrate'||op==='interpret'?55000:12000)});const body=await response.json();if(!response.ok)throw Error(body.error||'The host could not complete that request.');return body;}
function lock(flag){busy=flag;document.querySelectorAll('button').forEach(b=>b.disabled=flag||b.dataset.fieldDisabled==='true');}
async function poll(){if(!session||busy)return;try{const next=await api('state');if(!state||next.revision!==state.revision){state=next;render();}$('connection').textContent='HOST CONNECTED';}catch(e){$('connection').textContent='RECONNECTING';error(e.message);}}
async function action(op,data={}){if(busy)return false;lock(true);error('');try{const answer=await api(op,{revision:state.revision,...data});if(answer.left){disconnect();return true;}state=answer.state;render();if(answer.result){$('response').hidden=false;$('result').textContent=answer.result.text;$('roll').textContent=answer.result.mechanics||'';}return !answer.result||answer.result.intent!==null;}catch(e){error(e.message);return false;}finally{lock(false);await poll();}}
function disconnect(){session=null;state=null;loadedCharacterId=null;sessionStorage.removeItem('stem-session');$('game').hidden=true;$('entry').hidden=false;$('character-builder').hidden=false;$('character-apply').hidden=true;$('connection').textContent='DISCONNECTED';document.body.removeAttribute('data-region');document.body.classList.remove('remote');$('resume').hidden=!localStorage.getItem('stem-session');}
function render(){if(!state)return;const s=state,p=s.me,c=s.location;
 $('character-builder').hidden=s.started;$('character-apply').hidden=s.started;
 if(loadedCharacterId!==p.id&&catalog){if(!s.started)StemCreator.set(s.character_sheet.role,s.character_sheet);loadedCharacterId=p.id;}
 $('entry').hidden=true;$('game').hidden=false;document.body.dataset.region=c.region;document.body.classList.toggle('remote',p.remote);
 $('world-code').textContent=`WORLD ${s.code} · ${s.players.length}/6 EXPLORERS`;$('clock').textContent=`CYCLE ${s.tick} / ${s.phase.toUpperCase()} / ${s.paused?'PAUSED':s.season.toUpperCase()}`;$('weather').textContent=s.weather.toUpperCase();
 $('start').hidden=s.started||s.host!==session.id;$('pause').hidden=!s.started||s.host!==session.id;$('pause').textContent=s.paused?'RESUME CLOCK':'PAUSE CLOCK';
 $('region').textContent=p.remote?'NULL_FIELD.OMNI / REMOTE PERCEPT':c.region;$('location').textContent=p.remote?'Beyond the received horizon':c.title;
 $('provenance').textContent=p.remote?'UNVERIFIED PROJECTION · BODY REMAINS AT CURRENT COORDINATES':(s.atlas?'DRAWING-BASED GEOGRAPHY · DOCUMENTED LANDMARKS / GENERATED LOCAL LIFE':'LEGACY GENERATED SITE · ORIGINAL QUADRANT LAYOUT');$('description').textContent=s.description;
 $('condition-row').replaceChildren(...[`Moisture ${c.moisture}`,`Growth ${c.growth}`,`Stability ${c.stability}`,`AETHER ${c.aether}`,`Shelter ${c.shelter}`,`Fauna index ${c.fauna}`,s.succession].map(x=>make('span',x,'condition')));
 $('opportunities').replaceChildren(...s.opportunities.map(o=>{const n=make('div'),b=make('button',o.command.toUpperCase(),'quiet');b.onclick=()=>action('act',{text:o.command});n.append(make('p',o.text),b);return n;}));
 renderAtlas(s);renderAdventure(s);renderSystems(s);if(window.FieldGuide)FieldGuide.render(s,session.id,action,true);
 $('help').textContent=s.help;$('me').replaceChildren(make('strong',p.name),make('small',`${p.build} · XP ${p.xp} · Karma ${p.karma}`));
 $('vitals').replaceChildren();for(const [key,label]of [['health','HEALTH'],['energy','ENERGY'],['thirst','THIRST'],['food_need','HUNGER'],['sleep','SLEEP DEBT']]){const v=make('div','','vital'),l=make('label'),m=document.createElement('meter');l.append(make('span',label),make('span',`${p[key]}/100`));m.min=0;m.max=100;m.value=p[key];m.setAttribute('aria-label',label);v.append(l,m);$('vitals').append(v);}
 $('inventory').textContent=Object.entries(p.inventory).map(([k,v])=>`${k.toUpperCase()} ${v}`).join(' · ');
  $('map').replaceChildren();for(const t of s.map){const own=t.x===p.pos[0]&&t.y===p.pos[1],symbol=own?'◎':t.players.length?'●':t.shelter?'⌂':t.known?'·':t.revealed?(t.passable===false?'×':'◦'):'?';const cell=make('div',symbol,`map-cell ${t.revealed?'':'unknown'} ${t.revealed&&!t.known?'scouted':''} ${t.passable===false?'blocked':''} ${t.players.length?'occupied':''}`);const label=`${t.x},${t.y}: ${t.title}${t.players.length?' / '+t.players.join(', '):''}`;cell.title=label;cell.setAttribute('aria-label',label);$('map').append(cell);}
  $('position').textContent=`[${p.pos}] · ${s.discovered} recorded sites\n◎ You · ● Party · ⌂ Shelter · ◦ Scouted · × Blocked · ? Unknown\nOne step = one abstract survey sector.`;
 $('party').replaceChildren(...s.players.map(q=>{const n=make('div',q.name+(q.id===s.host?' / HOST':''),'party-member');n.append(make('small',`${q.build} · [${q.pos}]${q.remote?' · remote observation':''}`));return n;}));
 $('actors').replaceChildren(...(s.actors.length?s.actors.map(a=>make('p',`${a.name} / ${a.role}\n${a.activity} · needs ${a.need}`)):[make('p','No traveler is presently here.')]));
 $('contract').textContent=p.contract?`${(p.contract.kind||'survey').toUpperCase()} · ${p.contract.destination||'field target'} [${p.contract.target}]\nFor ${p.contract.faction}. Reward: ${p.contract.reward}.\n${!p.contract.kind?'At the target, type survey.':p.contract.kind==='restoration'?'Complete a successful repair here, then fulfill.':p.contract.kind==='delivery'?'Carry two food and one water; fulfill at the target.':'At the target, type fulfill.'}`:'No accepted commitment. Review the local board when ready.';
 $('contract-fulfill').onclick=()=>action('act',{text:p.contract&&!p.contract.kind?'survey':'fulfill'});
 $('contract-route').hidden=!s.atlas||!p.contract;
 $('reputation').replaceChildren(...Object.entries(s.reputation).map(([k,v])=>make('div',`${k} · shared ${v>=0?'+':''}${v} · personal ${p.personal_reputation[k]||0}`,'rep')));
 $('journal').replaceChildren(...s.journal.slice(-20).reverse().map(j=>{const n=make('div','',`journal-item ${j.kind}`);n.append(make('small',`CYCLE ${j.tick} / ${j.kind.toUpperCase()}${j.coord?' / ['+j.coord+']':''}`),make('div',j.text));return n;}));
 $('interpret-wrap').hidden=!s.narrator_enabled;$('narrate').hidden=!s.narrator_enabled;$('narrator-note').textContent=s.narrator_enabled?'A local language model is configured on this host.':'No local model configured. The scene above is generated by Stem’s state-driven procedural narrator.';
 $('submit-action').textContent=s.paused?'WORLD PAUSED':s.started?'ACT →':'WAITING FOR HOST';
 if(p.last_result&&$('response').hidden){$('response').hidden=false;$('result').textContent=p.last_result;$('roll').textContent=p.last_action?.mechanics||'';}
}
$('join-form').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true);error('');try{const code=$('code').value.trim(),result=await api(code?'join':'create',{name:$('name').value,build:StemCreator.role(),character:StemCreator.read(),code,seed:$('seed').value});session=result;sessionStorage.setItem('stem-session',JSON.stringify(result));localStorage.setItem('stem-session',JSON.stringify(result));state=await api('state');render();$('connection').textContent='HOST CONNECTED';}catch(e){error(e.message);}finally{lock(false);}};
$('resume').onclick=async()=>{try{session=JSON.parse(localStorage.getItem('stem-session'));loadedCharacterId=null;sessionStorage.setItem('stem-session',JSON.stringify(session));state=null;await poll();}catch(e){error(e.message);}};
$('start').onclick=()=>action('start');$('pause').onclick=()=>action('pause');$('disconnect').onclick=disconnect;
$('leave').onclick=async()=>{if(await action('leave')){localStorage.removeItem('stem-session');$('resume').hidden=true;}};
$('action-form').onsubmit=async e=>{e.preventDefault();const text=$('prompt').value.trim();if(text&&await action('act',{text})){$('prompt').value='';suggestion=null;$('confirm-intent').hidden=true;}};
$('prompt').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('action-form').requestSubmit();}};
$('prompt').oninput=()=>{suggestion=null;$('confirm-intent').hidden=true;};
for(const command of ['look','inspect the habitat','forage','collect water','repair the habitat','plant a seed','wait']){const b=make('button',command.toUpperCase());b.type='button';b.onclick=()=>action('act',{text:command});$('quick').append(b);}
document.querySelectorAll('[data-command]').forEach(b=>b.onclick=()=>action('act',{text:b.dataset.command}));
$('chat-form').onsubmit=async e=>{e.preventDefault();const text=$('chat-text').value;if(await action('chat',{text}))$('chat-text').value='';};
$('export').onclick=async()=>{try{const data=await api('export'),blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='Stem-field-journal.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){error(e.message);}};
$('narrate').onclick=async()=>{if(busy)return;lock(true);error('');$('model-prose').textContent='The local model is composing a scene…';try{const r=await api('narrate');$('model-prose').textContent=`${r.label} / cycle ${r.tick}\n\n${r.prose}`;}catch(e){$('model-prose').textContent='';error(e.message);}finally{lock(false);await poll();}};
$('interpret').onclick=async()=>{const text=$('prompt').value.trim();if(busy||!text)return;lock(true);error('');try{const r=await api('interpret',{text});suggestion={text,intent:r.intent};$('confirm-intent').textContent=`REVIEWED: TRY ${r.intent.action.toUpperCase()} ${r.intent.target.toUpperCase()} →`;$('confirm-intent').hidden=false;}catch(e){error(e.message);}finally{lock(false);await poll();}};
$('confirm-intent').onclick=async()=>{if(!suggestion)return;if(await action('act',suggestion)){suggestion=null;$('confirm-intent').hidden=true;$('prompt').value='';}};
fetch('/catalog').then(r=>{if(!r.ok)throw Error('Cannot load character creation.');return r.json();}).then(c=>{catalog=c;StemCreator.init(c.characters);const update=()=>{$('build-note').textContent=Object.entries(c.characters.presets[StemCreator.role()].attributes).map(([k,v])=>`${k.toUpperCase()} ${v}`).join(' · ');};const change=$('build').onchange;$('build').onchange=()=>{change();update();};update();if(state)render();}).catch(e=>error(e.message));

poll();setInterval(poll,4000);
window.addEventListener('unhandledrejection',e=>error('The interface could not complete an operation: '+(e.reason?.message||e.reason)));

function renderAtlas(s){
 $('atlas-panel').hidden=!s.atlas;if(!s.atlas)return;
 const a=s.atlas;$('atlas-note').textContent=a.note;
 const selected=$('atlas-destination').value;$('atlas-destination').replaceChildren(...a.landmarks.map(l=>new Option(l.name,l.id)));if(a.landmarks.some(l=>l.id===selected))$('atlas-destination').value=selected;
 const view=$('atlas-overlay');view.replaceChildren();const ns='http://www.w3.org/2000/svg',project=pos=>[40+(pos[0]+18)*22,40+(pos[1]+12)*22];
  const revealed=new Set((a.revealed||[]).map(pos=>pos.join(','))),fog=[];
  for(let y=-12;y<=12;y++)for(let x=-18;x<=18;x++)if(!revealed.has(`${x},${y}`)){const [cx,cy]=project([x,y]);fog.push(`M${cx-11} ${cy-11}h22v22h-22z`);}
  const cover=document.createElementNS(ns,'path');cover.setAttribute('d',fog.join(''));cover.setAttribute('class','atlas-fog');const coverTitle=document.createElementNS(ns,'title');coverTitle.textContent='Unexplored sectors';cover.append(coverTitle);view.append(cover);
  let segment=[];const drawRoute=()=>{if(segment.length>1){const route=document.createElementNS(ns,'polyline');route.setAttribute('points',segment.join(' '));route.setAttribute('class','atlas-route');view.append(route);}segment=[];};
  for(const pos of [s.me.pos,...a.route]){if(revealed.has(pos.join(',')))segment.push(project(pos).join(','));else drawRoute();}drawRoute();
 for(const l of a.landmarks){const point=document.createElementNS(ns,'circle'),title=document.createElementNS(ns,'title'),[x,y]=project(l.pos);point.setAttribute('cx',x);point.setAttribute('cy',y);point.setAttribute('r',8);point.setAttribute('class','atlas-landmark');point.setAttribute('role','button');point.setAttribute('tabindex','0');point.setAttribute('aria-label','Plan route to '+l.name);title.textContent=l.name+' / '+l.confidence;point.append(title);point.onclick=()=>{$('atlas-destination').value=l.id;showAtlasSelection();action('act',{text:'go to '+l.name});};point.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();point.onclick();}};view.append(point);}
 if(s.me.contract){const point=document.createElementNS(ns,'circle'),[cx,cy]=project(s.me.contract.target);point.setAttribute('cx',cx);point.setAttribute('cy',cy);point.setAttribute('r',11);point.setAttribute('class','atlas-commitment');point.setAttribute('role','button');point.setAttribute('tabindex','0');point.setAttribute('aria-label','Plan route to your commitment');point.onclick=()=>action('act',{text:'go to commitment'});point.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();point.onclick();}};view.append(point);}
 const marker=document.createElementNS(ns,'circle'),[x,y]=project(s.me.pos);marker.setAttribute('cx',x);marker.setAttribute('cy',y);marker.setAttribute('r',6);marker.setAttribute('class','atlas-player');view.append(marker);
 $('route-status').textContent=a.destination?`${a.destination} · ${a.route.length} sectors remaining / ${a.route_cycles} estimated travel cycles.`:'Select a gold landmark or named destination to plan a route.';showAtlasSelection();
}
function showAtlasSelection(){if(!state?.atlas)return;const l=state.atlas.landmarks.find(l=>l.id===$('atlas-destination').value);$('atlas-location-description').textContent=l?`${l.name} [${l.pos}] · ${l.services.join(', ')}\n${l.description}\nSource: ${l.source}. Confidence: ${l.confidence}.`:'';}
$('atlas-destination').onchange=showAtlasSelection;
$('route-plan').onclick=()=>{const l=state?.atlas?.landmarks.find(l=>l.id===$('atlas-destination').value);if(l)return action('act',{text:'go to '+l.name});};
$('character-apply').onclick=async()=>{try{await action('character',{build:StemCreator.role(),character:StemCreator.read()});}catch(e){error(e.message);}};
function renderAdventure(s){
 const p=s.me,ch=s.character_sheet,button=(label,command)=>{const b=make('button',label,'quiet');b.onclick=()=>action('act',{text:command});return b;};
 $('dialogue-options').replaceChildren(...s.dialogue_options.map(o=>button(o.label,o.command)));
 $('dialogue-history').replaceChildren(...p.dialogue_log.slice(-12).reverse().map(d=>make('p',`Cycle ${d.tick} · ${d.location} · ${d.npc} / ${d.topic}\n${d.response}`)));
 $('contract-options').replaceChildren(...(s.atlas?s.contract_options:[{label:'Accept survey commission',command:'accept a survey contract'}]).map(o=>button(o.label,o.command)));
 const serviceCommands={register:'register',mods:'study',lesson:'study',care:'clinic',medical_contract:'clinic',free_provision:'provision'};
 $('services').replaceChildren(button('FIELD TREATMENT / medkit','treat'),...s.local_services.filter(k=>serviceCommands[k]).map(k=>button(k.replaceAll('_',' ').toUpperCase(),serviceCommands[k])));
 $('equipment').replaceChildren();for(const [id,m]of Object.entries(catalog?.characters.equipment||{}))$('equipment').append(button(`${ch.loadout.includes(id)?'REMOVE':'INSTALL / 2 SCRAP'} ${m.label}`,`${ch.loadout.includes(id)?'remove':'install'} ${id}`));
 const lines=[`${ch.role} · ${ch.pronouns||'pronouns unspecified'} · ${ch.age||'age unspecified'}`,`${ch.origin} · ${ch.form} · ${ch.affiliation} · ${ch.affinity}`,Object.entries(ch.attributes).map(([k,v])=>`${k.toUpperCase()} ${v}`).join(' / '),`Appearance: ${ch.appearance||'not yet described'}`,`Voice: ${ch.voice||'not yet described'}`,`Mannerisms: ${ch.mannerisms||'not yet described'}`,`Biography: ${ch.bio||'not yet described'}`,`Goal: ${ch.goal||'not yet stated'}`,`Boundaries: ${ch.boundary||'not yet stated'}`,`Training: ${Object.entries(ch.skills).map(([k,v])=>(catalog?.characters.skills[k]?.label||k)+' '+v).join('; ')||'none'}`,`Verified field credentials: ${ch.credentials.join(', ')||'none'}`,`Loadout: ${ch.loadout.join(', ')||'none'} · care benefit ${ch.care_benefits}/3`,`Injuries: ${ch.injuries.join(', ')||'none'} · ailments: ${ch.ailments.join(', ')||'none'}`];
 $('character-sheet').replaceChildren(...lines.map(l=>make('p',l)));
}

function renderSystems(s){
 const p=s.me,check=p.last_check,command=(label,text)=>{const b=make('button',label,'quiet');b.type='button';b.onclick=()=>action('act',{text});return b;};
 $('check-summary').textContent=check?`${check.grade.toUpperCase()} / ${check.skill} · D20 ${check.die} + ${check.bonus} vs ${check.dc}\n${check.faction}: reputation ${check.reputation>=0?'+':''}${check.reputation} · context ${check.context>=0?'+':''}${check.context} · trust ${check.trust} · attitude ${check.attitude} · companions +${check.support}\n${check.reasons.join(' / ')||'Ordinary local conditions'}`:'Interaction checks appear after your first action.';
 $('check-history').replaceChildren(...p.check_log.slice(-8).reverse().map(c=>make('p',`Cycle ${c.tick} / ${c.action} / ${c.skill}: ${c.grade}. ${c.die} + ${c.bonus} vs ${c.dc}. Faction ${c.faction}. Context ${c.context}, standing ${c.reputation}, support ${c.support}.`)));
 const companions=s.companions;$('companion-count').textContent=`${companions.roster.length}/${companions.limit} ALONGSIDE`;
 function profile(a,own){
  const card=make('section','','companion-card');card.append(make('h3',a.name),make('p',`${a.role} · ${a.faction}\n${a.attitude_label.toUpperCase()} ${a.attitude}/100 · [${a.pos}]`),make('p',`${a.health} health / ${a.energy} energy · ${a.engagement.phase.toUpperCase()} / ${a.engagement.task}`));
  card.append(make('p',a.character.appearance,'subtle'),make('p',Object.entries(a.inventory).map(([k,v])=>`${k} ${v}`).join(' · '),'subtle'));
  const designation=make('details');designation.append(make('summary','FULL CHARACTER DESIGNATION'));
  for(const text of [`ID: ${a.id}`,`${a.character.pronouns} · ${a.character.form} · ${a.character.origin}`,Object.entries(a.character.attributes).map(([k,v])=>`${k.toUpperCase()} ${v}`).join(' / '),`Training: ${Object.entries(a.character.skills).map(([k,v])=>`${k} ${v}`).join('; ')}`,`Experience: ${a.experience} · verified field credentials: ${a.credentials.join(', ')||'none'} · equipment: ${a.equipment.join(', ')||'none'}`,`Voice: ${a.character.voice}. Mannerisms: ${a.character.mannerisms}.`,`Goal: ${a.character.goal}`,`Boundary: ${a.character.boundary}`,`Items: ${a.items.map(i=>i.name+' / '+i.effect).join('; ')}`,`Faction engagement: ${Object.entries(a.reputation).map(([k,v])=>k+' '+v).join('; ')}`,`Conditions: ${[...a.injuries,...a.ailments].join(', ')||'none'}`])designation.append(make('p',text));
  designation.append(make('h4','LORE'),...a.character.bio.split('\n\n').map(t=>make('p',t)));
  designation.append(make('h4','CONTRACT VIABILITY'),...Object.entries(a.contract_viability).map(([k,v])=>make('p',`${k.toUpperCase()}: ${v.viable?'READY':'LIMITED'} · training ${v.training}${v.preferred?' · preferred':''} · ${v.reasons.join(', ')}`)));
  card.append(designation);
  const history=make('details');history.append(make('summary','ENGAGEMENT AND CONVERSATION RECORD'),...a.engagement.events.slice(-6).reverse().map(e=>make('p',`Cycle ${e.tick}: ${e.text}`)),...a.memory.slice(-3).reverse().map(m=>make('p',`${m.speaker} / ${m.topic}: ${m.response}`)));card.append(history);
  if(own||a.available){const topics=make('div','','quick');for(const topic of companions.topics)topics.append(command(topic.toUpperCase(),`speak with ${a.id} about ${topic}`));card.append(topics);}
  if(own){
   const task=make('select');task.setAttribute('aria-label','Task for '+a.name);task.append(...companions.tasks.map(t=>new Option(t,t)));task.value=a.engagement.task;
   const taskButton=make('button','PROPOSE TASK','quiet');taskButton.onclick=()=>action('act',{text:`task ${a.id} ${task.value}`});card.append(task,taskButton);
   const supply=make('select');supply.setAttribute('aria-label','Supply for '+a.name);supply.append(...['water','food','scrap','seed','medkit'].map(t=>new Option(t,t)));supply.value='water';
   const give=make('button','SHARE ONE','quiet'),ask=make('button','REQUEST ONE','quiet');give.onclick=()=>action('act',{text:`share ${a.id} ${supply.value}`});ask.onclick=()=>action('act',{text:`request ${a.id} ${supply.value}`});card.append(supply,give,ask,command('FIELD CARE / MEDKIT',`care for ${a.id}`),command('RELEASE AGREEMENT',`dismiss ${a.id}`));
  }else if(a.available)card.append(command('RECRUIT / 1 FOOD + 1 WATER',`recruit ${a.id}`));
  else card.append(make('p','Already engaged with another expedition.','subtle'));
  return card;
 }
 $('companion-roster').replaceChildren(...(companions.roster.length?companions.roster.map(a=>profile(a,true)):[make('p','No active companion agreements. Review nearby NPCs below.','subtle')]));
 $('companion-candidates').replaceChildren(...(companions.candidates.length?companions.candidates.map(a=>profile(a,false)):[make('p','No unengaged traveler is nearby. Your companions keep pace with your physical route.','subtle')]));
 const c=s.location;$('infrastructure-status').textContent=`${c.feature}\nStability ${c.stability} · shelter ${c.shelter} · public relay ${c.relay||0} · water stock ${c.water}`;
 const b=s.business;$('business-panel').hidden=!b;
 if(b){$('business-status').textContent=`${b.name}\n${b.faction} · condition ${b.condition} · demand ${b.demand} · reserve ${b.reserve} scrap`;
  $('business-controls').replaceChildren(command('REVIEW BUSINESS','business'),command('MAINTAIN / 1 SCRAP','work business'),...Object.entries(b.prices).flatMap(([k,v])=>[command(`BUY ${k.toUpperCase()} / ${v} SCRAP / STOCK ${b.stock[k]}`,`buy ${k}`),command(`SELL ${k.toUpperCase()} / 1 SCRAP`,`sell ${k}`)]));
  $('business-history').replaceChildren(...b.ledger.slice(-8).reverse().map(e=>make('p',`Cycle ${e.tick}: ${e.text}`)));
 }
 const t=s.threat;$('combat-panel').hidden=!t||t.resolved||p.remote;if(t)$('threat-status').textContent=`${t.name} / ${t.state.toUpperCase()}\nHealth ${t.health} · defense ${t.defense} · counteraction ${t.attack}\n${t.intent}. ${t.lore}`;
}
