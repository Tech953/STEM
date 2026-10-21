"""Field Guide 1.0: shared, bounded Thorns/Stem rules; Python stdlib only.

Campaign RNG is independent of authentication entropy. The saved counter, scene,
actor identities and award ledger are authoritative; reads never reroll a scene.
"""
import copy
import hashlib
import json
import math
import re
from pathlib import Path

RULESET = 'field-guide-1'
CATALOG = json.loads((Path(__file__).parent / 'creature_catalog.json').read_text())
PROFILES = {x['id']: x for x in CATALOG}
HABITATS = {
    'needle': ['FOE01', 'FOE25', 'FOE39', 'FOE32', 'FOE38', 'FOE40'],
    'web': ['FOE02', 'FOE34', 'FOE08', 'FOE03', 'FOE06', 'FOE07'],
    'gale': ['FOE14', 'FOE29', 'FOE26', 'FOE28', 'FOE17', 'FOE33'],
    'shellwood': ['FOE16', 'FOE15', 'FOE27', 'FOE30', 'FOE35', 'FOE05'],
    'ark': ['FOE13', 'FOE31', 'FOE12', 'FOE04', 'FOE23', 'FOE24'],
    'enact': ['FOE18', 'FOE11', 'FOE37', 'FOE36', 'FOE09', 'FOE10'],
    'tar': ['FOE41', 'FOE20', 'FOE19', 'FOE42', 'FOE45', 'FOE43'],
    'bunker': ['FOE21', 'FOE44', 'FOE19', 'FOE41', 'FOE42', 'FOE43'],
    'campus': ['FOE46', 'FOE22', 'FOE47', 'FOE48', 'FOE22', 'FOE46'],
}
WEIGHTS = [4, 3, 2, 1, 1, 1]
ACTS = {'field_watch', 'field_engage', 'field_attack', 'field_shoot',
        'field_replace', 'field_guard', 'field_approach', 'field_retreat', 'field_end',
        'field_parley', 'field_withdraw', 'field_salvage', 'field_repair',
        'field_breather', 'field_rest', 'field_eat', 'field_drink',
        'field_treat', 'field_grow', 'field_recruit', 'field_dismiss',
        'field_npc_talk', 'field_npc_task', 'field_share', 'field_mastery'}
FREE = {'look', 'inspect', 'listen', 'inventory', 'map', 'goto', 'return',
        'dismiss', 'abandon', 'business', 'wait', 'ow_talk'}
MATERIALS = {'wood': (2, .4), 'metal': (6, .6), 'stone': (8, .5),
             'crystal': (4, .4), 'fabric': (1, .2), 'polymer': (3, .4)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def clamp(n, lo=0, hi=100):
    return max(lo, min(hi, n))


def active(w):
    return bool(w.get('field_rules', {}).get('enabled'))


def position(p):
    return p.get('pos', p.get('grid', [p.get('x', 0), p.get('y', 0)]))


def site_key(p):
    return ','.join(map(str, position(p)))


def vitals(p):
    return p.get('vitals', p)


def pack(p):
    return p.get('inventory', p.get('supplies', {}))


def people(w):
    return w.get('actors', w.get('field_companions', []))


def ensure_player(p, new=False):
    if 'inventory' not in p and 'supplies' not in p:
        p['supplies']=dict(food=0,water=0,scrap=0,seed=0,medkit=0)
    p.setdefault('personal_reputation', {})
    p.setdefault('relationships', {})
    p.setdefault('check_log', [])
    p.setdefault('progression', dict(earned_xp=p.get('xp', 0), spent_growth=0,
                                   awards={}, session_xp={}, goal_sessions=[]))
    p.setdefault('gear', {
        'staff': dict(id=p['id'] + ':staff', name='field staff', material='wood',
                      condition=100, threshold=1, embodied=2, salvaged=False),
        'cloak': dict(id=p['id'] + ':cloak', name='route cloak', material='fabric',
                      condition=100, threshold=1, embodied=1, salvaged=False),
        'role_tool': dict(id=p['id'] + ':tool', name='role tool', material='metal',
                          condition=100, threshold=1, embodied=1, salvaged=False),
    })
    p.setdefault('field_armor', 0)
    p.setdefault('loadout', [])
    p.setdefault('credentials', [])
    p.setdefault('companions', [])
    v = vitals(p)
    v.setdefault('energy', 100)
    for k in ['health', 'injuries', 'ailments']:
        v.setdefault(k, 100 if k == 'health' else [])
    inv = pack(p)
    inv.setdefault('scrap', 0)
    inv.setdefault('seed', 0)
    inv.setdefault('medkit', 0)
    if new:
        inv.update(food=4, water=5, scrap=3, seed=2, medkit=2)


def ensure_world(w, new=False):
    if 'field_rules' not in w:
        w['field_rules'] = dict(schema=1, enabled=new, cycle=0, last_watch=0,
                               rng_counter=0, rolls=[], session=1,
                               difficulty='normal', budget_mode='planning')
    w.setdefault('field_sites', {})
    if w['field_rules']['enabled']:
        for p in w['players']:
            ensure_player(p)
    return w['field_rules']


def enable(w, new=False):
    f = ensure_world(w)
    was_enabled=f['enabled']
    if not was_enabled:
        for member in w['players']:
            ensure_player(member)
            member['progression']['earned_xp']=member.get('xp',0)
    f['enabled'] = True
    f.setdefault('migration', 'New campaign' if new else
                 'Opted in: existing inventory, earned XP, identities and routes retained.')
    for p in w['players']:
        ensure_player(p, new=new)
        if new and 'credits' in p:
            p['credits'] = 0
    return f


def die(w, sides, label):
    f = ensure_world(w)
    # Rejection sampling avoids modulo bias for non-power-of-two dice.
    index = f['rng_counter']
    nonce = 0
    limit = 2**256 - (2**256 % sides)
    while True:
        raw = int.from_bytes(hashlib.sha256(
            f"{w['seed']}|field-guide-1|{index}|{nonce}|{label}".encode()).digest(), 'big')
        if raw < limit:
            break
        nonce += 1
    value = raw % sides + 1
    f['rng_counter'] += 1
    f['rolls'].append(dict(index=index, sides=sides, label=label, value=value))
    f['rolls'] = f['rolls'][-200:]
    return value


def grade(face, bonus, dc):
    if face == 1:
        return 'complication'
    if face == 20:
        return 'strong'
    margin = face + bonus - dc
    return ('strong' if margin >= 5 else 'success' if margin >= 0 else
            'complication' if margin <= -5 else 'setback')


def odds(bonus, dc):
    result = dict(complication=0, setback=0, success=0, strong=0)
    for face in range(1, 21):
        result[grade(face, bonus, dc)] += 5
    result['pass_percent'] = result['success'] + result['strong']
    return result


def bulk(p):
    inv = pack(p)
    loose = sum(inv.get(k, 0) for k in ['food', 'water', 'scrap', 'seed'])
    # Staff, cloak, role tool and each medkit occupy one bulk; keepsake is negligible.
    used = math.ceil(loose / 5) + 3 + inv.get('medkit', 0)
    cap = 10 + 2 * p['character']['attributes']['body']
    return dict(used=used, capacity=cap, overloaded=used > cap, blocked=used > 2*cap)


def ready(w, p, a, skill=None):
    cm = p.get('contract') or {}
    issuer = cm.get('faction', a.get('faction'))
    return (a.get('owner') == p['id'] and position(a) == position(p)
            and a.get('health', 100) >= 35 and a.get('energy', 100) >= 15
            and a.get('attitude', 50) >= 30
            and a.get('engagement', {}).get('phase') != 'recover'
            and a.get('personal_reputation', {}).get(issuer, 0) > -10
            and (not skill or a.get('character', {}).get('skills', {}).get(skill, 0) >= 1))


def breakdown(w, p, stat, skill, situation=0, faction=None, npc=None,
              support=False, combat=False):
    ensure_player(p)
    c = p['character']; v = vitals(p)
    training = c['skills'].get(skill, 0)
    tool_skills = {'leg_spikes':'transversal', 'meta_fingers':'fractech',
                   'bio_glass':'medtech', 'crystallin':'crystallin',
                   'survey_lens':'percept', 'filter_graft':'fieldcraft',
                   'rest_regulator':'fieldcraft', 'resonance_link':'contracts'}
    equipment = int(('black.dot' in p.get('credentials', []) or p.get('licensed',False))
                    and any(tool_skills.get(x) == skill and
                            p.get('mod_condition', {}).get(x, 100) >= 30
                            for x in p.get('loadout', [])))
    needs = ['hunger', 'thirst', 'sleep'] if 'vitals' in p else ['food_need', 'thirst', 'sleep']
    conditions = min(5, len(v['injuries']) + len(v['ailments']) +
                     sum(v.get(k, 0) >= 70 for k in needs))
    xp = min(2, p['progression']['earned_xp'] // 3)
    reputation = clamp(math.trunc((w.get('reputation', {}).get(faction, 0) +
                                  p['personal_reputation'].get(faction, 0)/2)/5), -2, 2)
    trust = int(bool(npc) and p['relationships'].get(npc['id'], {}).get('trust', 0) >= 3)
    attitude = (1 if npc.get('attitude', 50) >= 70 else
                -1 if npc.get('attitude', 50) < 30 else 0) if npc else 0
    already = p.get('_field_helpers', [])
    helpers = [a['id'] for a in people(w) if support and ready(w, p, a, skill)
               and a['id'] not in already and a != npc
               and (not combat or a.get('_field_ap', 8) >= 3)][:2]
    fatigue = -2 if v['energy'] < 25 else 0
    if skill == 'transversal' and bulk(p)['overloaded']:
        situation -= 2
    situation = clamp(situation, -3, 3)
    practice = min(2, training + equipment)
    total = c['attributes'][stat]+practice+xp+situation+reputation+trust+attitude+len(helpers)-conditions+fatigue
    return dict(attribute=c['attributes'][stat], training=training, equipment=equipment,
                practice=practice, experience=xp, context=situation, reputation=reputation,
                trust=trust, attitude=attitude, helpers=helpers, support=len(helpers),
                conditions=conditions, fatigue=fatigue, bonus=total)


def roll(w, p, stat, skill, dc, action, **context):
    b = breakdown(w, p, stat, skill, **context)
    if b['equipment']:
        tool_skills={'leg_spikes':'transversal','meta_fingers':'fractech','bio_glass':'medtech','crystallin':'crystallin','survey_lens':'percept','filter_graft':'fieldcraft','rest_regulator':'fieldcraft','resonance_link':'contracts'}
        eligible=next((m for m in p.get('loadout',[]) if tool_skills.get(m)==skill and p.get('mod_condition',{}).get(m,100)>=30),None)
        if eligible:p.setdefault('mod_condition',{})[eligible]=max(0,p.get('mod_condition',{}).get(eligible,100)-1)
    for a in people(w):
        if a['id'] in b['helpers']:
            a['energy'] = max(0, a['energy']-2)
            a['_field_support_spent'] = True
            a['_field_ap'] = a.get('_field_ap', 8)-3
    p.setdefault('_field_helpers', []).extend(b['helpers'])
    face = die(w, 20, p['id'] + ':' + action)
    result = grade(face, b['bonus'], dc)
    record = dict(b, die=face, dc=dc, total=face+b['bonus'], grade=result,
                  success=result in {'success', 'strong'}, action=action, stat=stat,
                  skill=skill, tick=w.get('tick', ensure_world(w)['cycle']),
                  faction=context.get('faction'), reasons=[], odds=odds(b['bonus'], dc))
    p['last_check'] = record
    p['check_log'].append(copy.deepcopy(record)); p['check_log'] = p['check_log'][-60:]
    p.setdefault('_checks', []).append(record)
    text = (f"D20 {face} + {b['bonus']} {stat}/{skill} vs {dc}: {result}. "
            f"Chance {record['odds']['pass_percent']}%; attribute {b['attribute']}, "
            f"practice {b['practice']}, XP {b['experience']}, context {b['context']:+}, "
            f"standing {b['reputation']:+}, trust {b['trust']}, attitude {b['attitude']:+}, "
            f"support {b['support']}, conditions −{b['conditions']}, fatigue {b['fatigue']}.")
    return record['success'], text


def award(w, p, identity, amount=1, goal=False):
    ensure_player(p)
    if not active(w):
        p['xp'] = p.get('xp', 0) + amount
        return amount
    g = p['progression']; session = str(w['field_rules']['session'])
    if identity in g['awards']:
        return 0
    used = g['session_xp'].get(session, 0)
    allowance = 1 if goal and session not in g['goal_sessions'] else max(0, 3-used) if not goal else 0
    amount = min(amount, allowance)
    # A resolved event cannot be farmed after a session boundary either.
    g['awards'][identity] = amount
    if goal and amount:
        g['goal_sessions'].append(session)
    elif amount:
        g['session_xp'][session] = used+amount
    g['earned_xp'] += amount
    p['xp'] = g['earned_xp']
    return amount


def grow(w, p, target):
    g = p['progression']; kind, _, name = target.partition(':')
    available = g['earned_xp']//3 - g['spent_growth']
    c = p['character']
    if kind == 'skill':
        require(name in c['skills_catalog'] if 'skills_catalog' in c else name in __import__('characters').SKILLS,
                'Choose a listed proficiency.')
        require(available >= 1 and c['skills'].get(name, 0) < 3, 'Need one Growth; skill maximum is 3.')
        c['skills'][name] = c['skills'].get(name, 0)+1; g['spent_growth'] += 1
    elif kind == 'attribute':
        require(name in c['attributes'], 'Choose an attribute.')
        require(available >= 2 and c['attributes'][name] < 4 and sum(c['attributes'].values()) < 10,
                'Need two Growth; attribute maximum 4 and total maximum 10.')
        c['attributes'][name] += 1; g['spent_growth'] += 2
    else:
        raise ValueError('Use skill:name or attribute:name.')
    return 'Growth recorded. Earned XP and the experience bonus remain intact.'


def habitat(cell):
    if cell.get('region') == 'OMNI-META-INFI-PARTICULATE':
        return None
    name = (cell.get('title', '')+' '+cell.get('feature', '')).lower()
    if cell.get('terrain')=='woodland' or any(x in name for x in ['snowl', 'shellwood', 'vine']):
        return 'shellwood'
    if re.search(r'\bark\b',name):
        return 'ark'
    return {'WN_TOWER': 'web' if 'web' in name else 'needle',
            'CITY_CLOUD_S': 'web', 'AETHERGALE': 'gale', 'ENACT_HILLS': 'enact'}.get(cell.get('region'))


def scene(w, p):
    return w.get('field_sites', {}).get(site_key(p), {}).get('encounter')


def generate(w, p, cell):
    f = ensure_world(w); h = habitat(cell)
    require(h in {'needle', 'web', 'gale', 'shellwood', 'ark', 'enact'},
            'No ordinary encounter can be generated from a remote projection.')
    sk = site_key(p); site = w['field_sites'].setdefault(sk, {})
    previous = site.get('encounter')
    if previous and (previous.get('actors') or previous.get('evidence_only')):
        return previous
    watch = f['cycle']//4
    if previous and previous['watch'] == watch:
        return previous
    nearby = [x for x in w['players'] if position(x) == position(p) and not x.get('remote')]
    budget = [2, 3, 4, 6, 7, 9][max(1, min(6, len(nearby)))-1]
    if f['difficulty'] == 'easy':
        budget = math.ceil(budget/2)
    elif f['difficulty'] == 'dangerous':
        budget = math.ceil(budget*1.5)
    start = f['rng_counter']
    prefix = f"{sk}:watch{watch}:"
    threshold = 3 if cell.get('stability', 80) < 35 else 1 if cell.get('shelter') or cell.get('facility') == 'sanctuary' else 2
    e = dict(id=prefix, watch=watch, habitat=h, budget=budget, actors=[],
             resolved=False, combat=None, declined=[], events=[], loot_paid=False,
             event='No new encounter; established clocks continue.')
    site['encounter'] = e
    if die(w, 6, prefix+'watch encounter') <= threshold:
        half = die(w, 6, prefix+'profile half'); face = die(w, 6, prefix+'profile face')
        ticket = face if half % 2 else face+6
        tickets = [pid for pid, count in zip(HABITATS[h], WEIGHTS) for _ in range(count)]
        profile = copy.deepcopy(PROFILES[tickets[ticket-1]])
        cost = profile['planning_cost']
        e.update(profile_face=ticket, sign=profile['sign'])
        if cost > budget:
            e.update(evidence_only=True, event='Signs only: this profile exceeds the encounter budget. Keep distance or take another route.')
        else:
            variant = die(w, 6, prefix+'variant A')+die(w, 6, prefix+'variant B')
            tag = 'depleted' if variant <= 4 else 'reinforced' if variant >= 10 else 'typical'
            if tag == 'reinforced' and profile['reinforced_cost'] > budget:
                tag = 'typical (budget fallback)'
            if tag in {'depleted', 'reinforced'}:
                delta = -1 if tag == 'depleted' else 1
                profile['health'] = max(10, profile['health']+5*delta)
                for k in ['defense', 'attack_dc', 'damage']:
                    profile[k] = max(1, profile[k]+delta)
                if delta > 0:
                    cost = profile['reinforced_cost']
            desired = (die(w, 6, prefix+'desired group size')+1)//2
            count = min(desired, budget//cost)
            mood = die(w, 6, prefix+'disposition A')+die(w, 6, prefix+'disposition B')
            disposition = ('defensive' if mood <= 3 else 'wary' if mood <= 5 else
                           'occupied' if mood <= 8 else 'curious' if mood <= 10 else 'helpful')
            need = ['a clear return route', 'a real replacement part', 'a witnessed agreement',
                    'shelter without obligation', 'an intact observation record', 'undisturbed habitat'][die(w,6,prefix+'need')-1]
            for n in range(count):
                a = copy.deepcopy(profile)
                a.update(instance_id=prefix+profile['id']+':'+str(n), max_health=profile['health'],
                         energy=100, variant=tag, planning_cost=cost, disposition=disposition,
                         present_need=need, state='present', morale_tested=False,
                         hex=[3,n], injuries=[], ailments=[])
                e['actors'].append(a)
            e.update(event='Encounter opportunity. Disposition never forces hostility or overrides a refusal.',
                     spent_budget=count*cost, requested_count=desired, variant=tag)
    e['rolls'] = [copy.deepcopy(r) for r in f['rolls'] if r['index'] >= start]
    return e


def after_cycle(w, p, cell):
    f = ensure_world(w)
    f['cycle'] += 1
    if f['cycle'] % 4:
        return
    f['last_watch'] = f['cycle']//4
    if habitat(cell) and not p.get('remote'):
        generate(w, p, cell)
    for a in p['gear'].values():
        # Packed tools are protected; exposed cloak receives environmental wear.
        if a['name'] == 'route cloak':
            wear = 1 + int(cell.get('moisture', 0) > 65) + (2 if cell.get('severe_storm') else 0)
            a['condition'] = max(0, a['condition']-wear)


def begin_action(p):
    p['_field_helpers'] = []
    p['_checks'] = []


def companion_cycle(w, p, cycles=1):
    for _ in range(cycles):
        for a in people(w):
            if a.get('owner') != p['id']:
                continue
            if 'pos' in a:
                a['pos'] = position(p)[:]
            a['x'], a['y'] = position(p)
            a['energy'] = max(0, a.get('energy',100) - (0 if a.pop('_field_support_spent',False) else 1))
            a['field_active_cycles'] = a.get('field_active_cycles',0)+1
            if a['field_active_cycles'] % 6 == 0:
                for k in ['food','water']:
                    if pack(a).get(k,0):
                        pack(a)[k] -= 1
                    else:
                        a['energy'] = max(0,a['energy']-3);a['attitude'] = max(0,a['attitude']-2)
            if a.get('attitude',50) < 20:
                a['owner'] = None
                p['companions'] = [i for i in p['companions'] if i != a['id']]


def distance(a,b):
    q, r = a[0]-b[0], a[1]-b[1]
    return max(abs(q),abs(r),abs(q+r))


def neighbors(a):
    return [[a[0]+q,a[1]+r] for q,r in [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]]


def live(a):
    return a['health'] > 0 and a['state'] == 'present'


def participant(w, e, identity):
    return next((p for p in w['players'] if p['id']==identity), None)


def combat_end(w,e):
    battle = e['combat']
    living = [i for i in battle['pcs'] if i not in battle['escaped'] and
              participant(w,e,i) and vitals(participant(w,e,i))['health'] > 0]
    if any(live(a) for a in e['actors']) and living:
        return False
    battle['finished'] = True
    if not any(live(a) for a in e['actors']):
        e['resolved'] = True
        for i in battle['pcs']:
            p = participant(w,e,i)
            if p:
                award(w,p,e['id']+'resolution')
    battle['conclude_pending'] = True
    return True


def morale(w,e,a):
    if a['morale_tested'] or a['health'] <= 0 or a['health'] > a['max_health']/2:
        return
    a['morale_tested'] = True
    face = die(w,20,a['instance_id']+':morale')
    if face == 20 or (face != 1 and face > a['morale']):
        a['state'] = 'withdrawn'
        e['events'].append(a['name']+' withdraws; its remaining possessions stay with it.')


def foe_turn(w,e,a):
    battle=e['combat'];ap=a['ap'];a['guard']=0
    candidates=[participant(w,e,i) for i in battle['pcs'] if i not in battle['escaped']]
    candidates=[p for p in candidates if p and vitals(p)['health']>0]
    if not candidates:
        return
    target=min(candidates,key=lambda p:(distance(a['hex'],battle['positions'][p['id']]),p['id']))
    loc=battle['positions'][target['id']]
    if a['id']=='FOE03' and battle['round']==1 and distance(a['hex'],loc)>1:
        a['guard']=2;ap-=2
    while ap>0 and distance(a['hex'],loc)>a['range'] and not a['stationary']:
        occupied=[x['hex'] for x in e['actors'] if x!=a and live(x)]
        choices=[x for x in neighbors(a['hex']) if x not in occupied and x not in battle['positions'].values()]
        if not choices:
            break
        best=min(choices,key=lambda x:(distance(x,loc),x))
        if distance(best,loc)>=distance(a['hex'],loc):
            break
        a['hex']=best;ap-=1
    attacks=0
    while (ap>=a['attack_ap'] and attacks<a['attack_limit'] and distance(a['hex'],loc)<=a['range']
           and (a['ammo'] is None or a['ammo']>0) and vitals(target)['health']>0):
        ap-=a['attack_ap'];attacks+=1
        if a['ammo'] is not None:
            a['ammo']-=1
        penalty=min(5,len(a['injuries'])+len(a['ailments']))+(2 if a['energy']<25 else 0)
        dc=max(6,a['attack_dc']-penalty)
        ok, text=roll(w,target,'body','fieldcraft',dc,'defend',
                      situation=min(3,battle['guards'].get(target['id'],0)),combat=True)
        loss=0 if ok else a['damage']
        v=vitals(target)
        if a['channel']=='Health':
            loss=max(0,loss-min(5,target.get('field_armor',0)))
            guard=next((x for x in people(w) if ready(w,target,x) and x.get('engagement',{}).get('task')=='guard'
                        and x.get('_guard_round')!=battle['round'] and x['energy']>=2),None)
            if loss and guard:
                share=min(3,loss);loss-=share;guard['health']=max(0,guard['health']-share)
                guard['energy']-=2;guard['_guard_round']=battle['round']
            v['health']=max(0,v['health']-loss)
        else:
            v['energy']=max(0,v['energy']-loss)
        e['events'].append(f"{a['name']} → {target['name']}: {loss} {a['channel']}. "+text)
    if a['ammo']==0:
        e['events'].append(a['name']+' has exhausted its stored attacks.')


def advance_turn(w,e):
    battle=e['combat']
    if combat_end(w,e):
        return
    for _ in range(len(battle['order'])+1):
        battle['cursor']=(battle['cursor']+1)%len(battle['order'])
        if battle['cursor']==0 and battle.get('started_round'):
            battle['round']+=1
        battle['started_round']=True
        who=battle['order'][battle['cursor']]
        p=participant(w,e,who)
        if who in battle['pcs'] and p is None:
            continue
        if p:
            if who in battle['escaped'] or vitals(p)['health']<=0:
                continue
            battle['ap'][who]=8+min(2,p['character']['attributes']['body']//2)
            battle['guards'][who]=0
            begin_action(p)
            for a in people(w):
                if a.get('owner')==who:
                    a['_field_ap']=8
            return
        a=next(x for x in e['actors'] if x['instance_id']==who)
        if live(a):
            foe_turn(w,e,a)
        if combat_end(w,e):
            return
    raise ValueError('Encounter has no available turn.')


def start_combat(w,p,e):
    pcs=[x for x in w['players'] if position(x)==position(p) and not x.get('remote') and vitals(x)['health']>0]
    entries=[]
    for x in pcs:
        a=x['character']['attributes'];initiative=a['body']+a['percept']+die(w,6,x['id']+':initiative')-1
        entries.append((-initiative,-a['percept'],-a['body'],x['id']))
    for a in e['actors']:
        if live(a):
            entries.append((-a['initiative'],0,0,a['instance_id']))
    e['combat']=dict(order=[x[3] for x in sorted(entries)],cursor=-1,round=1,
                     pcs=[x['id'] for x in pcs],positions={x['id']:[0,i] for i,x in enumerate(pcs)},
                     ap={},guards={},escaped=[],finished=False,conclude_pending=False)
    advance_turn(w,e)


def current(w,p):
    e=scene(w,p)
    if not e or not e.get('combat') or e['combat']['finished']:
        return None
    return e['combat']['order'][e['combat']['cursor']]


def release_seat(w, identity):
    """A departing seat cannot strand a shared encounter's active turn."""
    for site in w.get('field_sites',{}).values():
        e=site.get('encounter');b=e.get('combat') if e else None
        if not b or b['finished'] or identity not in b['pcs']:
            continue
        if identity not in b['escaped']:
            b['escaped'].append(identity)
        if b['order'][b['cursor']]==identity:
            advance_turn(w,e)


def damage(base,condition,strong,armor):
    factor=100 if condition>=60 else 80 if condition>=30 else 55
    return max(0,base*factor//100+(2 if strong else 0)-min(5,armor))


def consume(w,p,item):
    require(pack(p).get(item,0)>0,'No '+item+' remains in your pack.')
    pack(p)[item]-=1
    ok,text=roll(w,p,'body','fieldcraft',8,'consume')
    return ('You prepare one '+item+'. Recovery applies after the active cycle.',text,
            dict(kind='consume',item=item,success=ok))


def recovery(p, pending):
    if not pending:
        return
    v=vitals(p);kind=pending['kind']
    if kind=='consume':
        key=('hunger' if 'vitals' in p else 'food_need') if pending['item']=='food' else 'thirst'
        v[key]=clamp(v.get(key,0)-(45 if pending['success'] else 35));v['energy']=clamp(v['energy']+8)
    elif kind=='breather':
        v['energy']=clamp(v['energy']+(35 if pending['success'] else 25));v['health']=clamp(v['health']+(8 if pending['success'] else 4));v['sleep']=max(0,v.get('sleep',0)-10)
    elif kind=='full_rest':
        v['energy']=100;v['sleep']=0;v['health']=clamp(v['health']+25)
        for k in ['hunger' if 'vitals' in p else 'food_need','thirst']:
            v[k]=max(0,v.get(k,0)-45)
    elif kind=='treat' and pending['success']:
        v['health']=clamp(v['health']+25+(5 if pending.get('strong') else 0))
        for k in ['injuries','ailments']:
            if v[k]:
                v[k].pop(0);break


def handle(w,p,op,target,cell):
    """Return a result plus active cycles; callers own ecology and persistence."""
    require(active(w),'The host can adopt Field Guide rules from the field panel.')
    ensure_player(p)
    require(not p.get('remote'),'Return from the remote apparatus before physical field actions.')
    require(op in {'field_grow','field_mastery','field_dismiss'} or habitat(cell) is not None,'Received semblance provides no verified physical actor, material stock or shelter.')
    e=scene(w,p);b=e.get('combat') if e else None
    fighting=bool(b and not b['finished'])
    if not fighting:
        begin_action(p)
    if fighting:
        require(op=='field_dismiss' or current(w,p)==p['id'],'Wait for the highlighted character’s turn.')
        require(op in {'field_attack','field_shoot','field_guard','field_approach',
                       'field_retreat','field_end','field_parley','field_withdraw','field_treat','field_dismiss','field_mastery'},
                'Finish the local encounter before working, resting or changing a build.')
    result=dict(text='',mechanics='',cycles=0,pending=None)
    if op=='field_mastery':
        previous=p.get('last_check',{});session=str(w['field_rules']['session'])
        require(previous.get('grade')=='complication' and p['character']['skills'].get(previous.get('skill'),0)==3,'Mastery needs a complication on a rank-3 proficiency.')
        require(p.get('mastery_session')!=session,'Mastery is available once per session.')
        p['mastery_session']=session;previous['original_grade']='complication';previous['grade']='setback';previous['mastery']=True
        if p['check_log']:p['check_log'][-1]=copy.deepcopy(previous)
        result['text']='Mastery softens this complication to a setback. It remains a failed check; spent costs and resolved damage remain recorded.'
        return result
    if op=='field_grow':
        result['text']=grow(w,p,target);return result
    if op in {'field_eat','field_drink'}:
        result['text'],result['mechanics'],result['pending']=consume(w,p,'food' if op=='field_eat' else 'water')
        result['cycles']=1;return result
    if op in {'field_breather','field_rest'}:
        safe=cell.get('shelter',0)>0 or cell.get('facility')=='sanctuary'
        require(safe,'Find maintained shelter first.')
        require(not e or not any(live(a) and a['disposition']=='defensive' for a in e['actors']),
                'Find an unpressured shelter before resting.')
        if op=='field_rest':
            require(pack(p).get('food',0)>0 and pack(p).get('water',0)>0,'Full rest reserves one food and one water.')
            pack(p)['food']-=1;pack(p)['water']-=1
            result.update(text='A safe four-cycle rest is reserved. A new interruption cancels recovery.',cycles=4,pending=dict(kind='full_rest'))
        else:
            ok,text=roll(w,p,'body','fieldcraft',8,'breather')
            result.update(text='One sheltered breather; conditions remain recorded.',mechanics=text,cycles=1,pending=dict(kind='breather',success=ok))
        return result
    if op=='field_replace':
        require(target in p['gear'],'Choose a recorded ruined personal item.')
        old=p['gear'][target];require(old['condition']==0,'Replacement is for a ruined item; worn material can be repaired.')
        require(pack(p)['scrap']>=2,'Replacement reserves two real material units.')
        require(cell.get('shelter') or cell.get('facility') in {'clinic','sanctuary'},'Find a sheltered craft surface for replacement.')
        pack(p)['scrap']-=2
        ok,text=roll(w,p,'tech','metallurgy',11,'replace',support=True)
        if ok:
            retired=p.setdefault('retired_gear',[]);retired.append(copy.deepcopy(old))
            p['gear'][target]=dict(old,id=p['id']+':'+target+':replacement:'+str(len(retired)),condition=100,salvaged=False)
        result.update(text='Replacement '+('creates a new recorded object and retires the ruined ID.' if ok else 'does not hold; the reserved material is spent.'),mechanics=text,cycles=1)
        return result
    if op=='field_repair':
        require(target in p['gear'],'Choose a personal staff, cloak or role tool.')
        item=p['gear'][target]
        require(0<item['condition']<100,'Repair applies to worn, operable material; ruined objects need replacement.')
        require(pack(p)['scrap']>=1,'Repair spends one real scrap before its check.')
        pack(p)['scrap']-=1
        ok,text=roll(w,p,'tech','metallurgy',11,'repair',support=True)
        if ok:item['condition']=min(100,item['condition']+25)
        result.update(text='Material repair '+('adds 25 condition.' if ok else 'does not hold; its scrap is spent.'),mechanics=text,cycles=1)
        return result
    if op=='field_watch':
        result.update(text='Four active cycles pass. One shared encounter check belongs to the watch.',cycles=4)
        return result
    if op in {'field_recruit','field_dismiss','field_npc_talk','field_npc_task','field_share'}:
        return companion_action(w,p,op,target,cell)
    if op=='field_treat':
        require(pack(p).get('medkit',0)>0,'A treatment spends one medkit.')
        require(vitals(p)['health']<100 or vitals(p)['injuries'] or vitals(p)['ailments'],'No treatment is currently needed.')
        if fighting:require(b['ap'][p['id']]>=3,'Treatment costs 3 AP.')
        pack(p)['medkit']-=1
        ok,text=roll(w,p,'tech','medtech',10,'treat',support=not fighting)
        result.update(text='A field treatment is recorded.',mechanics=text,pending=dict(kind='treat',success=ok,strong=p['last_check']['grade']=='strong'),cycles=0 if fighting else 1)
        if fighting:
            b['ap'][p['id']]-=3;recovery(p,result.pop('pending'));result['pending']=None
            if b['ap'][p['id']]==0:
                advance_turn(w,e)
        return result
    require(e and e['actors'],'No present field encounter. Travel or spend a watch to observe an opportunity.')
    if op=='field_withdraw' and not fighting:
        if p['id'] not in e['declined']:e['declined'].append(p['id'])
        result['text']='You decline the encounter. Its identities, stock and boundaries remain in the record.'
        return result
    if op=='field_salvage':
        require(e['resolved'] and not fighting,'Resolve the encounter before recovering abandoned material.')
        require(not e['loot_paid'],'This scene’s abandoned material has already been recorded.')
        eligible=[a for a in e['actors'] if a['health']==0 and not a['person']]
        require(eligible,'No abandoned non-person material is available; a truce or withdrawal does not yield someone’s pack.')
        amount=sum(a['salvage_budget'] for a in eligible)
        require(pack(p)['scrap']+amount<=99,'Make room for the recovered material.')
        e['loot_paid']=True;pack(p)['scrap']+=amount
        result.update(text=f'Recovered {amount} scrap from finite exposed-component salvage budgets. Whole monuments remain intact.',cycles=1)
        return result
    a=next((x for x in e['actors'] if x['instance_id']==target),None)
    if op=='field_engage':
        require(not e['resolved'] and not fighting,'This encounter is already resolved or active.')
        require(any(live(x) for x in e['actors']),'No active encounter actor remains.')
        start_combat(w,p,e);result['text']='Local turn order is fixed. Movement and attacks spend AP; enemies act on their own turns.'
        return result
    if op=='field_parley' and not fighting:
        require(a and live(a),'Choose a present encounter actor.')
        token=a['instance_id']+':parley'
        attempts=e.setdefault('peace_after',{})
        require(ensure_world(w)['cycle']>=attempts.get(token,0),'Allow four active cycles or take another route before renewing this proposal.')
        attempts[token]=ensure_world(w)['cycle']+4
        ok,text=roll(w,p,'rapport','community' if a['person'] else 'memetic',13,'parley',support=True)
        if ok:
            a['state']='truce'
            if not any(live(x) for x in e['actors']):
                e['resolved']=True;award(w,p,e['id']+'resolution')
        result.update(text=('A limited, voluntary passage agreement is recorded. No gear, credential or private memory changes hands.' if ok else 'The proposal is declined. The public account and another route remain available.'),mechanics=text,cycles=1)
        return result
    require(fighting,'Begin the encounter before using tactical actions.')
    costs={'field_attack':3,'field_shoot':4,'field_guard':2,'field_approach':1,
           'field_retreat':1,'field_parley':3,'field_withdraw':1,'field_end':0}
    cost=costs[op]
    require(b['ap'][p['id']]>=cost,'Not enough AP; end the turn or choose a cheaper action.')
    if op in {'field_attack','field_shoot','field_approach','field_retreat','field_parley'}:
        require(a and live(a),'Choose a present encounter actor.')
    loc=b['positions'][p['id']]
    if op in {'field_attack','field_shoot'}:
        ranged=op=='field_shoot';reach=6 if ranged else 1
        require(distance(loc,a['hex'])<=reach,'The target is outside this action’s range. Approach first.')
        if ranged:
            require(('black.dot' in p['credentials'] or p.get('licensed',False)) and 'crystallin' in p['loadout'],
                    'Ranged fire requires an issued, registered crystallin retrofit.')
            require(pack(p)['scrap']>=1,'Every shot spends one actual scrap, including a miss.')
            p.setdefault('gear',{}) .setdefault('retrofit',dict(id=p['id']+':retrofit',name='crystallin retrofit',material='crystal',condition=100,threshold=20,embodied=2,salvaged=False))
        item=p['gear']['retrofit' if ranged else 'staff']
        require(item['condition']>=item['threshold'],'This weapon is below its operating threshold. Repair it first.')
        if ranged:pack(p)['scrap']-=1
        ok,text=roll(w,p,'body','ballistics' if ranged else 'transversal',a['defense'],
                     'shoot' if ranged else 'attack',situation=-min(3,a.get('guard',0)),support=True,combat=True)
        dealt=damage((9 if ranged else 6)+p['character']['attributes']['body'],item['condition'],p['last_check']['grade']=='strong',a['armor']) if ok else 0
        a['health']=max(0,a['health']-dealt);item['condition']=max(0,item['condition']-2)
        morale(w,e,a)
        result.update(text=f'{dealt} Health to {a["name"]}; weapon condition {item["condition"]}.',mechanics=text)
        if a['health']==0:a['state']='incapacitated' if a['person'] else 'disabled'
    elif op=='field_guard':
        ok,text=roll(w,p,'body','fieldcraft',10,'guard')
        if ok:b['guards'][p['id']]=2
        result.update(text='Guard lasts until the start of your next turn; guard and cover share a +3 cap.',mechanics=text)
    elif op in {'field_approach','field_retreat'}:
        require(not bulk(p)['blocked'],'Your load exceeds twice capacity; transfer supplies before moving.')
        occupied=[x['hex'] for x in e['actors'] if live(x)]+[v for k,v in b['positions'].items() if k!=p['id'] and k not in b['escaped']]
        choices=[n for n in neighbors(loc) if n not in occupied and max(abs(n[0]),abs(n[1]),abs(n[0]+n[1]))<=12]
        require(choices,'There is no open adjacent hex.')
        sign=1 if op=='field_approach' else -1
        next_pos=min(choices,key=lambda x:(sign*distance(x,a['hex']),x))
        require(sign*distance(next_pos,a['hex'])<sign*distance(loc,a['hex']),'No adjacent step changes that distance in the requested direction.')
        b['positions'][p['id']]=next_pos;result['text']='You move one hidden hex. Local terrain remains continuous.'
    elif op=='field_parley':
        ok,text=roll(w,p,'rapport','community' if a['person'] else 'memetic',13,'parley',support=True,combat=True)
        if ok:a['state']='truce'
        result.update(text='A local passage offer '+('is accepted.' if ok else 'is declined.'),mechanics=text)
    elif op=='field_withdraw':
        ok,text=roll(w,p,'body','transversal',11,'disengage')
        if ok:b['escaped'].append(p['id'])
        result.update(text='You '+('leave the local threat’s reach; travel is available when the encounter closes.' if ok else 'keep your current position.'),mechanics=text)
    else:
        result['text']='Your turn ends.'
    b['ap'][p['id']]-=cost
    if combat_end(w,e):
        pass
    elif op=='field_end' or b['ap'][p['id']]==0 or p['id'] in b['escaped']:
        advance_turn(w,e)
    e['events']=(e['events']+[result['text']])[-60:]
    return result


def companion_action(w,p,op,target,cell):
    selector,_,detail=target.partition('|')
    a=next((x for x in people(w) if x['id']==selector),None)
    require(a and position(a)==position(p),'Choose an NPC who is physically present.')
    owns=a.get('owner')==p['id'];result=dict(text='',mechanics='',cycles=0,pending=None)
    if op=='field_dismiss':
        require(owns,'Only your own agreement can be dismissed.')
        a['owner']=None;p['companions']=[i for i in p['companions'] if i!=a['id']]
        result['text']=a['name']+' keeps their pack and history after the agreement ends.'
    elif op=='field_npc_talk':
        result['text']=(a['name']+': '+a['character']['bio']+' My goal: '+a['character']['goal']+
                        '. My boundary: '+a['character']['boundary']+'. My task is '+a['engagement']['task']+
                        '; '+a['engagement']['phase']+' phase. Our retained shared events: '+str(len(a.get('memory',[])))+'.')
        a.setdefault('memory',[]).append(dict(player=p['id'],topic='lore',cycle=ensure_world(w)['cycle']))
        a['memory']=a['memory'][-40:]
    elif op=='field_recruit':
        require(not a.get('owner'),'This NPC already has an agreement.')
        require(sum(bool(x.get('owner')) for x in people(w))<2 and len(p['companions'])<2,
                'This expedition supports two active NPC agreements across the whole party.')
        require(a['health']>=35 and a['energy']>=15 and a['attitude']>=30,'This NPC needs care, rest or a willing attitude first.')
        require(ensure_world(w)['cycle']>=a.get('field_recruit_after',0),'Wait four active cycles before asking again.')
        require(pack(p).get('food',0)>=1 and pack(p).get('water',0)>=1,'An offer reserves one real food and water.')
        ok,text=roll(w,p,'rapport','community',11,'recruit',faction=a['faction'],npc=a)
        a['field_recruit_after']=ensure_world(w)['cycle']+4
        if ok:
            for k in ['food','water']:pack(p)[k]-=1;pack(a)[k]+=1
            a['owner']=p['id'];a['attitude']=min(100,a['attitude']+5);p['companions'].append(a['id'])
        else:a['attitude']=max(0,a['attitude']-1)
        result.update(text=a['name']+(' accepts a scoped agreement and the offered supplies.' if ok else ' declines; the offer stays in your pack.'),mechanics=text,cycles=1)
    elif op=='field_share':
        require(owns and detail in {'food','water','scrap','seed','medkit'},'Choose a companion and one actual supply.')
        require(pack(p).get(detail,0)>0 and pack(a).get(detail,0)<99,'Both packs must permit the transfer.')
        pack(p)[detail]-=1;pack(a)[detail]+=1;result.update(text='One '+detail+' transferred to '+a['name']+'.',cycles=1)
    else:
        require(owns and detail in {'support','guard','rest'},'Choose support, guard or rest for your companion.')
        a['engagement']['task']=detail;result['text']='The proposed '+detail+' scope is recorded within the existing voluntary agreement.'
    return result


def public(w,p,cell):
    if not active(w):
        return dict(enabled=False,ruleset=RULESET,host=w.get('host'),migration='Existing campaign: original rules retained. The host may adopt Field Guide 1.0.')
    ensure_player(p);f=w['field_rules'];e=copy.deepcopy(scene(w,p));g=p['progression']
    if e and e.get('combat'):
        b=e['combat'];e['active_turn']=None if b['finished'] else b['order'][b['cursor']]
        for a in e['actors']:
            a['distance']=distance(b['positions'].get(p['id'],[0,0]),a['hex'])
    return dict(enabled=True,ruleset=RULESET,cycle=f['cycle'],watch=f['cycle']//4,
                session=f['session'],session_xp=g['session_xp'].get(str(f['session']),0),
                earned_xp=g['earned_xp'],growth=g['earned_xp']//3-g['spent_growth'],
                bulk=bulk(p),gear=copy.deepcopy(p['gear']),habitat=habitat(cell),
                encounter=e,host=w.get('host'),latest_check=copy.deepcopy(p.get('last_check')),
                companions=[copy.deepcopy(a) for a in people(w) if position(a)==position(p)
                            and a.get('owner') in {None,p['id']}],
                roll_count=f['rng_counter'],recent_rolls=copy.deepcopy(f['rolls'][-12:]),
                session_note='3 ordinary XP per host-declared session; one agreed goal XP. NPCs provide support rather than independent attack turns.')
