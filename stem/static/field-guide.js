'use strict';
const SVG_NS='http://www.w3.org/2000/svg';
function tacticalBoardView(e,players,n){
 const battle=e?.combat,board=battle?.board;if(!board)return null;
 const wrap=n('section','','tactical-map'),habitat=/^(needle|web|gale|shellwood|ark|enact|tar|bunker|campus)$/.test(e.habitat)?e.habitat:'enact';
 wrap.append(n('p',`ISOMETRIC HEX FIELD · ${habitat.toUpperCase()} · RADIUS ${board.radius} · VISUAL TERRAIN ONLY`,'tactical-map-caption'));
 const svg=document.createElementNS(SVG_NS,'svg');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${habitat} encounter board with ${board.cells.length} axial hexes, radius ${board.radius}; combatant coordinates are listed below.`);
 const side=25,cart=(q,r)=>[1.5*side*q,Math.sqrt(3)*side*(r+q/2)],project=(x,y)=>[(x-y)*.8,(x+y)*.42];
 const center=(q,r)=>{const [x,y]=cart(q,r);return project(x,y);};
 const vertices=(q,r)=>{const [x,y]=cart(q,r);return Array.from({length:6},(_,i)=>{const a=Math.PI*i/3;return project(x+side*Math.cos(a),y+side*Math.sin(a));});};
 const corners=board.cells.flatMap(c=>vertices(c.q,c.r)),xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]),pad=26;
 svg.setAttribute('viewBox',`${Math.min(...xs)-pad} ${Math.min(...ys)-pad} ${Math.max(...xs)-Math.min(...xs)+pad*2} ${Math.max(...ys)-Math.min(...ys)+pad*2}`);
 const cellOrder=[...board.cells].sort((a,b)=>(a.q+a.r)-(b.q+b.r)||a.q-b.q);
 for(const cell of cellOrder){
  const hex=document.createElementNS(SVG_NS,'polygon');hex.setAttribute('points',vertices(cell.q,cell.r).map(([x,y])=>`${x.toFixed(1)},${y.toFixed(1)}`).join(' '));hex.setAttribute('class',`hex-tile hex-tile--${habitat}`);hex.setAttribute('data-q',cell.q);hex.setAttribute('data-r',cell.r);
  const title=document.createElementNS(SVG_NS,'title');title.textContent=`${cell.ground}${cell.feature?` / ${cell.feature}`:''} · axial ${cell.q},${cell.r} · visual only`;hex.append(title);svg.append(hex);
  if(cell.feature){const [x,y]=center(cell.q,cell.r),mark=document.createElementNS(SVG_NS,'circle');mark.setAttribute('cx',x.toFixed(1));mark.setAttribute('cy',(y-2-cell.relief).toFixed(1));mark.setAttribute('r',(2.3+cell.relief*.7).toFixed(1));mark.setAttribute('class',`hex-feature hex-feature--${habitat}`);const label=document.createElementNS(SVG_NS,'title');label.textContent=cell.feature+'; does not alter movement or cover.';mark.append(label);svg.append(mark);}
 }
 const combatants=[];
 const unit=(pos,label,kind,active=false)=>{
  if(!Array.isArray(pos))return;const [x,y]=center(pos[0],pos[1]),shape=document.createElementNS(SVG_NS,kind==='foe'?'polygon':'circle');
  combatants.push({q:pos[0],r:pos[1],label,kind,active});
  if(kind==='foe'){shape.setAttribute('points',`${x.toFixed(1)},${(y-9).toFixed(1)} ${(x+8).toFixed(1)},${y.toFixed(1)} ${x.toFixed(1)},${(y+9).toFixed(1)} ${(x-8).toFixed(1)},${y.toFixed(1)}`);}
  else{shape.setAttribute('cx',x.toFixed(1));shape.setAttribute('cy',y.toFixed(1));shape.setAttribute('r','8');}
  shape.setAttribute('class',`hex-unit hex-unit--${kind}${active?' hex-unit--active':''}`);shape.setAttribute('data-q',pos[0]);shape.setAttribute('data-r',pos[1]);
  const title=document.createElementNS(SVG_NS,'title');title.textContent=`${label} · axial ${pos[0]},${pos[1]}${active?' · active turn':''}`;shape.append(title);svg.append(shape);
  if(kind==='player'){const text=document.createElementNS(SVG_NS,'text');text.setAttribute('x',x.toFixed(1));text.setAttribute('y',(y+3).toFixed(1));text.setAttribute('text-anchor','middle');text.setAttribute('class','hex-unit-label');text.textContent=(label.trim()[0]||'P').toUpperCase();svg.append(text);}
 };
 for(const member of players){const pos=battle.positions?.[member.id];if(pos&&!battle.escaped?.includes(member.id))unit(pos,member.name,'player',e.active_turn===member.id);}
 for(const actor of e.actors||[])if(actor.hex)unit(actor.hex,actor.name,'foe',e.active_turn===actor.instance_id);
 const legend=n('p','● Explorers  ◆ Encounter actors · Coordinates are axial (q, r). Terrain is visual only.','tactical-map-legend');
 const positions=n('ul','','tactical-map-positions');
 for(const combatant of combatants){
  const side=combatant.kind==='player'?'EXPLORER':'ENCOUNTER ACTOR';
  const active=combatant.active?' · ACTIVE TURN':'';
  const item=n('li',`${side} · ${combatant.label} · AXIAL (${combatant.q}, ${combatant.r})${active}`,`tactical-map-position tactical-map-position--${combatant.kind}${combatant.active?' tactical-map-position--active':''}`);
  if(combatant.active)item.setAttribute('aria-current','true');
  positions.append(item);
 }
 wrap.append(svg,legend,positions);return wrap;
}
window.FieldGuide={
 render(s,id,send,stem=false){
  const p=stem?s.me:s.players.find(x=>x.id===id),f=stem?s.field_guide:p?.field_guide;
  if(!p||!f)return;
  let panel=document.getElementById('field-guide-panel');
  if(!panel){panel=document.createElement('section');panel.id='field-guide-panel';panel.className='field-guide';document.getElementById(stem?'description':'story').after(panel);}
  const n=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
  const started=s.started&&!s.paused,host=s.host===id;
  panel.replaceChildren(n('h2','FIELD GUIDE / SHARED RULES'));
  const button=(label,op,data={},parent=panel,disabled=false)=>{
   const b=n('button',label,'quiet');b.disabled=disabled;b.dataset.fieldDisabled=String(disabled);
   b.onclick=()=>send(op,data);parent.append(b);return b;
  };
  const act=(label,action,target='',parent=panel,disabled=false)=>button(label,'field',{action,target},parent,!started||disabled);
  if(!f.enabled){panel.append(n('p',f.migration));if(host)button('ADOPT FIELD GUIDE 1.0','field_adopt');return;}
  const fieldMode=stem||s.mode==='open';
  panel.append(n('p',`SESSION ${f.session} · ACTIVE CYCLE ${f.cycle} · WATCH ${f.watch} · ${f.earned_xp} EARNED XP · ${f.growth} GROWTH · ${f.session_xp}/3 SESSION XP`,'field-status'));
  panel.append(n('p',`Pack ${f.bulk.used}/${f.bulk.capacity} bulk${f.bulk.overloaded?' · overloaded: movement checks −2':''}. ${f.session_note}`,'dim'));
  const last=f.latest_check;
  if(last?.odds){const q=last.odds;panel.append(n('p',`${last.action}: ${last.die} + ${last.bonus} vs ${last.dc} → ${last.grade.toUpperCase()}. Exact chance ${q.pass_percent}% · complication ${q.complication}% · setback ${q.setback}% · success ${q.success}% · strong ${q.strong}%.`,'field-check'));}
  const e=f.encounter,b=e?.combat,fighting=!!b&&!b.finished,turn=e?.active_turn===id;
  if(fieldMode){
   const actions=n('div','','button-row');
   for(const [label,op] of [['SPEND A WATCH / 4 CYCLES','field_watch'],['BREATHER / 1 CYCLE','field_breather'],['FULL REST / 4 CYCLES + RATIONS','field_rest'],['EAT / 1 FOOD','field_eat'],['DRINK / 1 WATER','field_drink'],['TREAT / 1 MEDKIT','field_treat']])act(label,op,'',actions,fighting&&op!=='field_treat'||fighting&&!turn);
   panel.append(actions);
   if(e){
    const box=n('section','','field-encounter');box.append(n('h3',`ENCOUNTER / ${e.habitat.toUpperCase()} · BUDGET ${e.spent_budget||0}/${e.budget}`),n('p',e.event));
    if(e.sign)box.append(n('p',e.sign,'field-prose'));
    if(b)box.append(n('p',b.finished?'ENCOUNTER CLOSED':`ROUND ${b.round} · TURN ${s.players.find(x=>x.id===e.active_turn)?.name||e.active_turn} · YOUR AP ${b.ap[id]||0}`,'field-status'));
     if(fighting){const tactical=tacticalBoardView(e,s.players,n);if(tactical)box.append(tactical);}
    const target=n('select');target.setAttribute('aria-label','Encounter target');
    for(const a of e.actors){
     if(a.state==='present'&&a.health>0)target.append(new Option(a.name+' / '+a.instance_id,a.instance_id));
     const detail=n('details'),summary=n('summary',`${a.name} · ${a.state.toUpperCase()} · ${a.variant}`);detail.append(summary);
     detail.append(n('p',a.appearance,'field-prose'),n('p',`${a.health}/${a.max_health} Health · ${a.energy} Energy · Defense ${a.defense} · Attack DC ${a.attack_dc} · Damage ${a.damage} ${a.channel} · Armor ${a.armor} · AP ${a.ap} · Range ${a.range}${a.distance!==undefined?' · Distance '+a.distance+' hexes':''}`));
     for(const text of [`Intent: ${a.intent}`,`Disposition: ${a.disposition}; present need: ${a.present_need}.`,`Peaceful route: ${a.nonviolent}`,`Specific limits: ${a.special}`,`Stored attacks: ${a.ammo===null?'ordinary AP limit':a.ammo} · attacks/turn ${a.attack_limit} · ${a.stationary?'anchored':'mobile'}`,a.source_note])detail.append(n('p',text));
     box.append(detail);
    }
    if(e.actors.length){
     box.append(target);
     function targeted(label,action,disabled=false){const x=act(label,action,'',box,disabled);x.onclick=()=>send('field',{action,target:target.value});}
     if(!fighting&&!e.resolved){act('BEGIN LOCAL TURNS','field_engage','',box);targeted('OFFER PEACEFUL PASSAGE','field_parley');act('DECLINE FREELY','field_withdraw','',box);}
     if(fighting){
      targeted('APPROACH / 1 AP','field_approach',!turn);targeted('RETREAT / 1 AP','field_retreat',!turn);
      targeted('STAFF / 3 AP','field_attack',!turn);targeted('CRYSTALLIN SHOT / 4 AP + SCRAP','field_shoot',!turn);
      act('GUARD / 2 AP','field_guard','',box,!turn);targeted('PASSAGE OFFER / 3 AP','field_parley',!turn);
      act('DISENGAGE / 1 AP','field_withdraw','',box,!turn);act('END TURN / 0 AP','field_end','',box,!turn);
     }
     if(e.resolved&&!e.loot_paid&&e.actors.some(a=>a.health===0&&!a.person))act('RECOVER ABANDONED MATERIAL / ONCE','field_salvage','',box);
    }
    const history=n('details');history.append(n('summary','ENCOUNTER RECORD'),...e.events.slice(-12).map(t=>n('p',t)));box.append(history);panel.append(box);
   }else panel.append(n('p',`Habitat: ${f.habitat||'no verified physical habitat'}. Travel or spend a watch to observe a field opportunity; reading this panel never rolls.`,'dim'));
   if(last?.grade==='complication'&&(p.character?.skills?.[last.skill]||0)===3)act('USE RANK-3 MASTERY / ONCE PER SESSION','field_mastery','',panel,fighting&&!turn);
   const gear=n('details');gear.append(n('summary','MATERIAL CONDITION / FIELD REPAIRS'));
   for(const [key,g]of Object.entries(f.gear)){gear.append(n('p',`${g.name} · ${g.material} · condition ${g.condition}/100 · operating threshold ${g.threshold}`));if(g.condition===0)act(`REPLACE ${g.name.toUpperCase()} / 2 MATERIALS`,'field_replace',key,gear,fighting);if(g.condition>0&&g.condition<100)act(`REPAIR ${g.name.toUpperCase()} / 1 SCRAP`,'field_repair',key,gear,fighting);}
   panel.append(gear);
   if(!stem){
    const companions=n('details');companions.append(n('summary','COMPANIONS / TWO SHARED AGREEMENTS'));
    for(const a of f.companions){
     const card=n('div','','companion-card');card.append(n('h3',a.name),n('p',`${a.health} Health · ${a.energy} Energy · attitude ${a.attitude} · ${a.engagement.phase} / ${a.engagement.task}`),n('p',a.character.bio),n('p',`Goal: ${a.character.goal}. Boundary: ${a.character.boundary}.`),n('p',`Attributes ${JSON.stringify(a.character.attributes)} · training ${JSON.stringify(a.character.skills)} · own pack ${JSON.stringify(a.inventory)}`));
     act('REVIEW LORE / PLANS','field_npc_talk',a.id,card,fighting);
     if(a.owner===id){
      for(const task of ['support','guard','rest'])act('TASK / '+task.toUpperCase(),'field_npc_task',a.id+'|'+task,card,fighting);
      for(const item of ['food','water'])act('SHARE ONE '+item.toUpperCase(),'field_share',a.id+'|'+item,card,fighting);
      act('RELEASE AGREEMENT','field_dismiss',a.id,card);
     }else act('OFFER AGREEMENT / 1 FOOD + 1 WATER','field_recruit',a.id,card,fighting);
     companions.append(card);
    }
    panel.append(companions);
   }
  }
  const growth=n('details');growth.append(n('summary','CHARACTER GROWTH / EARNED XP REMAINS'));
  const choose=n('select');choose.setAttribute('aria-label','Growth choice');
  for(const attr of ['body','tech','percept','rapport'])choose.append(new Option(attr.toUpperCase()+' +1 / 2 Growth','attribute:'+attr));
  for(const skill of ['transversal','fieldcraft','ballistics','needlurgy','seamllurgy','fractech','metallurgy','crystallin','resource','arcane','archive','rune','medtech','necra','lifestring','druid','percept','light','aether','nullsurvey','history','contracts','community','teaching','memetic'])choose.append(new Option(skill+' +1 / 1 Growth','skill:'+skill));
  growth.append(choose);const spend=act('SPEND GROWTH','field_grow','',growth,fighting);spend.onclick=()=>send('field',{action:'field_grow',target:choose.value});panel.append(growth);
  if(host){const session=n('details');session.append(n('summary','HOST / SESSION RECORD'));
   session.append(n('p','Declare a new session when the group begins one. Award the additional goal XP only for an agreed, completed goal.'));
   button('BEGIN NEXT SESSION','field_session',{},session,fighting);
   for(const member of s.players)button('RECORD AGREED GOAL / '+member.name,'field_goal',{target:member.id},session);
   panel.append(session);
  }
  const trace=n('details');trace.append(n('summary',`DICE RECORD / ${f.roll_count} SAVED DRAWS`),...f.recent_rolls.map(r=>n('p',`#${r.index} · ${r.label} · D${r.sides} ${r.value}`)));panel.append(trace);
 }
};
