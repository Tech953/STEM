"""STEM: deterministic biomes and bounded autonomous simulation. Python stdlib."""
import copy
import hashlib
import random
import re
import secrets
import sys
import geography
import characters
import survival
import adventure
import checks
import companions
import institutions
import combat
import generation
import field_rules
import field_adventure

VERSION = '0.5.0'
BUILDS = {
    'Surveyor': dict(body=1, craft=2, percept=4, voice=1),
    'Wayfarer': dict(body=4, craft=1, percept=2, voice=1),
    'Artisan': dict(body=2, craft=4, percept=1, voice=1),
    'Mediator': dict(body=1, craft=1, percept=2, voice=4),
}
REGIONS = {
    'WN_TOWER': dict(title='The roots of the Needle', material='darkwood ash and patched bio-plast', scent='resin smoke and warm metal', sound='the low feedback hum of a distant Greatweb interface', color='ash-dark', source='WN_TOWER Reference / Greatweb, Undercroft.Beta, Harvet Fractlands', faction='Druid-Sec', plants=['neural-wood seedlings','ashroot mats','filament moss'], terrain=['root causeway','ash garden','service hollow','fract-node verge'], features=['sealed service cabinet','splintered darkwood trellis','bio-plast windbreak','fract-node inspection rail']),
    'CITY_CLOUD_S': dict(title='The mountain lattice', material='salvaged metal and pale mineral seams', scent='cold stone and machine oil', sound='a teaching projection repeating a measured interval', color='steel-blue', source='CITY_CLOUD_S / base.EN_KHO, ED.NET', faction='KHO / ED.NET', plants=['wireleaf lichen','terrace moss','mineral-root fans'], terrain=['metal terrace','mountain ledge','salvage court','geometric passage'], features=['bounded lesson projector','salvage sorting frame','condensation gutter','indexed metal panel']),
    'ENACT_HILLS': dict(title='The inhabited foothills', material='worked metallurgy and cultivated earth', scent='cooking smoke and rain-dark soil', sound='household tools striking a patient rhythm beyond the path', color='earth-gold', source='ENACT_HILLS / FOOTHILL CUSP, UPPER RUNEHILLS', faction='FOOTHILL CUSP residents', plants=['hearthgrass','copper-veined reeds','garden filaments'], terrain=['residential verge','terraced garden','craft courtyard','foothill path'], features=['community seed frame','patched irrigation sluice','household repair bench','archival boundary marker']),
    'AETHERGALE': dict(title='The contrail dustlands', material='wind-worked dust and crystalline fragments', scent='dry mineral dust against tent fabric', sound='guy-lines vibrating beneath a distant AETHER current', color='jade and rose', source='AETHERGALE / OMNICUSP, CHECKPOINT.GALE, CHECKPOINT.UNDERTOW', faction='NanoClad', plants=['contrail fans','dustlace colonies','glassroot clusters'], terrain=['tentway hollow','crystalline wash','dust basin','windward shelf'], features=['crystalline survey vane','folded pilgrim canopy','sealed water rack','LYLINE observation stake']),
}
DIRS = {'north':(0,-1),'east':(1,0),'south':(0,1),'west':(-1,0)}
ALIASES = {'n':'north','e':'east','s':'south','w':'west'}
MAX_CELLS = 2048
MAX_COORD = 10000
ACTIONS = ['look','inspect','listen','move','forage','water','salvage','restore','plant','shelter','rest','wait','talk','trade','negotiate','help','contract','survey','inventory','map','remote','return','eat','drink','goto','travel','abandon','fulfill','register','study','install','remove','treat','clinic','provision','dialogue']
ACTIONS += sorted(companions.ACTS | institutions.ACTS | combat.ACTS)
HELP = 'Mapped travel: go to ED.NET; travel next; ask about history; accept delivery contract; fulfill; register; study; treat; clinic; provision. Try: look; inspect the trellis; listen; head north; forage; collect water; salvage; repair the habitat; plant a seed; build shelter; rest; wait; talk to the traveler; negotiate a trade; trade for food; help the traveler; accept a survey contract; survey; eat; drink; remote survey; return. You can also write ordinary sentences using these intentions.'
HELP += ' Companions: recruit NAME; speak with NAME about lore; task NAME repair; share NAME water; care for NAME; dismiss NAME. Institutions: business; buy medkit; sell food; work business; inspect infrastructure; operate infrastructure; build relay. Encounters: attack; shoot; guard; parley; flee.'
standing=checks.standing

def rng(seed, *parts):
    digest=hashlib.sha256(('|'.join(map(str,[seed,*parts]))).encode()).digest()
    return random.Random(int.from_bytes(digest,'big'))

def require(ok, message):
    if not ok: raise ValueError(message)

def clamp(v, lo=0, hi=100): return max(lo,min(hi,v))
def key(x,y): return f'{x},{y}'
def phase(t): return ['dawn','daylight','dusk','night'][(t//6)%4]
def season(t): return ['renewal','dry season','storm season','recovery'][(t//96)%4]
def region_at(x,y,layout='legacy'):
    if layout=='atlas':return geography.info(x,y)['region']
    # Gameplay sectors, not a scale reproduction of the source maps.
    if y<0:return 'WN_TOWER' if x<0 else 'CITY_CLOUD_S'
    return 'ENACT_HILLS' if x<0 else 'AETHERGALE'

def terrain(seed,x,y,layout='legacy'):
    mapped=geography.info(x,y) if layout=='atlas' else None
    g=rng(seed,'terrain',x,y);region=region_at(x,y,layout);r=REGIONS[region]
    return dict(x=x,y=y,region=region,title=g.choice(['Quiet','Split','Low','Weathered','Hollow','Many-branched','Pale','Sheltered'])+' '+g.choice(r['terrain']),
        plant=g.choice(r['plants']),feature=g.choice(r['features']),elevation=g.randint(1,9),moisture=g.randint(25,70),growth=g.randint(20,65),stability=g.randint(45,80),aether=g.randint(15,55),food=g.randint(3,8),water=g.randint(3,9),scrap=g.randint(2,7),shelter=0,pressure=0,fauna=g.randint(1,6))

def emit(w,text,kind='world',coord=None):
    w['serial']+=1
    w['journal'].append(dict(id=w['serial'],tick=w['tick'],kind=kind,text=text,coord=coord))
    w['journal']=w['journal'][-160:]

def new_world(seed=None,layout='atlas',ruleset='field-guide-1'):
    require(layout in ['atlas','legacy'],'Invalid map layout.')
    w=dict(version=VERSION,seed=seed or secrets.token_hex(8),tick=0,serial=0,cells={},actors=[],journal=[],reputation={r['faction']:0 for r in REGIONS.values()},started=False,paused=False,revision=0,players=[],host='',contracts_completed=0)
    require(ruleset in {'legacy','field-guide-1'},'Invalid ruleset.')
    field_rules.ensure_world(w,new=ruleset=='field-guide-1')
    w['layout']=layout;w['spawn']=geography.SPAWN[:] if layout=='atlas' else [0,0];adventure.init(w)
    visit(w,*w['spawn'])
    companions.spawn_pair(w,sys.modules[__name__])
    emit(w,'STEM begins at a new field station among the four corners. Its people, chronology and route network are a sequel adaptation; no THORNS ending is assumed.', 'story')
    return w

def visit(w,x,y):
    k=key(x,y)
    if k not in w['cells']:
        require(len(w['cells'])<MAX_CELLS,'This prototype has reached its 2,048-site save limit. Existing routes remain playable; start another seed for a new expedition.')
        c=terrain(w['seed'],x,y,w.get('layout','legacy'));c.update(visited_at=w['tick'],changes=[],harvested=0)
        mapped=geography.info(x,y) if w.get('layout')=='atlas' else None
        if mapped:
            c['terrain']=mapped['terrain'];c['travel_cost']=mapped['cost'];c['landmark']=mapped['landmark'];
            if mapped['landmark']:
                c['title']=mapped['landmark']['name'];c['shelter']=int('shelter' in mapped['landmark']['services']);c['feature']=mapped['landmark']['name']+' field apparatus'
        if [x,y]==w.get('spawn',[0,0]):c.update(title='The THORNS Encampment / Stem field station' if w.get('layout')=='atlas' else 'The Stem field station',shelter=3,water=18,food=12,scrap=10,stability=85)
        w['cells'][k]=c
        g=rng(w['seed'],'resident',x,y)
        if len(w['actors'])<24 and (g.random()<.38 or [x,y]==w.get('spawn',[0,0])):
            who=g.choice(['Iri','Sen','Vela','Orin','Tavi','Meren','Kest','Ara'])+' '+g.choice(['Reed','Ash','Vane','Thread','Vale'])
            w['actors'].append(dict(id=k,name=who,x=x,y=y,role=g.choice(['route keeper','repairer','provisioner','observer']),need=g.choice(['water','food','scrap']),trust=0,activity='checking a field record',last_help=-10))
        combat.ensure(c,w,sys.modules[__name__])
    generation.ensure_site(w,w['cells'][k])
    return w['cells'][k]

def local(w,p): return visit(w,*p['pos'])
def add_player(w,name,build,character=None):
    require(len(w['players'])<6,'This expedition already has six players.')
    require(isinstance(name,str) and 0<len(name.strip())<=32 and all(ord(c)>=32 for c in name),'Use a name of 1–32 printable characters.')
    require(isinstance(build,str) and (build in BUILDS or build in characters.ROLES),'Choose a valid discipline.')
    sheet=characters.validate(character,build) if character is not None else characters.default(build)
    p=dict(id=secrets.token_hex(6),token=secrets.token_urlsafe(32),name=name.strip(),build=build,character=sheet,pos=w.get('spawn',[0,0])[:],health=100,energy=100,thirst=0,food_need=0,inventory=dict(food=4,water=5,scrap=3,seed=2),xp=0,karma=0,contract=None,notes=[],remote=False,insights=[],last_result='',last_action=None)
    characters.ensure(p);survival.ensure(p);p['route']=[];p['destination']=None
    p['companions']=[];p['personal_reputation']={};p['check_log']=[]
    generation.ensure_player(p)
    if field_rules.active(w):field_rules.ensure_player(p,new=True)
    w['players'].append(p)
    if not w['host']:w['host']=p['id']
    return p

def weather(w,c):
    # Stable in four-tick blocks; shared regional weather, local altitude variation.
    g=rng(w['seed'],'weather',c['region'],w['tick']//4)
    storm_bias=18 if season(w['tick'])=='storm season' else 0
    roll=g.randrange(100)+storm_bias
    return 'particulate storm' if roll>=85 else 'rain' if roll>=58 and c['region']!='AETHERGALE' else 'contrail squall' if roll>=58 else 'dry wind' if roll>=30 else 'still air'

def succession(c):
    if c['stability']<25:return 'fractured habitat'
    if c['growth']<20:return 'depleted verge'
    if c['growth']>70 and c['moisture']>45:return 'flourishing stand'
    if c['pressure']>35:return 'disturbed growth'
    return 'recovering mosaic' if c['growth']>=40 else 'sparse colonization'

def tick(w,reason='autonomous pulse'):
    companions.ensure_world(w)
    w['tick']+=1
    old_moist={k:c['moisture'] for k,c in w['cells'].items()}
    for k,c in w['cells'].items():
        before=succession(c);climate=weather(w,c);storm=climate in ['particulate storm','contrail squall'];rain=climate=='rain'
        neighbors=[old_moist[key(c['x']+dx,c['y']+dy)] for dx,dy in DIRS.values() if key(c['x']+dx,c['y']+dy) in old_moist]
        drift=0 if not neighbors else (1 if sum(neighbors)/len(neighbors)>old_moist[k]+10 else -1 if sum(neighbors)/len(neighbors)<old_moist[k]-10 else 0)
        c['moisture']=clamp(c['moisture']+(7 if rain else -2 if climate=='dry wind' else -1)+drift)
        c['pressure']=clamp(c['pressure']-1)
        c['aether']=clamp(c['aether']+(4 if storm else -1))
        c['growth']=clamp(c['growth']+(2 if c['moisture']>=35 and c['stability']>=35 else -1)-(1 if c['pressure']>35 else 0))
        c['stability']=clamp(c['stability']+(-2 if storm and not c['shelter'] else 1 if c['growth']>55 else 0))
        if w['tick']%6==0:
            c['fauna']=clamp(c['fauna']+(1 if c['growth']>55 and c['moisture']>30 else -1 if c['growth']<25 or storm else 0),0,12)
        if c['fauna']>7:c['growth']=clamp(c['growth']-1)
        if w['tick']%4==0:
            c['food']=clamp(c['food']+(1 if c['growth']>=45 else 0),0,20)
            c['water']=clamp(c['water']+(2 if rain else 0),0,25)
        if w['tick']%24==0 and storm and c['shelter']:c['shelter']-=1
        after=succession(c)
        if before!=after:emit(w,f"{c['title']} changes from {before} to {after}; moisture {c['moisture']}, stability {c['stability']}.",coord=[c['x'],c['y']])
    # Actors have their own needs and bounded local migration; no omniscient planning.
    occupied={(a['x'],a['y']) for a in w['actors']}
    for a in w['actors']:
        c=w['cells'][key(a['x'],a['y'])]
        if not a.get('owner') and w['tick']%6==0 and c.get(a['need'],0)>0:
            c[a['need']]-=1;a['activity']='sharing provisions' if a['need'] in ['food','water'] else 'maintaining a tool'
        if not a.get('owner') and w['tick']%8==0:
            candidates=[w['cells'][key(a['x']+dx,a['y']+dy)] for dx,dy in DIRS.values() if key(a['x']+dx,a['y']+dy) in w['cells'] and (a['x']+dx,a['y']+dy) not in occupied]
            if candidates and (c['stability']<40 or c.get(a['need'],0)<2):
                dest=max(candidates,key=lambda t:t['stability']+t.get(a['need'],0)*3)
                if dest['stability']+dest.get(a['need'],0)*3>c['stability']+c.get(a['need'],0)*3:
                    occupied.discard((a['x'],a['y']));a['x'],a['y']=dest['x'],dest['y'];a['pos']=[a['x'],a['y']];occupied.add((a['x'],a['y']));a['activity']='seeking a steadier supply route'
                    emit(w,f"{a['name']} leaves {c['title']} for {dest['title']}, seeking {a['need']} and safer ground.",coord=[a['x'],a['y']])
    companions.cycle(w,sys.modules[__name__]);institutions.cycle(w,sys.modules[__name__])
    if w['tick']%4==0:emit(w,f"{phase(w['tick']).capitalize()} in the {season(w['tick'])}. Regional weather fronts shift; travelers reassess their supplies.")
    w['revision']+=1

def describe(w,p):
    c=local(w,p);r=REGIONS[c['region']];g=rng(w['seed'],'prose',*p['pos'],w['tick']//4)
    if p['remote']:
        return '\n\n'.join([
            'REMOTE PERCEPT / UNVERIFIED. Your body remains at '+c['title']+'. A survey apparatus presents an interpretation of distant NULL_FIELD.OMNI reports; this is not passage through RED>GATE>.',
            g.choice(['A tesseract-like contour folds across the received field. Its apparent dimensions disagree between successive observations; a fort-sized outline closes into something that seems no larger than a brick.','A signpost-like figure holds writing whose spacing changes while you read. The frame resembles a familiar contract board, but neither its destinations nor the identities behind its offers can be verified.','Helical sections seem to absorb residual light. You can count their edges in one observation and lose the correspondence in the next; the report does not establish what lies inside.']),
            'Jade and rose echoes recall the documented contrails. That resemblance is an observation, not evidence of a safe route or a known mechanism. Type “return” to lower the apparatus; ordinary travel and gathering are unavailable while observing.'
        ])
    moisture='damp enough to hold a clear footprint' if c['moisture']>55 else 'dry enough to scatter under a heel' if c['moisture']<25 else 'cool beneath a thin surface crust'
    growth=f"{c['plant'].capitalize()} {'crowds the edges in dense interlocking growth' if c['growth']>65 else 'persists in broken islands between exposed surfaces' if c['growth']<30 else 'threads through gaps in an uneven patchwork'}."
    construction=f"The {c['feature']} stands {'firm, with its joints recently checked' if c['stability']>65 else 'under strain; fine misalignments interrupt its silhouette' if c['stability']<35 else 'serviceable but weather-marked, with repairs from more than one hand'}."
    mapped=adventure.landmark(w,p);keeper=adventure.resident(w,p)
    residents=([keeper] if keeper else [])+[a for a in w['actors'] if [a['x'],a['y']]==p['pos']]
    social=' '.join(a.get('description',f"{a['name']}, a {a['role']}, is {a['activity']}.")+f" Their attention returns to the supply of {a['need']}." for a in residents) or 'No traveler is present. The field record contains no claim that the route ahead is unoccupied.'
    resources=f"At survey scale, available stores show food {c['food']}, water {c['water']}, salvage {c['scrap']}. " + ('A constructed shelter breaks the wind.' if c['shelter'] else 'No maintained shelter has been recorded here.')
    memory=('Recent traces: '+' '.join(c['changes'][-2:])) if c['changes'] else 'The surface carries older repairs, but no action from this expedition has yet been recorded here.'
    threat=combat.ensure(c,w,sys.modules[__name__])
    if threat and not threat['resolved']:memory+=f" A {threat['name']} is {threat['intent']}; condition {threat['health']}. Inspect, guard, parley, engage, or withdraw."
    personal=characters.ensure(p);companions=[a for a in w['players'] if a['id']!=p['id'] and a['pos']==p['pos']]
    character_traces=' '.join(a['name']+' is present: '+(characters.ensure(a)['appearance'] or characters.ensure(a)['form'])+'.' for a in companions)
    detail=generation.describe_site(w,c,phase(w['tick']),weather(w,c))
    return '\n\n'.join([
        (mapped['description']+' Route placement: '+mapped['confidence']+'. ' if mapped else '')+f"It is {phase(w['tick'])} in the {season(w['tick'])}. {c['title']} opens through {r['material']}; {weather(w,c)} moves across the {r['color']} scene. Underfoot, the ground is {moisture}.",
        f"You notice {r['scent']}. Under it runs {r['sound']}. {growth} {construction}",
        detail,
        f"The habitat is a {succession(c)}. "+('Small forager traces cross the undergrowth repeatedly; concentrated grazing slows the newest shoots. ' if c['fauna']>7 else 'Sparse forager tracks interrupt the surface, disappearing under the next fold of growth. ' if c['fauna'] else 'No recent forager tracks register in the field survey. ')+f"{resources} {social} {character_traces}",
        memory+(' Place names and source characters follow the supplied references; route placement, dialogue and current ecology are Stem adaptations.' if mapped else ' This site and its inhabitants are generated sequel material; regional motifs come from '+r['source']+'.')
    ])

def parse(text):
    require(isinstance(text,str) and 0<len(text.strip())<=1200,'Write an action of 1–1,200 characters.')
    simple={'full rest':'field_rest','breather':'field_breather','spend a watch':'field_watch','end turn':'field_end'}
    if text.lower().strip() in simple:return dict(action=simple[text.lower().strip()],target=''),None
    if re.search(r"\b(do not|don't|never|avoid|what if|what happens|can i|could i|should i)\b",text.lower()):
        return None,'That reads as a question or a negated intention. No action was taken. State one direct intention, or use look to review the scene.'
    if re.search(r'\band\b',text.lower()):
        return None,'Please submit one intention at a time so each consequence is clear.'
    s=text.lower().strip();s=re.sub(r'[^\w\s\-]',' ',s);s=' '.join(s.split())
    # Multiple instructions never silently become an unintended partial action.
    if re.search(r'\b(then|afterwards|and then)\b',s):return None,'Please submit one action at a time so you can see its consequences.'
    if re.search(r'\b(cross|enter|breach|bypass)\b.*\b(red|gate|admin|restricted)\b',s):return None,'This prototype does not grant entry through RED>GATE> or restricted institutions. Try “remote survey”.'
    m=re.search(r'\b(?:speak|talk) (?:with|to) (.+?) about (lore|plans|contracts|factions|history|needs|attitude)$',s)
    if m:return dict(action='npc_talk',target=m.group(1)+'|'+m.group(2)),None
    m=re.search(r'\b(recruit|dismiss) (.+)$',s)
    if m:return dict(action=m.group(1),target=m.group(2)),None
    m=re.search(r'\btask (.+?) (support|survey|repair|forage|guard|mediate|rest)$',s)
    if m:return dict(action='npc_task',target=m.group(1)+'|'+m.group(2)),None
    m=re.search(r'\b(share|request) (.+?) (food|water|scrap|seed|medkit)$',s)
    if m:return dict(action=m.group(1),target=m.group(2)+'|'+m.group(3)),None
    m=re.search(r'\bcare for (.+)$',s)
    if m:return dict(action='companion_treat',target=m.group(1)),None
    for op,pattern in [('business_work',r'\b(work|maintain) (?:the )?business\b'),('business',r'\b(business|shop|exchange ledger)\b'),('relay',r'\b(build|maintain) (?:a |the )?relay\b'),('operate',r'\boperate (?:the )?infrastructure\b'),('infrastructure',r'\binfrastructure\b')]:
        if re.search(pattern,s):return dict(action=op,target=''),None
    m=re.search(r'\b(buy|sell) (?:a |one |some )?(food|water|seed|medkit)$',s)
    if m:return dict(action=m.group(1),target=m.group(2)),None
    for op in ['attack','shoot','guard','parley','flee']:
        if re.search(r'\b'+op+r'\b',s):
            target=re.sub(r'^.*?\b'+op+r'\b\s*','',s)
            return dict(action=op,target=target),None
    if s in ALIASES:return dict(action='move',target=ALIASES[s]),None
    for direction in DIRS:
        if s==direction or re.search(r'\b(go|walk|head|travel|move|continue|wander)\b.*\b'+direction+r'\b',s):return dict(action='move',target=direction),None
    m=re.search(r'\b(?:go to|route to|navigate to|travel to|head to)\s+(.+)$',s)
    if m:return dict(action='goto',target=m.group(1)),None
    m=re.search(r'\bask (?:about|regarding)\s+(place|routes|needs|contract|history|access)\b',s)
    if m:return dict(action='dialogue',target=m.group(1)),None
    m=re.search(r'\b(install|remove)\s+(?:mod\s+)?(.+)$',s)
    if m:
        mod=next((k for k,v in characters.EQUIPMENT.items() if geography.norm(m.group(2)) in [geography.norm(k),geography.norm(v['label'])]),m.group(2).replace(' ','_'))
        return dict(action=m.group(1),target=mod),None
    patterns=[
      ('abandon',r'\b(abandon|cancel commitment)\b'),('fulfill',r'\b(fulfill|complete contract|turn in contract)\b'),('register',r'\b(register|registration)\b'),('study',r'\b(study|train|learn)\b'),('treat',r'\b(treat|use medkit|bandage)\b'),('clinic',r'\b(clinic|seek care|medical treatment)\b'),('provision',r'\b(provision|pilgrim supplies)\b'),('travel',r'\b(travel next|follow route|continue route|next step)\b'),
      ('return',r'\b(return|lower the apparatus|end projection)\b'),
      ('remote',r'\b(remote|projection|distant percept)\b'),
      ('contract',r'\b(contract|commission|job)\b'),
      ('survey',r'\b(survey|record the habitat|document the habitat)\b'),
      ('water',r'\b(collect|gather|find|filter|draw)\b.*\bwater\b'),
      ('shelter',r'\b(build|construct|erect|make)\b.*\b(shelter|camp|canopy)\b'),
      ('restore',r'\b(repair|restore|stabilize|mend|rehabilitate)\b'),
      ('plant',r'\b(plant|sow|seed the)\b'),
      ('forage',r'\b(forage|gather food|find food|harvest food)\b'),
      ('salvage',r'\b(salvage|scavenge|gather scrap)\b'),
      ('negotiate',r'\b(negotiate|bargain)\b'),
      ('trade',r'\b(trade|barter|buy)\b'),
      ('help',r'\b(help|assist|donate|give)\b'),
      ('talk',r'\b(talk|speak|ask|negotiate|greet)\b'),
      ('eat',r'\b(eat|consume food)\b'),('drink',r'\b(drink)\b'),
      ('rest',r'\b(rest|sleep|recover)\b'),('wait',r'\b(wait|watch time|pass time)\b'),
      ('listen',r'\b(listen|hear)\b'),('inventory',r'\b(inventory|backpack|supplies)\b'),
      ('map',r'\b(map|routes|where am i)\b'),('inspect',r'\b(inspect|examine|touch|observe)\b'),
      ('look',r'\b(look|describe|surroundings|help commands)\b'),
    ]
    for action,pattern in patterns:
        if re.search(pattern,s):
            target=next((v for v in ['food','water','scrap','seed'] if re.search(r'\b'+v+r'\b',s)),'')
            if action=='contract':target=next((k for k in ['survey','delivery','restoration','diplomacy'] if k in s),'survey')
            return dict(action=action,target=target),None
    return None,'I could not map that intention to a supported world action. No time or resources were spent. '+HELP

def check(w,p,stat,dc,skill=None,context=None):
    canonical={'craft':'tech','voice':'rapport'}.get(stat,stat)
    skill=skill or {'body':'fieldcraft','tech':'metallurgy','percept':'percept','rapport':'contracts'}[canonical]
    return checks.resolve(w,p,canonical,dc,skill,sys.modules[__name__],context)

def record(c,w,p,text):
    c['changes'].append(f"At cycle {w['tick']}, {p['name']} {text}");c['changes']=c['changes'][-12:]

def present_actor(w,p):
    keeper=adventure.resident(w,p)
    if keeper:return keeper
    return next((a for a in w['actors'] if [a['x'],a['y']]==p['pos']),None)

def act(w,p,intent,raw='',following_route=False):
    adventure.init(w)
    companions.ensure_world(w)
    action=intent.get('action');target=intent.get('target','');require(action in ACTIONS or action in field_rules.ACTS,'Unsupported action.')
    require(w['started'],'The host must begin the expedition.');require(not w['paused'],'The host has paused this world.')
    if p['remote']:
        require(action in ['return','look','inspect','listen','map','inventory','remote','study'],'Lower the remote apparatus with “return” before acting in the physical world.')
    if field_rules.active(w):
        if action in field_rules.ACTS:return field_adventure.run(w,p,action,target,sys.modules[__name__])
        integrated=field_adventure.native(w,p,intent,sys.modules[__name__])
        if integrated is not None:return integrated
        require(not field_rules.current(w,p) or action in {'look','inspect','listen','inventory','map','dismiss'},'Finish the active field encounter before ordinary work.')
        field_rules.begin_action(p);p['_field_xp_before']=p.get('xp',0)
    c=local(w,p);inv=p['inventory'];time_cost=True;out='';mechanics=''
    p['_intent']=intent.copy();p['_checks']=[];p['_contract_before']=copy.deepcopy(p.get('contract') or {})
    for module in [companions,institutions,combat]:
        if action in module.ACTS:
            integrated=module.handle(w,p,intent,raw,sys.modules[__name__])
            return finish(w,p,intent,raw,integrated['text'],integrated['mechanics'],integrated['time_spent'])
    integrated=adventure.handle(w,p,intent,raw,sys.modules[__name__]) if action in adventure.ACTS else None
    if integrated is not None:
        if integrated.get('already_finalized'):return integrated
        return finish(w,p,intent,raw,integrated['text'],integrated['mechanics'],integrated['time_spent'])
    if action in ['look','inspect','listen','inventory','map']:
        time_cost=False
        if action=='inspect':out=describe(w,p)+f"\n\nMeasured field indices: moisture {c['moisture']}, growth {c['growth']}, stability {c['stability']}, AETHER pressure {c['aether']}. These are game-scale readings, not source-defined measurements."
        elif action=='listen':out='Through the apparatus, scale and distance remain uncertain.' if p['remote'] else f"You stand still and distinguish {REGIONS[c['region']]['sound']} from {weather(w,c)}. Observation alone does not disturb this habitat."
        elif action=='inventory':out='Field pack: '+', '.join(f'{k} {v}' for k,v in inv.items())+'.'
        elif action=='map':out=f"Position {p['pos']}; {len(w['cells'])} recorded sites. Each grid step is one survey sector, not a canonical distance. North decreases Y."
        else:out=describe(w,p)
    elif action=='move':
        require(target in DIRS,'Choose north, east, south, or west.');dx,dy=DIRS[target];x,y=p['pos'];require(max(abs(x+dx),abs(y+dy))<=MAX_COORD,'You have reached this prototype’s coordinate boundary.')
        if w.get('layout')=='atlas':require(geography.info(x+dx,y+dy)['passable'],'This sector is water, outside the drawing, or the RED>GATE> barrier. Choose a mapped land route or bridge.')
        if field_rules.active(w):require(not field_rules.bulk(p)['blocked'],'Transfer supplies before moving a load over twice capacity.')
        if not following_route:p['route']=[];p['destination']=None
        dest=visit(w,x+dx,y+dy);p['pos']=[x+dx,y+dy];out='You follow a surveyed connection '+target+' into '+dest['title']+'.'
        storm=weather(w,dest) in ['particulate storm','contrail squall'] and not dest['shelter']
        ok,mechanics=check(w,p,'body',12 if storm else 10,'transversal',dict(from_pos=[x,y]))
        if storm:
            if not ok:
                p['health']=clamp(p['health']-8);survival.harm(p,'strained leg');
                if 'filter_graft' not in p['loadout'] or 'black.dot' not in p['credentials']:survival.harm(p,'particulate irritation',True)
                out+=' The exposed crossing costs 8 health and records a strained leg; unfiltered exposure may cause irritation.'
        elif not ok:p['energy']=clamp(p['energy']-2);out+=' An awkward crossing costs two additional energy.'
    elif action in ['forage','water','salvage']:
        resource={'forage':'food','water':'water','salvage':'scrap'}[action];require(c[resource]>0,f'No accessible {resource} remains here. Explore or allow the habitat to recover.')
        stat,skill,dc=checks.DEFAULTS[action];ok,mechanics=check(w,p,stat,dc,skill)
        if ok:
            amount=min(2,c[resource]);require(inv[resource]+amount<=99,'Your pack cannot hold more of this resource.');c[resource]-=amount;inv[resource]+=amount;p['xp']+=1;c['pressure']=clamp(c['pressure']+4);c['harvested']+=amount
            if resource=='food':c['growth']=clamp(c['growth']-3)
            out=f'You gather {amount} {resource}. The site’s accessible stock diminishes.';record(c,w,p,f'gathered {amount} {resource}.')
        else:out='You stop before committing to an unreliable source. The attempt takes time but yields no supplies.'
    elif action in ['restore','plant','shelter']:
        resource='seed' if action=='plant' else 'scrap';cost=2 if action=='shelter' else 1
        require(inv[resource]>=cost,f'You need {cost} {resource}.')
        if action=='shelter':require(c['shelter']<3,'The local shelter is already fully maintained.')
        if action=='restore':require(c['stability']<95,'The habitat is already stable enough; save your materials.')
        if action=='plant':require(c['growth']<90,'This stand is already dense enough; seek depleted ground.')
        inv[resource]-=cost;stat,skill,dc=checks.DEFAULTS[action];ok,mechanics=check(w,p,stat,dc,skill)
        if ok:
            if action=='restore':c['stability']=clamp(c['stability']+18);c['pressure']=clamp(c['pressure']-12)
            elif action=='plant':c['growth']=clamp(c['growth']+16);c['moisture']=clamp(c['moisture']-4)
            else:c['shelter']+=1
            adventure.after_work(w,p,action,True)
            p['xp']+=1;p['karma']=clamp(p['karma']+1,-100,100);f=REGIONS[c['region']]['faction'];standing(w,p,f,1)
            out={'restore':'You stabilize the habitat and reduce disturbance.','plant':'You establish a new planted patch. Its future depends on moisture and stability.','shelter':'You raise or reinforce a shared shelter. Storm exposure here is reduced.'}[action];record(c,w,p,out)
        else:out='The work does not hold. Its materials are spent; the habitat retains its prior condition.'
    elif action in ['eat','drink']:
        resource='food' if action=='eat' else 'water';require(inv[resource]>0,f'You have no {resource}.');inv[resource]-=1
        ok,mechanics=check(w,p,'body',8,'fieldcraft');field='food_need' if action=='eat' else 'thirst';p[field]=clamp(p[field]-(45 if ok else 35));p['energy']=clamp(p['energy']+8);out=f'You use one {resource} and reduce your {field.replace("_"," ")}. '+('The preparation holds well.' if ok else 'An inefficient preparation leaves some need unresolved.')
    elif action=='rest':
        require(c['shelter']>0,'Find or build a shelter before resting.');ok,mechanics=check(w,p,'body',8,'fieldcraft');p['energy']=clamp(p['energy']+(35 if ok else 25));p['sleep']=0;p['health']=clamp(p['health']+(15 if ok else 8));out='You rest behind a maintained windbreak. You regain energy and health; the world continues to move.'
    elif action=='wait':out='You let a world cycle pass without intervening.'
    elif action in ['talk','trade','negotiate','help']:
        a=present_actor(w,p);require(a is not None,'No traveler is currently here. They may have moved to seek supplies or safer ground.')
        if action=='talk':
            time_cost=False;out=f"{a['name']} says: ‘I keep an eye on {a['need']}. When the ground will not hold, I follow a safer provision route. If you want to help, bring one {a['need']}.’ Their trust in you is {a['trust']}. This dialogue is generated from their current need."
        elif action=='negotiate':
            require(w['tick']>=a.get('next_offer',0),'This traveler is not ready to reconsider an offer. Wait a few cycles.')
            faction=a.get('faction',REGIONS[c['region']]['faction'])
            ok,mechanics=check(w,p,'voice',12,'contracts',dict(npc=a['id'],faction=faction));a['next_offer']=w['tick']+6
            if ok:
                p['bargain']=dict(actor=a['id'],expires=w['tick']+5);p['xp']+=1
                out=f"{a['name']} agrees to one exchange of two food or water for one scrap, if local stock permits. The offer lasts five cycles."
            else:out=f"{a['name']} keeps the ordinary terms. No supplies change hands."
        elif action=='trade':
            require(target in ['food','water','seed'],'Specify “trade for food”, “trade for water”, or “trade for seed”.');require(inv['scrap']>=1,'Barter costs one scrap.')
            offer=p.get('bargain',{});amount=2 if target!='seed' and offer.get('actor')==a['id'] and offer.get('expires',-1)>=w['tick'] else 1
            require(inv[target]+amount<=99,'Your pack is full for that resource.')
            if target!='seed':require(c[target]>=amount,f'Not enough local {target} is available for this exchange.');c[target]-=amount
            else:require(c['growth']>=30,'This habitat cannot spare seeds yet.');c['growth']-=3
            ok,mechanics=check(w,p,'rapport',10,'contracts',dict(npc=a['id']))
            if ok:
                inv['scrap']-=1;inv[target]+=amount
                if amount==2:p.pop('bargain',None)
                out=f"You exchange one scrap for {amount} {target} with {a['name']}."
            else:
                if target!='seed':c[target]+=amount
                else:c['growth']+=3
                out='The barter remains unconfirmed; no goods or scrap change hands.'
        else:
            require(inv[a['need']]>=1,f"They need one {a['need']}.");require(w['tick']-a['last_help']>=4,'They have what they need for now. Check back after four cycles.')
            rel=p['relationships'].setdefault(a['id'],dict(visits=0,trust=0,last_topic='',introduced=False));rel['trust']=min(5,rel['trust']+1)
            ok,mechanics=check(w,p,'rapport',9,'community',dict(npc=a['id']));faction=a.get('faction',REGIONS[c['region']]['faction']);standing(w,p,faction,1 if ok else 0)
            inv[a['need']]-=1;c[a['need']]=clamp(c[a['need']]+1,0,25);a['trust']=min(5,a['trust']+1);a['last_help']=w['tick'];p['karma']=clamp(p['karma']+1,-100,100);out=f"You give {a['name']} one {a['need']}; their local supply improves."
    elif action=='contract':
        require(p['contract'] is None,'You already carry a survey commitment. Reach its target and type “survey”.')
        x,y=p['pos'];g=rng(w['seed'],'contract',p['id'],w['contracts_completed'],w['tick']);dx,dy=g.choice([(2,1),(-2,1),(1,-2),(-1,-2)])
        require(max(abs(x+dx),abs(y+dy))<=MAX_COORD,'No contract target is available beyond the survey boundary.')
        ok,mechanics=check(w,p,'rapport',11,'contracts')
        if ok:p['contract']=dict(target=[x+dx,y+dy],faction=REGIONS[c['region']]['faction'],reward='2 seeds, 2 food, 2 water, 2 XP');out=f"A new generated field commission asks for an honest habitat survey at {p['contract']['target']}. Reward: {p['contract']['reward']}."
        else:out='The proposed commitment needs clearer terms. Nothing is accepted.'
    elif action=='survey':
        contract=p['contract'];require(contract is not None and p['pos']==contract['target'],'Reach the coordinates on your accepted survey contract first.')
        require(all(inv[k]<=97 for k in ['seed','food','water']),'Make room for the survey reward in your pack.')
        ok,mechanics=check(w,p,'percept',10)
        if ok:
            for resource in ['seed','food','water']:inv[resource]+=2
            p['xp']+=2;standing(w,p,contract['faction'],2);w['contracts_completed']+=1;p['contract']=None;out='You submit the observations with their uncertainties intact and receive the recorded reward.'
        else:out='The readings do not yet agree. Your commitment remains open; a later survey may resolve it.'
    elif action=='remote':p['remote']=True;time_cost=False;out=describe(w,p)
    elif action=='return':require(p['remote'],'You are already observing the physical world.');p['remote']=False;time_cost=False;out='You lower the apparatus. Your physical coordinates have not changed.'
    return finish(w,p,intent,raw,out,mechanics,time_cost)

def finish(w,p,intent,raw,out,mechanics,time_cost):
    action=intent['action']
    if field_rules.active(w):out+=field_adventure.settle_progression(w,p,intent)
    if not mechanics and not (field_rules.active(w) and action in field_rules.FREE):
        stat,skill,dc=checks.DEFAULTS.get(action,('percept','percept',10))
        ok,mechanics=check(w,p,stat,dc,skill)
        if action in {'look','inspect','listen','remote'}:
            out+=' '+('Your trained reading distinguishes the current working context.' if ok else 'Confirmed records remain readable; deeper interpretation is uncertain.')
    observed=[*w['actors'],*w.get('residents',{}).values()]
    generation.witness(w,p,intent,local(w,p),observed,p.get('last_check',{}).get('success'))
    companions.after_action(w,p,intent,time_cost,sys.modules[__name__])
    if time_cost:
        cycles=local(w,p).get('travel_cost',1) if action in {'move','flee'} else 1
        if field_rules.active(w):
            before=p['health'];field_adventure.advance(w,p,cycles,sys.modules[__name__]);rescued=before==0
        else:
            rescued=survival.advance(w,p,cycles)
            for _ in range(cycles):tick(w,'player action')
        if rescued:out+=' Field-station recovery returns you to '+str(p['pos'])+'. Injuries and ailments remain. This prototype has no permadeath.'
        companions.after_action(w,p,intent,False,sys.modules[__name__])
    p.pop('_intent',None);p.pop('_checks',None);p.pop('_contract_before',None)
    p['last_result']=out;p['last_action']=dict(action=action,target=intent.get('target',''),input=raw,mechanics=mechanics,tick=w['tick'])
    if action not in ['look','inspect','listen','map','inventory'] or mechanics:emit(w,p['name']+': '+out+(' '+mechanics if mechanics else ''),'dialogue' if action in ['talk','dialogue'] else 'action',p['pos'][:])
    w['revision']+=1
    return dict(text=out,mechanics=mechanics,intent=intent,time_spent=time_cost)

def snapshot(w,p):
    adventure.init(w)
    companions.ensure_world(w)
    c=local(w,p);x,y=p['pos'];cells=[]
    for dy in range(-3,4):
        for dx in range(-3,4):
            found=w['cells'].get(key(x+dx,y+dy));cells.append(dict(x=x+dx,y=y+dy,known=bool(found),title=found['title'] if found else 'Unsurveyed',region=found['region'] if found else None,shelter=found['shelter'] if found else 0,players=[a['name'] for a in w['players'] if a['pos']==[x+dx,y+dy]]))
    opportunities=[]
    if not p['remote']:
        if c['stability']<50:opportunities.append(dict(text='The habitat is losing its structural margin.',command='repair the habitat'))
        if c['growth']<40:opportunities.append(dict(text='Gaps in the stand leave room for careful planting.',command='plant a seed'))
        if c['shelter']==0:opportunities.append(dict(text='This route has no maintained refuge from storms.',command='build shelter'))
        if c['water']<3:opportunities.append(dict(text='Accessible water is nearly exhausted; look for another route.',command='map'))
        if present_actor(w,p):opportunities.append(dict(text='A traveler’s current needs may connect you to this place.',command='talk to the traveler'))
        if p['contract'] and p['pos']==p['contract']['target']:opportunities.insert(0,dict(text='You have reached your '+p['contract'].get('kind','survey')+' commitment.',command='fulfill' if p['contract'].get('kind') else 'survey'))
    else:opportunities.append(dict(text='Only the received percept is available here; the physical route remains unchanged.',command='return'))
    result=dict(character_sheet=characters.sheet(p),atlas=geography.public(p) if w.get('layout')=='atlas' else None,dialogue_options=adventure.topics(w,p),contract_options=adventure.board(w,p),local_services=(adventure.landmark(w,p) or {}).get('services',[]),version=VERSION,code=w['code'],revision=w['revision'],tick=w['tick'],phase=phase(w['tick']),season=season(w['tick']),started=w['started'],paused=w['paused'],host=w['host'],me={k:copy.deepcopy(v) for k,v in p.items() if k!='token'},players=[{k:copy.deepcopy(a[k]) for k in ['id','name','build','pos','remote']} for a in w['players']],location=copy.deepcopy(c),description=describe(w,p),weather=weather(w,c),succession=succession(c),map=cells,actors=([copy.deepcopy(adventure.resident(w,p))] if adventure.resident(w,p) else [])+[copy.deepcopy(a) for a in w['actors'] if [a['x'],a['y']]==p['pos']],journal=w['journal'][-50:],reputation=w['reputation'],discovered=len(w['cells']),help=HELP,opportunities=opportunities)
    result['companions']=companions.snapshot(w,p);result['business']=institutions.public(w,p,sys.modules[__name__]);result['threat']=None if field_rules.active(w) else combat.public(c)
    result['field_guide']=field_rules.public(w,p,c)
    return result
