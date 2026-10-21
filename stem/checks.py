"""One transparent resolver for skill, situation, standing and expedition support."""
import copy
import characters

SOCIAL = {'talk','dialogue','negotiate','trade','contract','fulfill','recruit','npc_talk','npc_task','buy','sell','business','business_work','parley','clinic','register','share','request','help','dismiss','abandon','provision'}
DEFAULTS = {
    'move':('body','transversal',10), 'goto':('percept','fieldcraft',9),
    'forage':('percept','druid',10), 'water':('percept','resource',10),
    'salvage':('tech','metallurgy',10), 'restore':('tech','fractech',9),
    'plant':('tech','druid',9), 'shelter':('tech','metallurgy',9),
    'talk':('rapport','community',10), 'dialogue':('rapport','teaching',10),
    'contract':('rapport','contracts',11), 'fulfill':('rapport','contracts',10),
    'trade':('rapport','contracts',10), 'help':('rapport','community',9),
    'register':('rapport','contracts',10), 'install':('tech','needlurgy',11),
    'remove':('tech','needlurgy',9), 'clinic':('rapport','community',9),
    'provision':('rapport','community',8), 'rest':('body','fieldcraft',8),
    'eat':('body','fieldcraft',8), 'drink':('body','fieldcraft',8),
    'remote':('percept','nullsurvey',11), 'return':('percept','nullsurvey',8),
    'inventory':('percept','resource',8), 'map':('percept','fieldcraft',8),
    'abandon':('rapport','contracts',8), 'dismiss':('rapport','community',8),
    'wait':('percept','percept',8), 'listen':('percept','percept',10),
    'look':('percept','percept',9), 'inspect':('percept','percept',10),
}

def standing(w, subject, faction, amount):
    w['reputation'][faction] = max(-20,min(20,w['reputation'].get(faction,0)+amount))
    rep = subject.setdefault('personal_reputation',{})
    rep[faction] = max(-20,min(20,rep.get(faction,0)+amount))

def resolve(w, subject, stat, dc, skill, engine, context=None):
    context = context or {}
    stat = {'craft':'tech','voice':'rapport'}.get(stat,stat)
    action = context.get('action',subject.get('_intent',{}).get('action','inspect'))
    c = w['cells'][engine.key(*subject.get('pos',[subject.get('x',0),subject.get('y',0)]))]
    npc = next((a for a in [*w['actors'],*w.get('residents',{}).values()] if a['id']==context.get('npc')),None)
    faction = context.get('faction') or (npc.get('faction') if npc else None) or engine.REGIONS[c['region']]['faction']
    if action in {'fulfill','survey'} and subject.get('contract'):
        faction = context.get('faction') or subject['contract']['faction']
    parts = characters.bonus(subject,stat,skill)
    reputation = max(-2,min(2,int((w['reputation'].get(faction,0)+subject.get('personal_reputation',{}).get(faction,0)/2)/5)))
    reasons = []
    situation = 0
    climate = engine.weather(w,c)
    if action not in SOCIAL:
        if engine.phase(w['tick'])=='night': situation-=1; reasons.append('night −1')
        if climate in {'particulate storm','contrail squall'} and not c['shelter']:
            situation-=2; reasons.append('exposure −2')
        if c['stability']<35: situation-=1; reasons.append('unstable ground −1')
        if c['shelter']: situation+=1; reasons.append('shelter +1')
        if c.get('relay',0)>0: situation+=1; reasons.append('maintained relay +1')
        if action in {'forage','plant','water'} and c['growth']>65:
            situation+=1; reasons.append('healthy habitat +1')
    else:
        if c['stability']<35: situation-=1; reasons.append('local disruption −1')
        if climate in {'particulate storm','contrail squall'}: situation-=1; reasons.append('storm pressure −1')
    situation += context.get('modifier',0)
    if context.get('reason'): reasons.append(context['reason'])
    situation = max(-3,min(3,situation))
    trust = min(1,subject.get('relationships',{}).get(npc['id'],{}).get('trust',0)//3) if npc else 0
    attitude = (1 if npc.get('attitude',50)>=70 else -1 if npc.get('attitude',50)<30 else 0) if npc else 0
    helpers = []
    for ally in w['actors']:
        if ally.get('owner')!=subject.get('id') or ally['id']==context.get('npc'): continue
        beside=[ally['x'],ally['y']]==subject.get('pos') or (action=='move' and [ally['x'],ally['y']]==context.get('from_pos'))
        if not beside or ally.get('health',100)<35 or ally.get('energy',100)<15: continue
        if ally.get('engagement',{}).get('phase')=='recover' or ally.get('attitude',50)<30: continue
        if subject.get('contract') and action in {'fulfill','survey'} and ally.get('personal_reputation',{}).get(faction,0)<=-10:continue
        if ally.get('character',{}).get('skills',{}).get(skill,0)>0: helpers.append(ally['id'])
    helpers = helpers[:2]
    fatigue = -2 if subject.get('energy',100)<25 else 0
    bonus = parts['total']+reputation+situation+trust+attitude+len(helpers)+fatigue
    import field_rules,field_adventure
    if field_rules.active(w):
        return field_adventure.check(w,subject,stat,dc,skill,engine,context,situation,npc,faction)
    die = engine.secrets.randbelow(20)+1
    success = die==20 or (die!=1 and die+bonus>=dc)
    grade = 'strong' if success and (die==20 or die+bonus-dc>=5) else 'success' if success else 'setback'
    record = dict(tick=w['tick'],action=action,skill=skill,stat=stat,die=die,dc=dc,total=die+bonus,bonus=bonus,
                  success=success,grade=grade,faction=faction,reputation=reputation,context=situation,
                  reasons=reasons,trust=trust,attitude=attitude,support=len(helpers),helpers=helpers,
                  attribute=parts['attribute'],training=parts['training'],equipment=parts['equipment'],
                  experience=parts['experience'],conditions=parts['conditions'],fatigue=fatigue)
    subject['last_check']=record
    subject.setdefault('check_log',[]).append(copy.deepcopy(record));subject['check_log']=subject['check_log'][-60:]
    subject.setdefault('_checks',[]).append(record)
    mechanics = (f"D20 {die} + {bonus} {stat} vs {dc}: {grade}. {characters.SKILLS[skill]['label']}. "
                 f"Attribute {parts['attribute']}, training {parts['training']}, equipment {parts['equipment']}, "
                 f"experience {parts['experience']}, conditions −{parts['conditions']}, fatigue {fatigue}; "
                 f"reputation {reputation:+} [{faction}], context {situation:+} ({', '.join(reasons) or 'ordinary conditions'}), "
                 f"trust {trust:+}, attitude {attitude:+}, companion support +{len(helpers)}.")
    return success, mechanics
