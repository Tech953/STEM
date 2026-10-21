"""Persistent NPC designation, voluntary expedition membership and local autonomy."""
import copy
import hashlib
import random
import characters as chars
import geography as geo
import generation
import field_rules

ACTS={'recruit','dismiss','npc_talk','npc_task','share','request','companion_treat'}
PHASES=['observe','plan','work','reflect','recover']
TASKS={'support','survey','repair','forage','guard','mediate','rest'}
TOPICS={'lore','plans','contracts','factions','history','needs','attitude'}
ROLE_MAP={'route keeper':'NanoClad Scout','repairer':'Metal-kin Artisan','provisioner':'Seam Mediator','observer':'Fractech Archivist'}
FACTIONS={'WN_TOWER':['THORNS','Embrite','Druid-Sec'],'CITY_CLOUD_S':['Fractech','KHO / ED.NET'],'ENACT_HILLS':['FOOTHILL CUSP residents','PYRI'],'AETHERGALE':['NanoClad','CHECKPOINT.RESID community']}

def seeded(w,identity):
    return random.Random(int.from_bytes(hashlib.sha256((w['seed']+'|designation|'+identity).encode()).digest(),'big'))

def ensure(w,a):
    a['pos']=[a['x'],a['y']]
    if 'character' not in a:
        g=seeded(w,a['id']);cell=w['cells'][f"{a['x']},{a['y']}"]
        role=ROLE_MAP.get(a['role'],g.choice(list(chars.ROLES)))
        ch=chars.default(role);ch['origin']=cell['region'];ch['pronouns']=g.choice(['she/her','they/them','he/him'])
        tone=a.get('tone') or g.choice(['reflective and exact','dryly humorous','direct and warm','reserved and observant'])
        craft=g.choice(['a childhood tool bench','a caravan water rack','a failed condensation frame','a communal salvage table'])
        loss=g.choice(['a route abandoned after a storm','a teacher whose record became fragmentary','a home workshop scattered between checkpoints','an unfinished repair blamed on the wrong person'])
        motive=g.choice(['make practical care available before someone has to plead for it','restore an honest route record','learn which memories deserve to become commitments','leave a working refuge for the next crossing'])
        boundary=g.choice(['No forced memory extraction','No abandonment of injured travelers','No claims of administrator authority','No taking provisions from unwilling civilians'])
        token=g.choice(['a scored route washer','a folded repair diagram','a darkwood bead from a former workshop','an unsigned lesson slip'])
        appearance=a.get('description') or f"A weathered route layer, carefully patched cuffs, and {token} identify {a['name']}."
        lore=[f"{a['name']} learned the everyday practices of {cell['region']} around {craft}. Their {role.lower()} training grew through shared work rather than an inherited claim of authority.",
              f"They remember {loss}. The event did not settle into a single explanation; they keep the physical evidence beside the versions told by other people. It shapes what they ask before promising help.",
              f"They carry {token}, a personal object rather than a credential. Their current aim is to {motive}. They will accept work that contributes to that aim, while naming a limit: {boundary.lower()}.",
              f"Their unfinished question is whether a dependable practice can outlast the people who first taught it. Traveling, repairing, surveying and talking can produce new evidence. Their engagement record preserves those events without replacing the original history."]
        if a['id'] in {'resident:ed_net','resident:runehills','resident:resid','resident:casc'}:
            anchor=geo.landmark(a['x'],a['y'])
            lore=[anchor['description'],a['line'],
                  'This stationary source-character encounter uses the supplied documents as its history. Dialogue and numerical designation are Stem adaptations.',
                  'No later fate, private biography, or source-world outcome is established by this field encounter.']
            motive={'resident:ed_net':'keep bounded learning distinct from unrestricted access','resident:runehills':'offer a teaching pattern without coercion','resident:resid':'support pilgrims with free provisions','resident:casc':'keep remembered light distinct from a person’s present agreement'}[a['id']]
            token='a local field record';boundary='No claims beyond the documented encounter'
            ch['form']='lightPROKT< concept' if a['id']=='resident:runehills' else 'Other / unspecified'
        ch.update(appearance=appearance,voice=tone,mannerisms=g.choice(['checks a seam before answering','pauses to compare the latest route mark','keeps tools in a repeated order']),bio='\n\n'.join(lore),goal=motive,boundary=boundary)
        a['character']=ch;a.setdefault('faction',g.choice(FACTIONS[cell['region']]))
        a['items']=[dict(name=token,kind='keepsake',effect='personal lore; no permission'),dict(name='field staff',kind='tool',effect='ordinary route protection')]
        a['lore']=lore;a['attitude']=g.randint(45,65);a['personal_reputation']={a['faction']:g.randint(0,4)}
        a['contract_preferences']={'NanoClad Scout':['survey','delivery'],'Metal-kin Artisan':['restoration','delivery'],'Seam Mediator':['diplomacy','delivery'],'Fractech Archivist':['survey','diplomacy'],'Needlurgist':['restoration','survey'],'Light Reader':['survey','diplomacy']}[role]
        a['health']=g.randint(85,100);a['energy']=100;a['inventory']=dict(food=3,water=4,scrap=2,seed=1,medkit=1)
        a['engagement']=dict(phase='observe',cycles=0,last_tick=w['tick'],task='support',events=[],last_work=-20)
        a['owner']=None;a['memory']=[];a['injuries']=[];a['ailments']=[];a['xp']=0;a['credentials']=[];a['loadout']=[]
    a.setdefault('presentation',generation.npc_identity(w['seed'],a))
    chars.ensure(a)
    a.setdefault('owner',None);a.setdefault('memory',[]);a.setdefault('attitude',50)
    return a

def ensure_world(w):
    for a in [*w['actors'],*w.get('residents',{}).values()]:ensure(w,a)
    for p in w['players']:
        p.setdefault('companions',[]);p.setdefault('personal_reputation',{});p.setdefault('check_log',[])
        p['companions']=[a['id'] for a in w['actors'] if a.get('owner')==p['id']]

def spawn_pair(w,engine):
    """Two actual travelers start at the field station; they share the normal registry."""
    x,y=w['spawn']
    local=[a for a in w['actors'] if [a['x'],a['y']]==[x,y]]
    while len(local)<2 and len(w['actors'])<24:
        g=seeded(w,'field-companion:'+str(len(local)))
        a=dict(id='npc_'+hashlib.sha256((w['seed']+':'+str(len(local))).encode()).hexdigest()[:10],
               name=g.choice(['Sela','Neri','Venn','Ari'])+' '+g.choice(['Brace','Thread','Reed','Vale']),
               x=x,y=y,role='repairer' if not local else 'provisioner',need='water',trust=0,
               activity='looking for a reciprocal expedition agreement',last_help=-10)
        w['actors'].append(a);local.append(a)
    ensure_world(w)

def find(w,selector):
    exact=[a for a in w['actors'] if geo.norm(selector)==geo.norm(a['id'])]
    if exact:return exact[0]
    named=[a for a in w['actors'] if geo.norm(selector)==geo.norm(a['name'])]
    if len(named)>1:raise ValueError('That name belongs to several NPCs. Use the designation ID shown in the companion panel.')
    return named[0] if named else None

def attitude(a):
    return 'committed' if a['attitude']>=75 else 'cooperative' if a['attitude']>=50 else 'cautious' if a['attitude']>=30 else 'unwilling'

def event(w,a,text):
    a['engagement']['events'].append(dict(tick=w['tick'],text=text));a['engagement']['events']=a['engagement']['events'][-30:]

def viability(w,p,a):
    ch=a['character'];scores={}
    skills={'survey':'percept','delivery':'fieldcraft','restoration':'metallurgy','diplomacy':'contracts'}
    for kind,skill in skills.items():
        blockers=[]
        if a['health']<35:blockers.append('needs care')
        if a['energy']<15:blockers.append('needs rest')
        if a['attitude']<30:blockers.append('unwilling attitude')
        if field_rules.active(w) and a['engagement']['phase']=='recover':blockers.append('recovery phase')
        cm=p.get('contract')
        faction=cm['faction'] if cm else a['faction']
        if a.get('personal_reputation',{}).get(faction,0)<=-10:blockers.append('faction conflict')
        if kind=='delivery' and (a['inventory']['food']<2 or a['inventory']['water']<1):blockers.append('insufficient personal provisions')
        scores[kind]=dict(viable=not blockers,preferred=kind in a['contract_preferences'],training=ch['skills'].get(skill,0),reasons=blockers or ['ready for scoped expedition support'])
    return scores

def public(w,p,a):
    ensure(w,a)
    return dict(id=a['id'],name=a['name'],role=a['character']['role'],pos=[a['x'],a['y']],faction=a['faction'],
                recruited=a.get('owner')==p['id'],available=a.get('owner') is None,character=copy.deepcopy(a['character']),
                items=copy.deepcopy(a['items']),inventory=a['inventory'].copy(),health=a['health'],energy=a['energy'],
                experience=a['xp'],credentials=a['credentials'][:],equipment=a['loadout'][:],
                injuries=a['injuries'][:],ailments=a['ailments'][:],attitude=a['attitude'],attitude_label=attitude(a),
                engagement=copy.deepcopy(a['engagement']),reputation=a['personal_reputation'].copy(),
                contract_viability=viability(w,p,a),memory=copy.deepcopy(a['memory'][-6:]))

def snapshot(w,p):
    ensure_world(w)
    own=[public(w,p,a) for a in w['actors'] if a.get('owner')==p['id']]
    nearby=[public(w,p,a) for a in w['actors'] if [a['x'],a['y']]==p['pos'] and a.get('owner')!=p['id']]
    return dict(limit=2,roster=own,candidates=nearby,tasks=sorted(TASKS),topics=sorted(TOPICS))

def speech(w,p,a,topic,success,engine):
    ch=a['character'];phase=a['engagement']['phase'];task=a['engagement']['task']
    last=a['engagement']['events'][-1]['text'] if a['engagement']['events'] else 'We have not yet done shared field work.'
    if topic=='lore':body=ch['bio'] if success else a['lore'][0]+' The rest needs a steadier conversation.'
    elif topic=='plans':body=f"I want to {ch['goal']}. I am in my {phase} cycle, with {task} as my current task. {last}"
    elif topic=='contracts':
        v=viability(w,p,a);body='My preferred commitments are '+', '.join(a['contract_preferences'])+'. '+('Your current issuer is '+p['contract']['faction']+'. ' if p.get('contract') else '')+' '.join(k+': '+('ready' if x['viable'] else ', '.join(x['reasons'])) for k,x in v.items())
    elif topic=='factions':body=f"My recorded affiliation is {a['faction']}. Its shared standing with this expedition is {w['reputation'].get(a['faction'],0)}, and your personal standing is {p.get('personal_reputation',{}).get(a['faction'],0)}. My own engagement is {a['personal_reputation']}."
    elif topic=='history':body=f"We have {sum(m.get('actor_id')==p['id'] for m in a['memory'])} identified shared conversations in the retained record. {last} Your current aim is {p['character']['goal'] or 'still unstated'}."
    elif topic=='needs':body=f"Health {a['health']}, energy {a['energy']}. My own pack holds {a['inventory']}. I need care and materials before a difficult promise becomes viable."
    else:body=f"I am {attitude(a)} about this agreement. My limit is {ch['boundary'].lower()}. Trust grows through shared work and provision, not a declared affiliation."
    if not success and topic!='lore':body+=' I can give the public record, but I am not ready to elaborate on its private uncertainties.'
    return generation.dialogue(w,p,a,topic,body,success,engine.local(w,p))

def handle(w,p,intent,raw,engine):
    ensure_world(w);op=intent['action'];target=intent.get('target','');selector,_,detail=target.partition('|')
    a=find(w,selector);engine.require(a is not None,'Choose a traveling NPC from the companion panel.')
    engine.require([a['x'],a['y']]==p['pos'],'The NPC must be physically alongside you.')
    owns=a.get('owner')==p['id'];time=True;mechanics=''
    if op=='recruit':
        engine.require(a.get('owner') is None,'That NPC already has an expedition agreement.')
        engine.require(len(p['companions'])<2,'You may travel alongside at most two NPC companions.')
        if field_rules.active(w):engine.require(sum(bool(a.get('owner')) for a in w['actors'])<2,'The whole party supports two active NPC agreements.')
        engine.require(a['attitude']>=30 and a['health']>=35 and (not field_rules.active(w) or a['energy']>=15),'This NPC is not currently willing or able to travel.')
        engine.require(p['inventory']['food']>=1 and p['inventory']['water']>=1,'A recruitment agreement offers one food and one water.')
        engine.require(w['tick']>=a.get('recruit_after',0),'Give this NPC four cycles before proposing the agreement again.')
        ok,mechanics=engine.check(w,p,'rapport',11,'community',dict(npc=a['id'],faction=a['faction']))
        a['recruit_after']=w['tick']+4
        if ok:
            engine.require(a['inventory']['food']<99 and a['inventory']['water']<99,'The NPC pack needs space for the agreement provisions.')
            for k in ['food','water']:p['inventory'][k]-=1;a['inventory'][k]+=1
            a['owner']=p['id'];p['companions'].append(a['id']);a['attitude']=min(100,a['attitude']+5)
            event(w,a,'Accepted a reciprocal expedition agreement with '+p['name']+'.')
            out=a['name']+' joins your expedition, retaining their own lore, pack, faction relationships and right to withdraw.'
        else:a['attitude']=max(0,a['attitude']-1);out=a['name']+' declines for now. No agreement provisions change hands.'
    elif op=='dismiss':
        engine.require(owns,'Only your own companion can be released from this agreement.');time=False
        _,mechanics=engine.check(w,p,'rapport',8,'community',dict(npc=a['id']))
        a['owner']=None;p['companions'].remove(a['id']);event(w,a,'The expedition agreement was released without taking the NPC’s possessions.')
        out=a['name']+' returns to autonomous local travel with their pack and history.'
    elif op=='npc_talk':
        engine.require(a.get('owner') in {None,p['id']},'That NPC is engaged with another expedition.');time=False
        topic=detail or 'plans';engine.require(topic in TOPICS,'Choose lore, plans, contracts, factions, history, needs or attitude.')
        skill='history' if topic=='lore' else 'contracts' if topic=='contracts' else 'community'
        ok,mechanics=engine.check(w,p,'percept' if topic=='lore' else 'rapport',10,skill,dict(npc=a['id']))
        out=speech(w,p,a,topic,ok,engine)
        import adventure
        out=adventure.note_dialogue(w,p,a,topic,out)
        a['memory'].append(dict(tick=w['tick'],topic=topic,actor_id=p['id'],speaker=p['name'],response=out));a['memory']=a['memory'][-40:]
        if ok and w['tick']>=a.get('bond_after',0):
            p['relationships'][a['id']]['trust']=min(5,p['relationships'][a['id']]['trust']+1)
            a['attitude']=min(100,a['attitude']+1);a['bond_after']=w['tick']+4
    elif op=='npc_task':
        engine.require(owns,'Recruit the NPC before proposing an expedition task.');engine.require(detail in TASKS,'Choose a listed companion task.')
        ok,mechanics=engine.check(w,p,'rapport',10,'teaching',dict(npc=a['id']))
        if ok:a['engagement']['task']=detail;event(w,a,'Agreed to the '+detail+' task.');out=a['name']+' agrees to '+detail+'. Work occurs in the engagement cycle and uses their own materials.'
        else:a['attitude']=max(0,a['attitude']-1);out=a['name']+' keeps their current task and asks for a clearer proposal.'
    elif op in {'share','request'}:
        engine.require(owns,'Share expedition supplies with your own recruited companion.');engine.require(detail in {'food','water','scrap','seed','medkit'},'Choose one listed supply.')
        if op=='share':
            engine.require(p['inventory'].get(detail,0)>0 and a['inventory'][detail]<99,'Both packs must permit the transfer.')
            ok,mechanics=engine.check(w,p,'rapport',9,'community',dict(npc=a['id']))
            p['inventory'][detail]-=1;a['inventory'][detail]+=1;a['attitude']=min(100,a['attitude']+(3 if ok else 1));out='One '+detail+' is transferred to '+a['name']+'; their own pack record is updated.'
        else:
            reserve=1 if detail in {'food','water'} else 0
            engine.require(a['inventory'][detail]>reserve and p['inventory'][detail]<99,'The NPC protects their last ration and needs stock to share.')
            ok,mechanics=engine.check(w,p,'rapport',11,'community',dict(npc=a['id']))
            if ok and a['attitude']>=40:a['inventory'][detail]-=1;p['inventory'][detail]+=1;out=a['name']+' agrees to share one '+detail+' from their personal pack.'
            else:out=a['name']+' keeps that supply for their own viable commitments.'
    elif op=='companion_treat':
        engine.require(owns,'Field care is for your own companion.');engine.require(p['inventory']['medkit']>0,'You need a medkit.')
        engine.require(a['health']<100 or a['injuries'] or a['ailments'],'That companion does not need treatment.')
        p['inventory']['medkit']-=1;ok,mechanics=engine.check(w,p,'tech',10,'medtech',dict(npc=a['id']))
        if ok:
            healing=25+(5 if p.get('last_check',{}).get('grade')=='strong' else 0) if field_rules.active(w) else 30
            a['health']=min(100,a['health']+healing)
            for field in ['injuries','ailments']:
                if a[field]:a[field].pop(0);break
            a['attitude']=min(100,a['attitude']+3);out=f'Care restores {healing} companion health and resolves one condition.'
        else:out='The companion treatment consumes its medkit without resolving the condition.'
    else:return None
    return dict(text=out,mechanics=mechanics,intent=intent,time_spent=time)

def after_action(w,p,intent,time_spent,engine):
    if field_rules.active(w):
        for a in w['actors']:
            if a.get('owner')==p['id']:
                a['x'],a['y']=p['pos'];a['pos']=p['pos'][:]
        return
    helpers={k for r in p.get('_checks',[]) for k in r['helpers']}
    for a in w['actors']:
        if a.get('owner')!=p['id']:continue
        a['x'],a['y']=p['pos'];a['pos']=p['pos'][:]
        if time_spent:
            a['energy']=max(0,a['energy']-(2 if a['id'] in helpers else 1))
            if a['id'] in helpers:event(w,a,'Contributed trained support to '+intent['action']+'.')
            a['travel_actions']=a.get('travel_actions',0)+1
            if a['travel_actions']>=6:
                for supply in ['food','water']:
                    if a['inventory'][supply]>0:a['inventory'][supply]-=1
                    else:a['energy']=max(0,a['energy']-3);a['attitude']=max(0,a['attitude']-2)
                a['travel_actions']=0;event(w,a,'Used available personal rations after six active expedition actions.')
        if intent['action'] in {'fulfill','restore','plant','help'} and p.get('last_check',{}).get('success'):
            if time_spent:a['attitude']=min(100,a['attitude']+1)
        if intent['action']=='fulfill' and p.get('last_check',{}).get('success'):
            previous=p.get('_contract_before',{});faction=previous.get('faction')
            if faction and a['health']>=35 and a['energy']>=15 and a['attitude']>=30:
                a['personal_reputation'][faction]=min(20,a['personal_reputation'].get(faction,0)+1)
                event(w,a,'Recorded shared engagement with '+faction+' after a completed commitment.')
        if intent['action']=='abandon' and p.get('_contract_before',{}).get('kind') in a['contract_preferences']:
            a['attitude']=max(0,a['attitude']-3);event(w,a,'Reconsidered the agreement after a preferred commitment was abandoned.')
        if a['health']<=0:
            a['health']=35;a['engagement']['phase']='recover';event(w,a,'Withdrew from active support for recovery.')

def release_all(w,p):
    for a in w['actors']:
        if a.get('owner')==p['id']:a['owner']=None
    p['companions']=[]

def cycle(w,engine):
    ensure_world(w)
    if w['tick']%4:return
    for a in w['actors']:
        if field_rules.active(w) and any(v.get('encounter',{}).get('combat') and not v['encounter']['combat']['finished'] and a.get('owner') in v['encounter']['combat']['pcs'] for v in w.get('field_sites',{}).values()):continue
        ensure(w,a);e=a['engagement'];p=next((p for p in w['players'] if p['id']==a.get('owner')),None)
        if a.get('owner') and not p:a['owner']=None
        if p:a['x'],a['y']=p['pos'];a['pos']=p['pos'][:]
        c=w['cells'][engine.key(a['x'],a['y'])];e['cycles']+=1;e['last_tick']=w['tick']
        if a['attitude']<20 and p:
            release_id=a['id'];a['owner']=None;p['companions']=[k for k in p['companions'] if k!=release_id]
            event(w,a,'Withdrew voluntarily because the agreement no longer felt viable.');engine.emit(w,a['name']+' withdraws from the expedition agreement.','npc',a['pos'][:]);p=None
        phase=e['phase']
        if a['energy']<15 or a['health']<35:phase='recover'
        if phase=='observe':a['activity']='reading local weather, stores and faction records';event(w,a,'Observed '+c['title']+' with stability '+str(c['stability'])+'.')
        elif phase=='plan':
            a['activity']='weighing scoped work against provisions and attitude'
            if e['task']=='support':e['planned']='repair' if c['stability']<50 and a['inventory']['scrap'] else 'survey'
            else:e['planned']=e['task']
            event(w,a,'Planned '+e['planned']+' within the current physical sector.')
        elif phase=='work':
            task=e.get('planned',e['task']);a['activity']='working on '+task
            if w['tick']-e['last_work']>=12 and a['energy']>=15:
                a['_intent']=dict(action='npc_task',target=task)
                skill={'repair':'metallurgy','forage':'druid','mediate':'contracts','guard':'fieldcraft'}.get(task,'percept')
                stat=chars.SKILLS[skill]['stat'];ok,roll=engine.check(w,a,stat,10,skill,dict(action='restore' if task=='repair' else 'forage' if task=='forage' else 'inspect',faction=a['faction']))
                e['last_work']=w['tick'];a['energy']=max(0,a['energy']-4)
                effect='The work remained unresolved.'
                if ok and task=='repair' and a['inventory']['scrap'] and c['stability']<95:
                    a['inventory']['scrap']-=1;c['stability']=min(100,c['stability']+8);effect='Spent one personal scrap to restore 8 local stability.'
                    engine.record(c,w,a,effect)
                elif ok and task=='forage' and c['food'] and a['inventory']['food']<99:
                    c['food']-=1;a['inventory']['food']+=1;c['pressure']=min(100,c['pressure']+2);effect='Gathered one real local food into the NPC pack.'
                elif ok and task=='mediate':
                    a['personal_reputation'][a['faction']]=min(20,a['personal_reputation'].get(a['faction'],0)+1);effect='Recorded one personal faction engagement after local mediation.'
                elif task=='rest':a['energy']=min(100,a['energy']+12);effect='Reserved the work period for rest.'
                elif ok:effect='Recorded a local '+task+' observation; no item or permission was created.'
                if ok and task!='rest':
                    if field_rules.active(w):field_rules.award(w,a,'work:'+engine.key(a['x'],a['y'])+':'+task)
                    else:a['xp']=min(10000,a['xp']+1)
                event(w,a,effect);a.pop('_intent',None);a.pop('_checks',None)
                if p:engine.emit(w,a['name']+': '+effect+' '+roll,'npc',a['pos'][:])
        elif phase=='reflect':a['activity']='comparing the latest work with a personal unresolved question';event(w,a,'Reconsidered the aim to '+a['character']['goal']+'.')
        else:
            a['activity']='resting and maintaining personal equipment';a['energy']=min(100,a['energy']+(14 if c['shelter'] else 6))
            if c['shelter'] and a['health']<100:a['health']=min(100,a['health']+4)
            event(w,a,'Recovered at '+c['title']+'; shelter '+str(c['shelter'])+'.')
        e['phase']=PHASES[(PHASES.index(phase)+1)%len(PHASES)]
