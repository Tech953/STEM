"""Mapped institutions, persistent characterization, dialogue and varied commitments."""
import copy
import geography as geo
import characters as chars
import survival
import companions
import generation
import field_rules

ACTS={'goto','travel','abandon','fulfill','register','study','install','remove','treat','clinic','provision','dialogue','contract','survey','talk'}
PERSONAS={
 'thorns':('Iri Thread','THORNS fabricator','THORNS','practical, reciprocal','We stitch a route into every layer. Tell me what you can carry, and what you need to leave behind.'),
 'arcturion':('Sen Ledger','contract keeper','THORNS','measured, welcoming','A contract should say what will be done, where, and for whom. Your name belongs beside your actual commitment.'),
 'wn_tower':('Ninefold Tutor','archive-tech visitor','WN_EDU','exact, patient','The height of the Needle changes what a path means. A lesson is an offer; access has its own conditions.'),
 'greatweb':('Tavi Brace','Embrite maintenance worker','Embrite','plainspoken','We mend the accessible rail. The entire network is not ours to command.'),
 'blackdot':('Black.Dot Registrar','registration representative','WN_LAW','formal, precise','I can record this field scope. I cannot make you an administrator.'),
 'wn_med':('Vela Tran','contracted care coordinator','WN_MED','clinical','Care here depends on a client relationship. The general population is outside this desk’s treatment contract.'),
 'mod_op':('Orin Grain','exchange craftsperson','MOD_OP','terse, exact','Show the materials and the agreement. A name alone is not an exchange.'),
 'ed_net':('KHO','bounded educational projection','KHO / ED.NET','questioning, precise','What in your report was observed, and what did you infer? Keep the distinction visible.'),
 'runehills':('PYRI','lightPROKT< teacher','PYRI','open, reflective','I can offer a pattern. Your choice to learn it is still yours.'),
 'resid':('PAMAN DAL','pilgrim provision guide','CHECKPOINT.RESID community','generous, steady','Take what supports your crossing. Care for the next pilgrim when your own hands are steady.'),
 'casc':('Lila','sage at the tent','Lila / CASC','careful, personal','A remembered thought may resemble a present voice. Do not treat that resemblance as a person’s agreement.'),
 'undertow':('Meren Vane','NanoClad border recorder','NanoClad','restrained, observational','We record a change before naming it. That is how uncertainty survives a long journey.'),
}
FACTIONS=['THORNS','Embrite','Druid-Sec','Fractech','WN_LAW','KHO / ED.NET','OMNI-META.OPEND','MMTX<','SEC.IO','FOOTHILL CUSP residents','NanoClad','CHECKPOINT.RESID community','Lila / CASC','Sap Core','Lifestring.CO','WN_MED','MILI_WN','WN_EDU','The Harvet','ANC.NI','MOD_OP','SPIDREsec','initial_VERGE','ADMIN.COA','PYRI']
RESIDENT_DETAILS={
 'thorns':'Seam-scored bio-plast sleeves and a bundle of repair thread carry the marks of many crossings.',
 'arcturion':'A flattened ledger rests beneath ink-marked hands; loose route slips are weighted against the draft.',
 'wn_tower':'A narrow lesson frame throws small geometric reflections across an ash-dusted work surface.',
 'greatweb':'A patched brace harness catches against the service rail, its fittings polished by repeated handling.',
 'blackdot':'Verification plates and a small registration stylus divide the counter into carefully maintained scopes.',
 'wn_med':'A clean service screen separates the client ledger from the dust brought in by passing pilgrims.',
 'mod_op':'Darkwood shavings collect below the exchange bench; each crystallin fitting is laid beside its material record.',
 'ed_net':'A bounded light-projection lesson places KHO’s symbolic figurehead between geometric metal frames.',
 'runehills':'PYRI’s lightPROKT< presence accompanies worked-metal teaching patterns.',
 'resid':'PAMAN DAL’s guidance carries through the provision station beside the lightPROKT< tree’s filtered water.',
 'casc':'Lila, a blind sage, listens beside the tent while light manifestations move at the dustland edge.',
 'undertow':'A dust-sealed field coat is folded around a border ledger; observations are entered before names.',
}
REGIONAL_DETAILS={'WN_TOWER':'Ash has settled into the seams of a repaired outer layer; a roll of route bindings hangs close to hand.','CITY_CLOUD_S':'Salvage dust marks the work surface, where a metal route gauge rests beside carefully sorted fragments.','ENACT_HILLS':'Household repair tools share a table with the local route book; worked metal carries the warmth of repeated use.','AETHERGALE':'A dust-worn route wrap hangs beside a provision tally, its edges catching jade and rose light.'}
STUDY_SKILLS={'wn_tower':'seamllurgy','thorns':'community','arcturion':'contracts','greatweb':'fractech','undercroft':'percept','lower_burgs':'teaching','blackdot':'needlurgy','spidre':'transversal','mod_op':'crystallin','wn_med':'medtech','harvet':'druid','vines':'druid','ind_crux':'history','amp_lands':'resource','foothills':'community','runehills':'rune','gravesite':'archive','base_kho':'metallurgy','ed_net':'fractech','mid':'transversal','peak':'memetic','triad':'fieldcraft','resid':'lifestring','gale':'arcane','casc':'light','undertow':'nullsurvey','red_gate':'aether','northern_spiral':'history'}

def init(w):
 w.setdefault('layout','legacy');w.setdefault('spawn',[0,0]);w.setdefault('residents',{});w.setdefault('contract_serial',0)
 for f in FACTIONS:w['reputation'].setdefault(f,0)
 for p in w['players']:chars.ensure(p);survival.ensure(p);p.setdefault('route',[]);p.setdefault('destination',None);p.setdefault('companions',[]);p.setdefault('personal_reputation',{})
 generation.ensure_world(w)
def landmark(w,p):return geo.landmark(*p['pos']) if w.get('layout')=='atlas' else None
def resident(w,p):
 lm=landmark(w,p)
 if not lm:return None
 k=lm['id']
 if k not in w['residents']:
  if k in PERSONAS:name,role,faction,tone,line=PERSONAS[k]
  else:
   name=lm['name'].split()[0]+' Routekeeper';role='local route custodian';faction={'WN_TOWER':'Embrite','CITY_CLOUD_S':'KHO / ED.NET','ENACT_HILLS':'FOOTHILL CUSP residents','AETHERGALE':'NanoClad'}[lm['region']];tone='grounded, watchful';line='This place has its own work and limits. I can discuss its routes, resources and commitments.'
  w['residents'][k]=dict(id='resident:'+k,name=name,role=role,faction=faction,tone=tone,line=line,x=lm['pos'][0],y=lm['pos'][1],need='water' if lm['region']=='AETHERGALE' else 'scrap',trust=0,activity='keeping the local route and provision record',last_help=-10,description=f"{name}, {role}, speaks in a {tone} manner. "+RESIDENT_DETAILS.get(k,REGIONAL_DETAILS[lm['region']]))
 return companions.ensure(w,w['residents'][k])
def topics(w,p):
 a=resident(w,p)
 if not a:return []
 options=[('place','Ask about this place'),('routes','Ask about the routes'),('needs','Ask what they need'),('contract','Ask about available commitments'),('history','Ask what they remember of you'),('access','Ask about access and certification')]
 return [dict(topic=t,label=label,command='ask about '+t) for t,label in options]
def note_dialogue(w,p,a,topic,text):
 lm=landmark(w,p)
 log=dict(tick=w['tick'],location=lm['name'] if lm else w['cells'][str(p['pos'][0])+','+str(p['pos'][1])]['title'],npc=a['name'],topic=topic,response=text,character=dict(name=p['name'],pronouns=chars.ensure(p)['pronouns'],origin=p['character']['origin'],affiliation=p['character']['affiliation'],appearance=p['character']['appearance'],voice=p['character']['voice'],goal=p['character']['goal'],boundary=p['character']['boundary']))
 p['dialogue_log'].append(log);p['dialogue_log']=p['dialogue_log'][-200:]
 rel=p['relationships'].setdefault(a['id'],dict(visits=0,trust=0,last_topic='',introduced=False))
 rel['visits']+=1;rel['last_topic']=topic;rel['introduced']=True
 return text

def board(w,p):
 lm=landmark(w,p)
 if not lm or not any(s in lm['services'] for s in ['board','medical_contract']):return []
 kinds=['survey','delivery','restoration','diplomacy'] if 'board' in lm['services'] else ['delivery']
 return [dict(kind=k,label={'survey':'Record a habitat at a mapped destination','delivery':'Carry two food and one water to a named recipient','restoration':'Repair a habitat near a named destination','diplomacy':'Carry an introduction and pass a Rapport check'}[k],command='accept '+k+' contract') for k in kinds]
def contract(w,p,kind,engine):
 require=engine.require;lm=landmark(w,p);require(lm is not None and board(w,p),'Find a contract board on the route map.')
 require(p['contract'] is None,'Finish or abandon your current commitment first.');require(kind in {o['kind'] for o in board(w,p)},'Choose one of this board’s displayed commitment types.')
 options=[v for v in geo.LANDMARKS.values() if v['pos']!=p['pos'] and 'survey' in v['services']]
 # Nearby destinations keep basic commitments viable; replay rotates among them.
 options.sort(key=lambda v:(abs(v['pos'][0]-p['pos'][0])+abs(v['pos'][1]-p['pos'][1]),v['name']))
 target=options[w['contract_serial']%min(6,len(options))];w['contract_serial']+=1
 faction=resident(w,p)['faction'];c=dict(id=w['contract_serial'],kind=kind,target=target['pos'][:],destination=target['name'],issuer=lm['name'],faction=faction,progress=0,accepted_tick=w['tick'],reward='2 food, 2 water, 1 seed, 2 XP, +2 reputation; care benefits where applicable')
 if kind=='restoration':
  # Use an adjacent generated site, so the task is work rather than arrival.
  x,y=target['pos'];c['target']=next(([x+dx,y+dy] for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)] if geo.info(x+dx,y+dy)['passable'] and not geo.landmark(x+dx,y+dy)),target['pos'][:]);c['destination']='Habitat near '+target['name']
 if field_rules.active(w):
  local=engine.local(w,p)
  require(local['food']>=2 and local['water']>=2 and local['growth']>=3,'This issuer lacks real provisions for another reward escrow.')
  local['food']-=2;local['water']-=2
  if local.get('contract_seed_stock',0)>0:local['contract_seed_stock']-=1
  else:local['growth']-=3
  c.update(issuer_pos=p['pos'][:],escrow=dict(food=2,water=2,seed=1),recipient=target['name']+' field recorder',scope='one '+kind+' commitment',evidence='recorded work at the exact target',deadline=None,exit='Abandon freely; −1 issuer standing')
 p['contract']=c;return f"{lm['name']} registers a {kind} commitment to {c['destination']} at {c['target']}. {('Carry two food and one water. ' if kind=='delivery' else 'Complete one successful repair at the target. ' if kind=='restoration' else 'Present the introduction and pass a Rapport check. ' if kind=='diplomacy' else 'Record the habitat with a Percept check. ')}Then type fulfill. Reward: {c['reward']}."
def after_work(w,p,action,success):
 c=p.get('contract')
 if c and c.get('kind')=='restoration' and action=='restore' and success and p['pos']==c['target']:c['progress']=1

def handle(w,p,intent,raw,engine):
 op=intent['action'];target=intent.get('target','');require=engine.require;lm=landmark(w,p);a=resident(w,p) or engine.present_actor(w,p);c=engine.local(w,p);time=False;roll='';out=''
 if op in ['contract','survey','talk'] and w.get('layout')!='atlas':return None
 if op=='goto':
  require(w.get('layout')=='atlas','Interpreted route travel is available in new atlas worlds. Legacy saves keep their previous grid.')
  if geo.norm(target)=='commitment':
   require(p['contract'] is not None,'Accept a commitment before routing to its target.');dest=dict(pos=p['contract']['target'],name=p['contract']['destination'])
  else:
   k=geo.resolve(target);require(k is not None,'Choose a named landmark from the route map.');dest=geo.LANDMARKS[k]
  path=geo.route(p['pos'],dest['pos']);p['route']=path;p['destination']=dest['name'];out=f"Route registered to {dest['name']}: {len(path)} sectors. Travel takes each step and its survival cost; this is not teleportation."
  ok,roll=engine.check(w,p,'percept',9,'fieldcraft');out+=(' Your route-reading check gives a clear traversal plan.' if ok else 'The physical route is recorded, but its conditions need cautious observation.')
 elif op=='travel':
  require(p.get('route'),'Choose a destination on the route map first.')
  dest=p['route'][0];dx,dy=dest[0]-p['pos'][0],dest[1]-p['pos'][1]
  direction=next(k for k,v in engine.DIRS.items() if v==(dx,dy));p['route']=p['route'][1:]
  result=engine.act(w,p,dict(action='move',target=direction),raw,following_route=True)
  if not p['route'] and p['pos']==dest:result['text']+=' You have reached the registered route destination.';p['last_result']=result['text']
  return dict(already_finalized=True,**result)
 elif op=='talk' or op=='dialogue':
  require(a is not None,'No one is presently here to answer. Travelers may move to a better-supplied site.')
  topic=target or 'place';require(topic in ['place','routes','needs','contract','history','access'],'Choose a displayed dialogue topic.')
  ch=chars.ensure(p);rel=p['relationships'].get(a['id'],{});prefix=f"{a['name']} addresses {p['name']}, introduced as {ch['origin']} / {ch['affiliation']}. "
  ok,roll=engine.check(w,p,'rapport',10,'teaching' if topic in ['history','access'] else 'community',dict(npc=a['id']))
  if not rel.get('introduced'):prefix+=('Your described appearance is registered: '+ch['appearance']+'. ' if ch['appearance'] else '')
  if topic=='place':speech=a.get('line','I follow the supplies and the ground that will hold them. ')+(lm['description'] if lm else c['title']+' is part of my current route.')
  elif topic=='routes':speech='Landmarks and routes are listed on your interpreted atlas. Terrain and storms make distance costly. Your recorded destination is '+str(p.get('destination') or 'not yet chosen')+'.'
  elif topic=='needs':speech=f"I currently need {a['need']}. Giving one unit helps the local provision record. Work at this place may also support the habitat."
  elif topic=='contract':speech=('We offer survey, delivery, restoration and introduction commitments. Review the exact destination and costs before agreeing.' if board(w,p) else 'I keep no open contract board here. The route map identifies places where one is available.')
  elif topic=='history':speech=f"Our ledger records {rel.get('visits',0)} conversations and trust {rel.get('trust',0)}. Your declared goal is {ch['goal'] or 'not yet stated'}. You have completed {len(p['contract_history'])} registered commitments."
  else:speech='Your verified field credentials are '+(', '.join(p['credentials']) or 'none')+'. Origins, affiliations and reputation never grant admin.OS or adminENACT. Exterior observation is distinct from entry.'
  if ch['voice']:prefix+='Your dialogue style is recorded as '+ch['voice']+'. '
  if ch['mannerisms']:prefix+='Your mannerisms are recorded as '+ch['mannerisms']+'. '
  if ch['boundary']:speech+=' Your stated boundary remains recorded: '+ch['boundary']
  if ok:
   speech+=' The exchange leaves room for a fuller explanation of the local responsibilities.'
   if w['tick']>=a.get('dialogue_after',-4):a['attitude']=min(100,a['attitude']+1);a['dialogue_after']=w['tick']+4
  else:speech+=' I can confirm those records, but I will keep the rest of this account provisional.'
  out=note_dialogue(w,p,a,topic,prefix+generation.dialogue(w,p,a,topic,speech,ok,c))
 elif op=='contract':
  kind=target or 'survey';require(p['contract'] is None,'Finish or abandon your current commitment first.');require(kind in {o['kind'] for o in board(w,p)},'Choose one of this board’s displayed commitment types.')
  ok,roll=engine.check(w,p,'rapport',11,'contracts',dict(npc=a['id'] if a else None));time=not field_rules.active(w)
  out=contract(w,p,kind,engine) if ok else 'The commitment terms are not yet accepted; no active contract is created.'
 elif op in ['fulfill','survey']:
  cm=p['contract'];require(cm is not None and 'kind' in cm,'Accept a mapped commitment first.');require(p['pos']==cm['target'],'Reach the commitment’s exact target coordinates.')
  require(all(p['inventory'][k]<=97 for k in ['food','water','seed']),'Make room for the registered reward.')
  kind=cm['kind'];time=True
  if kind=='delivery':require(p['inventory']['food']>=2 and p['inventory']['water']>=1,'Delivery requires two food and one water.')
  elif kind=='restoration':require(cm['progress']>=1 or (c['stability']>=90 and c['growth']>=75),'Complete a successful repair here before fulfilling this commitment.')
  stat,skill={'delivery':('tech','resource'),'restoration':('tech','metallurgy'),'diplomacy':('rapport','contracts'),'survey':('percept','percept')}[kind]
  ok,roll=engine.check(w,p,stat,10,skill,dict(faction=cm['faction'],npc=a['id'] if a else None))
  if ok:
   if field_rules.active(w):
    paid=p.setdefault('paid_contracts',[]);require(str(cm['id']) not in paid,'This commitment has already been paid.');paid.append(str(cm['id']))
   if kind=='delivery':p['inventory']['food']-=2;p['inventory']['water']-=1
   for k,n in [('food',2),('water',2),('seed',1)]:p['inventory'][k]+=n
   p['xp']+=2;p['karma']=engine.clamp(p['karma']+2,-100,100);engine.standing(w,p,cm['faction'],2)
   p['care_benefits']=min(3,p['care_benefits']+1)
   if cm['faction']=='WN_MED' and 'WN_MED care relationship' not in p['credentials']:p['credentials'].append('WN_MED care relationship')
   p['contract_history'].append(dict(**copy.deepcopy(cm),completed_tick=w['tick']));p['contract_history']=p['contract_history'][-60:];p['contract']=None
   out=f"Your {kind} commitment is completed and its reward recorded. Care benefit tier is now {p['care_benefits']}/3."
  else:out='The submission is not yet accepted; its commitment remains open. No reward is paid.'
 elif op=='abandon':
  cm=p['contract'];require(cm is not None,'No accepted commitment.')
  if field_rules.active(w) and cm.get('escrow') and cm.get('issuer_pos'):
   issuer=w['cells'][engine.key(*cm['issuer_pos'])]
   issuer['food']+=cm['escrow']['food'];issuer['water']+=cm['escrow']['water'];issuer['contract_seed_stock']=issuer.get('contract_seed_stock',0)+cm['escrow']['seed']
  f=cm.get('faction');_,roll=engine.check(w,p,'rapport',8,'contracts',dict(faction=f));engine.standing(w,p,f,-1);p['karma']=engine.clamp(p['karma']-1,-100,100);p['contract']=None;out='The commitment is closed as abandoned: −1 reputation and karma.'
 elif op=='register':
  require(lm and 'register' in lm['services'],'Visit Black.Dot Outpost or the Arcturion to register the expedition scope.')
  require('black.dot' not in p['credentials'],'Your bounded field registration is already recorded.');require(p['inventory']['scrap']>=1,'Registration requires one scrap for the physical record.')
  ok,roll=engine.check(w,p,'rapport',10,'contracts',dict(npc=a['id']));time=True
  if ok:
   p['inventory']['scrap']-=1;p['credentials']+=['black.dot','Merc Tag'];blueprint=chars.ensure(p)['mod']
   if blueprint!='none' and blueprint not in p['loadout']:p['loadout'].append(blueprint)
   out='Field-scope black.dot and Merc Tag registration recorded. The selected starting mod may now support listed checks; no administrator clearance is granted.'
  else:out='The proposed registration needs clearer scope. No scrap or credential changes hands.'
 elif op=='study':
  skill='nullsurvey' if p['remote'] else STUDY_SKILLS.get(lm['id'] if lm else '',{'WN_TOWER':'druid','CITY_CLOUD_S':'metallurgy','ENACT_HILLS':'history','AETHERGALE':'aether'}[c['region']])
  if skill=='lifestring':skill='community' # No extraction/resurrection practice is implemented.
  p.setdefault('study_records',{});tag=engine.key(*p['pos'])+':'+skill
  require(w['tick']>=p['study_records'].get(tag,-10)+8,'Return to this exercise after eight cycles; repeated immediate study grants no experience.')
  p['study_records'][tag]=w['tick'];stat=chars.SKILLS[skill]['stat'];ok,roll=engine.check(w,p,stat,11,skill);time=True
  if ok:
   p['xp']+=1
   if lm and lm['id']=='ed_net' and 'ED.NET lesson' not in p['credentials']:p['credentials'].append('ED.NET lesson')
   out='You complete a bounded '+chars.SKILLS[skill]['label']+' exercise and record 1 XP. The result is learning, not unrestricted permission.'
  else:out='The exercise leaves an unresolved distinction. Your observation remains in the record.'
 elif op in ['install','remove']:
  require(lm and 'mods' in lm['services'],'Find a bio-mod craft exchange on the map.');require(target in chars.EQUIPMENT,'Choose a displayed bio-mod.')
  if op=='remove':
   require(target in p['loadout'],'That mod is not installed.');ok,roll=engine.check(w,p,'tech',9,'needlurgy',dict(npc=a['id']))
   if ok:p['loadout'].remove(target);out='The mod is removed; spent exchange materials are not refunded.'
   else:out='Removal is deferred because the safe interface check does not resolve.'
  else:
   require('black.dot' in p['credentials'],'Register the relevant field scope before installing regulated equipment.');require(target not in p['loadout'] and len(p['loadout'])<3,'Three equipment slots; remove a mod before adding another.');require(p['inventory']['scrap']>=2,'This verified exchange requires two scrap.');p['inventory']['scrap']-=2;ok,roll=engine.check(w,p,'tech',11,'needlurgy',dict(npc=a['id']))
   if ok:p['loadout'].append(target);out='Installed '+chars.EQUIPMENT[target]['label']+' within the bounded field scope.'
   else:out='The mod does not integrate; its two exchange scrap are spent.'
  time=True
 elif op=='treat':
  require(p['inventory'].get('medkit',0)>=1,'You have no medkit.');require(p['injuries'] or p['ailments'] or p['health']<100,'No treatment is currently needed.');p['inventory']['medkit']-=1;ok,roll=engine.check(w,p,'tech',10,'medtech');time=True
  if ok:
   p['health']=min(100,p['health']+25)
   if p['injuries']:p['injuries'].pop(0)
   elif p['ailments']:p['ailments'].pop(0)
   out='Treatment restores 25 health and resolves one recorded condition.'
  else:out='The field treatment does not resolve the condition; its medkit is spent.'
 elif op=='clinic':
  require(lm and ('care' in lm['services'] or 'medical_contract' in lm['services']),'Find an appropriate care waypoint.')
  if lm['id']=='wn_med':require('WN_MED care relationship' in p['credentials'],'WN_MED treats contracted clients. Complete a commitment from its desk to establish this relationship.')
  cost=0 if lm['id']=='resid' else max(1,3-p['care_benefits']);require(p['inventory']['scrap']>=cost,'Care requires '+str(cost)+' scrap under this prototype exchange.')
  p['inventory']['scrap']-=cost;p['health']=100;p['injuries']=[];p['ailments']=[];out='Recorded injuries and ailments are treated. Hunger, thirst and sleep still need provision and rest.';time=True
  ok,roll=engine.check(w,p,'rapport',9,'community',dict(npc=a['id']))
  if ok:p['energy']=min(100,p['energy']+5);out+=' A clear care handover also restores five energy.'
 elif op=='provision':
  require(lm and 'free_provision' in lm['services'],'Free pilgrim provision is specifically available at CHECKPOINT.RESID.')
  if field_rules.active(w):
   for item,limit in [('food',4),('water',5)]:
    amount=min(max(0,limit-p['inventory'][item]),c[item]);c[item]-=amount;p['inventory'][item]+=amount
   p['thirst']=max(0,p['thirst']-45);p['food_need']=max(0,p['food_need']-45)
  else:p['thirst']=0;p['food_need']=0;p['inventory']['food']=min(99,max(4,p['inventory']['food']));p['inventory']['water']=min(99,max(5,p['inventory']['water']))
  out='CHECKPOINT.RESID provides water and food freely for the onward journey. This does not grant portable infinity or general immortality.'
  ok,roll=engine.check(w,p,'rapport',8,'community',dict(npc=a['id']));out+=(' The guide also helps clarify your onward care plan.' if ok else 'The free provisions are supplied; the onward conversation remains brief.')
 else:return None
 return dict(text=out,mechanics=roll,intent=intent,time_spent=time)
