'use strict';
window.StemCreator={};
(()=>{
 const C=window.StemCreator,get=id=>document.getElementById(id),make=(tag,text='')=>{const n=document.createElement(tag);n.textContent=text;return n;};
 const fields=['pronouns','origin','form','affiliation','affinity','mod','bio','goal','boundary','appearance','voice','mannerisms','age'];
 let catalog=null;
 function message(text){get('character-message').textContent=text;}
 function totals(){const a=Object.keys(catalog.attributes).reduce((s,k)=>s+Number(get('char-attr-'+k).value),0),sk=Object.keys(catalog.skills).reduce((s,k)=>s+Number(get('char-skill-'+k).value),0);get('character-budget').textContent=`Attributes ${a}/8 · training ${sk}/6. Identity and affiliations do not grant clearance.`;}
 C.role=()=>get('build').value;
 C.read=()=>{
  if(!catalog)throw Error('Character catalog is still loading.');
  const c={schema:2,role:C.role(),attributes:{},skills:{}};for(const k of fields)c[k]=get('char-'+k).value;
  for(const k of Object.keys(catalog.attributes))c.attributes[k]=Number(get('char-attr-'+k).value);
  for(const k of Object.keys(catalog.skills)){const v=Number(get('char-skill-'+k).value);if(v)c.skills[k]=v;}
  if(Object.values(c.attributes).some(v=>!Number.isInteger(v)||v<1||v>4)||Object.values(c.attributes).reduce((a,b)=>a+b,0)!==8)throw Error('Allocate exactly 8 attribute points, with scores 1–4.');
  if(Object.values(c.skills).some(v=>!Number.isInteger(v)||v<0||v>3)||Object.values(c.skills).reduce((a,b)=>a+b,0)>6)throw Error('Allocate at most 6 proficiency points, with scores 0–3.');
  return c;
 };
 C.set=(role,c)=>{
  if(!catalog?.roles[role])throw Error('Unknown discipline.');get('build').value=role;
  const defaults=catalog.presets[role];for(const k of fields)get('char-'+k).value=c[k]??defaults[k]??'';
  for(const k of Object.keys(catalog.attributes))get('char-attr-'+k).value=c.attributes?.[k]??defaults.attributes[k];
  for(const k of Object.keys(catalog.skills))get('char-skill-'+k).value=c.skills?.[k]||0;totals();
 };
 C.init=c=>{
  catalog=c;const prior=get('build').value;get('build').replaceChildren(...Object.keys(c.roles).map(k=>new Option(k,k)));
  const area=get('character-fields');area.replaceChildren();const labels={pronouns:'Pronouns',origin:'Origin',form:'Embodiment concept',affiliation:'Affiliation or aspiration',affinity:'Affinity',mod:'Starting bio-mod blueprint',bio:'Biography and backstory',goal:'Goal',boundary:'Boundaries',appearance:'Appearance',voice:'Voice and dialogue style',mannerisms:'Mannerisms',age:'Age description (optional)'};
  const lists={origin:c.origins,form:c.forms,affiliation:c.affiliations,affinity:c.affinities,mod:Object.keys(c.mods)};
  for(const k of fields){const label=make('label',labels[k]),input=make(lists[k]?'select':['bio','goal','boundary','appearance','voice','mannerisms'].includes(k)?'textarea':'input');input.id='char-'+k;if(lists[k])input.append(...lists[k].map(v=>new Option(k==='mod'?c.mods[v].label:v,v)));else{input.maxLength=c.text_limits[k];input.rows=k==='bio'?6:3;}label.append(input);area.append(label);}
  const attrs=get('character-attributes');attrs.replaceChildren();for(const [k,desc]of Object.entries(c.attributes)){const label=make('label',k.toUpperCase()),input=make('input');input.id='char-attr-'+k;input.type='number';input.min=1;input.max=4;input.oninput=totals;label.append(input,make('small',desc));attrs.append(label);}
  const skills=get('character-skills');skills.replaceChildren();for(const [k,v]of Object.entries(c.skills)){const label=make('label',v.label),input=make('input');input.id='char-skill-'+k;input.type='number';input.min=0;input.max=3;input.oninput=totals;label.append(input,make('small',v.usage));skills.append(label);}
  C.set(c.roles[prior]?prior:'Fractech Archivist',c.presets[c.roles[prior]?prior:'Fractech Archivist']);
  get('build').onchange=()=>C.set(C.role(),catalog.presets[C.role()]);C.ready=true;
 };
 function bundle(){return {format:'Stem-character',version:2,role:C.role(),character:C.read()};}
 get('character-draft').onclick=()=>{try{localStorage.setItem('stem-character-draft',JSON.stringify(bundle()));message('Character draft saved in this browser.');}catch(e){message(e.message);}};
 get('character-load').onclick=()=>{try{const b=JSON.parse(localStorage.getItem('stem-character-draft'));C.set(b.role,b.character);C.read();message('Draft loaded.');}catch(e){message(e.message);}};
 get('character-export').onclick=()=>{try{const blob=new Blob([JSON.stringify(bundle(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=make('a');a.href=url;a.download='Stem-character.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Exported the character template; earned progress stays in the world save.');}catch(e){message(e.message);}};
 get('character-import').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>65536)throw Error('Character template must be at most 64 KiB.');const b=JSON.parse(await file.text());if(!((b.format==='Stem-character'&&b.version===2)||(b.format==='THORNS-character'&&b.version===1)))throw Error('Use a Stem v2 or THORNS v1 character template.');C.set(b.role,b.character);C.read();message('Template loaded; the server validates it when you enter or apply.');}catch(e){message(e.message);}finally{e.target.value='';}};
})();
