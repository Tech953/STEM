"""Finite local businesses and practical, persistent public infrastructure."""
import copy
import geography

ACTS={'business','buy','sell','business_work','infrastructure','operate','relay'}
GOODS={'food':1,'water':1,'seed':2,'medkit':3}

def business(w,p,engine):
    lm=geography.landmark(*p['pos']) if w.get('layout')=='atlas' else None
    if not lm or not any(k in lm['services'] for k in ['trade','craft','mods','register']):return None
    businesses=w.setdefault('businesses',{})
    if lm['id'] not in businesses:
        keeper=engine.present_actor(w,p)
        businesses[lm['id']]=dict(id=lm['id'],name=lm['name']+' field exchange',faction=keeper['faction'],
            stock=dict(food=4,water=5,seed=2,medkit=2),reserve=6,condition=75,demand=0,
            ledger=[],last_restock=w['tick'],worker=keeper['name'])
    return businesses[lm['id']]

def prices(w,p,b):
    score=w['reputation'].get(b['faction'],0)+p.get('personal_reputation',{}).get(b['faction'],0)/2
    adjustment=(-1 if score>=10 else 1 if score<=-5 else 0)+b['demand']
    return {k:max(1,v+adjustment) for k,v in GOODS.items()}

def public(w,p,engine):
    b=business(w,p,engine)
    return dict(**copy.deepcopy(b),prices=prices(w,p,b),sell_price=1) if b else None

def ledger(w,b,text):
    b['ledger'].append(dict(tick=w['tick'],text=text));b['ledger']=b['ledger'][-30:]

def handle(w,p,intent,raw,engine):
    op=intent['action'];target=intent.get('target','');c=engine.local(w,p);b=business(w,p,engine)
    out='';mechanics='';time=True
    if op in {'business','buy','sell','business_work'}:
        engine.require(b is not None,'Visit a mapped trade, craft, registration or mod exchange.')
        context=dict(faction=b['faction'],npc=engine.present_actor(w,p)['id'])
        if op=='business':
            time=False;ok,mechanics=engine.check(w,p,'percept',10,'resource',context)
            out=f"{b['name']} offers {b['stock']}. Prices in scrap: {prices(w,p,b)}. Reserve {b['reserve']}; condition {b['condition']}. "
            out+=('The demand and maintenance record appear consistent.' if ok else 'Public prices remain readable; the underlying ledger needs a closer review.')
        elif op=='buy':
            engine.require(target in GOODS,'Buy food, water, seed or medkit.');cost=prices(w,p,b)[target]
            engine.require(b['stock'][target]>0,'The business has no stock of that item.');engine.require(p['inventory']['scrap']>=cost,'This purchase requires '+str(cost)+' scrap.')
            engine.require(b['reserve']+cost<=999,'The business reserve cannot accept more scrap.')
            engine.require(p['inventory'][target]<99,'Make room in your pack.')
            ok,mechanics=engine.check(w,p,'rapport',10,'contracts',context)
            if ok:
                p['inventory']['scrap']-=cost;p['inventory'][target]+=1;b['stock'][target]-=1;b['reserve']+=cost
                out=f"You buy one {target} for {cost} scrap. Both stock ledgers are updated.";ledger(w,b,p['name']+' bought '+target+'.')
            else:out='The transaction remains unsigned. No scrap or goods change hands.'
        elif op=='sell':
            engine.require(target in GOODS,'Sell food, water, seed or medkit.');engine.require(p['inventory'][target]>0,'You have no item to offer.')
            engine.require(b['reserve']>=1 and b['stock'][target]<20,'The business cannot accept that consignment.');engine.require(p['inventory']['scrap']<99,'Make room for payment.')
            ok,mechanics=engine.check(w,p,'rapport',10,'contracts',context)
            if ok:
                p['inventory'][target]-=1;p['inventory']['scrap']+=1;b['stock'][target]+=1;b['reserve']-=1
                out='The business buys one '+target+' for one scrap from its actual reserve.';ledger(w,b,p['name']+' sold '+target+'.')
            else:out='The consignment is declined; goods and reserve remain unchanged.'
        else:
            engine.require(p['inventory']['scrap']>=1,'Exchange maintenance requires one scrap.');engine.require(b['condition']<95,'This exchange is already maintained.')
            p['inventory']['scrap']-=1;ok,mechanics=engine.check(w,p,'tech',11,'metallurgy',context)
            if ok:
                b['condition']=min(100,b['condition']+15);p['xp']+=1;engine.standing(w,p,b['faction'],1)
                out='You spend one scrap to restore 15 business condition and record one issuer standing.';ledger(w,b,p['name']+' maintained the exchange.')
            else:out='The maintenance does not hold; its scrap is spent.'
    elif op=='infrastructure':
        time=False;ok,mechanics=engine.check(w,p,'percept',10,'fractech')
        out=f"Public infrastructure at {c['title']}: {c['feature']}; stability {c['stability']}, shelter {c['shelter']}, relay {c.get('relay',0)}, water stock {c['water']}. "
        out+=('The weak joints and safe working scope are distinguishable.' if ok else 'The field indices are confirmed, but the fault location remains uncertain.')
    elif op=='operate':
        engine.require(c['water']>0 and p['inventory']['water']<99,'The accessible apparatus needs local water and pack space.')
        ok,mechanics=engine.check(w,p,'tech',11,'fractech')
        if ok:
            c['water']-=1;p['inventory']['water']+=1;c['pressure']=max(0,c['pressure']-2)
            engine.record(c,w,p,'operated the public water apparatus within its recorded scope.');out='You transfer one actual local water through the accessible apparatus.'
        else:out='The safe parameter test fails; no supply moves.'
    elif op=='relay':
        engine.require(c.get('relay',0)<2,'The public field relay is fully maintained.');engine.require(p['inventory']['scrap']>=3,'A relay build requires three scrap.')
        p['inventory']['scrap']-=3;ok,mechanics=engine.check(w,p,'tech',13,'fractech')
        if ok:
            c['relay']=c.get('relay',0)+1;p['xp']+=1;engine.standing(w,p,engine.REGIONS[c['region']]['faction'],1)
            engine.record(c,w,p,'built a bounded public field relay.');out='The public relay gains one level and supports later field checks at this sector.'
        else:out='The relay does not integrate; its three scrap are spent.'
    else:return None
    return dict(text=out,mechanics=mechanics,intent=intent,time_spent=time)

def cycle(w,engine):
    if w['tick']%12:return
    for b in w.get('businesses',{}).values():
        lm=geography.LANDMARKS[b['id']];c=w['cells'].get(engine.key(*lm['pos']))
        if not c:continue
        storm=engine.weather(w,c) in {'particulate storm','contrail squall'}
        b['condition']=max(0,b['condition']-(3 if storm else 1));b['demand']=1 if storm or b['condition']<35 else 0
        # Restock transfers from physical local stores; it does not fabricate products.
        if b['condition']>=35:
            for good in ['food','water']:
                amount=min(2,c[good],max(0,8-b['stock'][good]));c[good]-=amount;b['stock'][good]+=amount
        b['last_restock']=w['tick'];ledger(w,b,'Reviewed demand and transferred available local provision into shop stock.')
