"""Stem integration for the shared Field Guide rules and existing simulation."""
import field_rules as rules


def setup(w,new=False):
    rules.ensure_world(w)
    if new:rules.enable(w,new=True)


def check(w,p,stat,dc,skill,engine,context,situation,npc,faction):
    action=context.get('action',p.get('_intent',{}).get('action','inspect'))
    if action in {'look','inspect','listen','inventory','map','goto','return','dismiss','abandon','business','wait'}:
        return True,'Confirmed records, voluntary exits and planning require no roll and award no XP.'
    return rules.roll(w,p,stat,skill,dc,action,situation=situation,faction=faction,npc=npc,
                      support=action not in {'talk','dialogue','npc_talk','provision','clinic','recruit','npc_task'})


def settle_progression(w,p,intent):
    before=p.pop('_field_xp_before',p.get('xp',0));delta=p.get('xp',0)-before
    if delta<=0:return ''
    p['xp']=before
    action=intent['action'];cm=p.get('_contract_before',{})
    identity=('contract:'+str(cm.get('id',str(cm.get('target'))+':'+str(cm.get('accepted_tick'))))
              if action in {'fulfill','survey'} and cm else 'site:'+rules.site_key(p)+':'+action)
    amount=rules.award(w,p,identity,delta)
    return f' XP recorded: {amount} within the session cap; repeated resolved situations pay once.'


def advance(w,p,cycles,engine,world_clock=True):
    # Personal needs affect the participant, never idle remote seats.
    for _ in range(cycles):
        engine.survival.advance(w,p,1)
        rules.companion_cycle(w,p,1)
        if world_clock:
            engine.tick(w,'active field cycle')
            c=engine.local(w,p)
            rules.after_cycle(w,p,dict(c,severe_storm=engine.weather(w,c) in {'particulate storm','contrail squall'}))


def run(w,p,action,target,engine):
    c=engine.local(w,p)
    result=rules.handle(w,p,action,target,c)
    advance(w,p,result['cycles'],engine)
    pending=result.get('pending');e=rules.scene(w,p)
    if pending and pending['kind']=='full_rest' and e and any(rules.live(a) and a['disposition']=='defensive' for a in e['actors']):
        pending=None;result['text']+=' A defensive arrival interrupts the rest. Reserved rations remain spent.'
    rules.recovery(p,pending)
    if e and e.get('combat') and e['combat'].pop('conclude_pending',False):
        first=True
        for identity in e['combat']['pcs']:
            person=next((x for x in w['players'] if x['id']==identity),None)
            if person:
                # Incapacitation recovery is an explicit two-cycle rescue, not a free read.
                if person['health']==0:
                    advance(w,person,2,engine,world_clock=False)
                advance(w,person,1,engine,world_clock=first);first=False
    p['last_result']=result['text'];p['last_action']=dict(action=action,target=target,input='',mechanics=result['mechanics'],tick=w['tick'])
    engine.emit(w,p['name']+': '+result['text']+(' '+result['mechanics'] if result['mechanics'] else ''),'action',p['pos'][:])
    w['revision']+=1
    return dict(text=result['text'],mechanics=result['mechanics'],intent=dict(action=action,target=target),time_spent=bool(result['cycles']))


def native(w,p,intent,engine):
    action=intent['action']
    mapping={'eat':'field_eat','drink':'field_drink','rest':'field_breather','treat':'field_treat',
             'attack':'field_attack','shoot':'field_shoot','guard':'field_guard','flee':'field_withdraw','parley':'field_parley'}
    if action not in mapping:return None
    field=mapping[action];e=rules.scene(w,p);target=intent.get('target','')
    if action in {'attack','shoot','guard','flee','parley'}:
        rules.require(e and e['actors'],'No present field encounter. Travel or spend a watch; inspect the field panel.')
        actor=next((a for a in e['actors'] if rules.live(a)),None)
        target=actor['instance_id'] if actor else ''
        if action!='parley' and (not e.get('combat') or e['combat']['finished']):
            return run(w,p,'field_engage','',engine)
    return run(w,p,field,target,engine)
