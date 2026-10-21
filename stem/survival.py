"""THORNS-derived needs, injuries and ailments; costs apply only to personal actions."""
def ensure(p):
 p.setdefault('sleep',0);p.setdefault('injuries',[]);p.setdefault('ailments',[]);p['inventory'].setdefault('medkit',2)
def harm(p,condition,ailment=False):
 ensure(p);field='ailments' if ailment else 'injuries'
 if condition not in p[field]:p[field].append(condition)
def advance(w,p,cycles=1):
 ensure(p)
 for _ in range(cycles):
  p['energy']=max(0,p['energy']-3);p['thirst']=min(100,p['thirst']+4);p['food_need']=min(100,p['food_need']+2);p['sleep']=min(100,p['sleep']+(2 if 'rest_regulator' in p.get('loadout',[]) and 'black.dot' in p.get('credentials',[]) else 3))
  damage=sum(p[k]>=90 for k in ['thirst','food_need','sleep'])*4+len(p['ailments'])
  p['health']=max(0,p['health']-damage)
  if p['health']==0:
   p.update(pos=w.get('spawn',[0,0])[:],health=40,energy=40,thirst=35,food_need=35,sleep=35,remote=False,route=[],destination=None)
   return True
 return False
