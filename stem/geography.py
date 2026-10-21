"""Playable interpretation of the two uploaded drawings, not a surveyed scale map."""
from collections import deque
import re
MIN_X,MAX_X,MIN_Y,MAX_Y=-18,18,-12,12
SPAWN=[-10,3]
# coords register visible relative placement; district/checkpoint subpositions use DOCX topology.
def place(name,x,y,region,services,description,source,confidence='interpreted'):
 return dict(name=name,pos=[x,y],region=region,services=services.split(),description=description,source=source,confidence=confidence)
LANDMARKS={
 'thorns':place('The THORNS Encampment',-10,3,'WN_TOWER','shelter board craft','Patched bio-plast canopies sit below the Needle’s western approach. Fabricators compare route records and repair the layers that keep pilgrims moving.','overview: labeled encampment; WN_TOWER / Bio-Plast Encampment','high label / approximate placement'),
 'arcturion':place('The Arcturion',-11,0,'WN_TOWER','shelter board register trade','An inn and portfolio exchange at WN_REZ; worn worktables hold Merc Tag proposals alongside unfinished biographies.','DOCX: WN_REZ; inset: settlement approach'),
 'wn_tower':place('Witches Needle',-12,-3,'WN_TOWER','board lesson','The drawn tower rises from its ringed infrastructure. Its height belongs to a vertical district system, not an ordinary flat road.','overview: Witches Needle; inset: tower and ring structures','high label / approximate placement'),
 'greatweb':place('Greatweb Approach',-12,-1,'WN_TOWER','repair survey','An exposed service approach connects the lower districts to geometric feedback infrastructure. Public repairs do not grant unrestricted network control.','inset: rings and connecting line; DOCX: Greatweb'),
 'undercroft':place('Undercroft.Beta',-14,1,'WN_TOWER','salvage shelter','Darkwood ash gathers in low infrastructure hollows. Unregulated advertisements compete with patched, ordinary shelters.','inset: lower approach; DOCX: Undercroft.Beta'),
 'lower_burgs':place('The Lower_Burgs',-14,-2,'WN_TOWER','shelter trade craft','Community tool benches and Embrite-passed equipment make everyday repairs visible beside the larger city framework.','inset: grouped settlement blocks; DOCX: Lower_Burgs'),
 'blackdot':place('Black.Dot Outpost',-10,-2,'WN_TOWER','register mods','Verification instruments record bounded augmentation scopes. Registration is a working relationship, not an administrator identity.','DOCX: Black.Dot outposts; inset placement interpretation'),
 'spidre':place('SPIDREsec Pilgrim Rail',-13,2,'WN_TOWER','mods board','LEG|SPIKES users check vertical guide lines before beginning their maintenance routes around the Greatweb.','DOCX: SPIDREsec; inset infrastructure approach'),
 'mod_op':place('MOD_OP Exchange',-11,-4,'WN_TOWER','mods craft trade','Darkwood carvings and crystallin interfaces are offered through verifiable exchanges. The counter records materials and commitments, not universal currency.','DOCX: MOD_OP; district placement interpretation'),
 'wn_med':place('WN_MED Contract Desk',-10,-4,'WN_TOWER','medical_contract','A contracted service desk keeps its client list separate from public route traffic. Coverage requires an earned care relationship.','DOCX: WN_MED; district placement interpretation'),
 'harvet':place('The Harvet Woodland',13,5,'WN_TOWER','board survey salvage','The eastern woodland drawn in dense branching marks supports darkwood extraction cycles and competing needs for recovery and provision.','overview: The Harvet label; DOCX: The Harvet','high label / approximate placement'),
 'vines':place('The Vines',-13,9,'WN_TOWER','forage survey','A broad southwestern thicket follows the vine-like enclosure in the drawing. Its local ecology and inhabitants are generated Stem material.','overview: The Vines label','high label / approximate placement'),
 'ind_crux':place('Ind.Crux Route Marker',-6,-5,'ENACT_HILLS','board survey','The mapped label sits near an open route between the western settlements and northern woodland. Its spelling and function remain provisional.','overview: label read approximately as Ind.Crux','provisional transcription'),
 'amp_lands':place('Amp Lands',0,-8,'ENACT_HILLS','forage survey','Branching woodland encloses the northern plain. The drawing’s Amp Lands label anchors this generated field habitat.','overview: Amp Lands label','high label / approximate placement'),
 'foothills':place('FOOTHILL CUSP',0,-3,'ENACT_HILLS','shelter board trade care','Cooking, washing, cultivation and household repairs distinguish this civilian territory from the archival boundary above it.','DOCX: FOOTHILL CUSP; overview: northern settlement below woodland'),
 'runehills':place('UPPER RUNEHILLS Approach',2,-5,'ENACT_HILLS','lesson craft','Worked metal forms and an offered lesson mark an approach to PYRI’s teachings. Institutional certification remains distinct from goodwill.','DOCX: UPPER RUNEHILLS; mountain/settlement interpretation'),
 'gravesite':place('GRAVESITE Boundary',4,-6,'ENACT_HILLS','survey','SEC.IO marks the archival boundary. You can read exterior records; the interior is not an accessible public route.','DOCX: GRAVESITE; map placement inferred'),
 'base_kho':place('base.EN_KHO',6,0,'CITY_CLOUD_S','shelter salvage board','Salvaged metal sorting platforms sit below the drawn eastern mountain complex. The educational network is embedded in the construction.','overview: eastern mountain settlement; DOCX: base.EN_KHO'),
 'ed_net':place('ED.NET',7,-1,'CITY_CLOUD_S','lesson survey','KHO’s bounded projection contrasts a record with what can actually be observed. Learning here is specific rather than unrestricted access.','DOCX: ED.NET; eastern mountain placement interpretation'),
 'mid':place('Plat.EN_MID Approach',8,1,'CITY_CLOUD_S','salvage mods','Functional shelters and layered bio-mod repairs frame a hazardous middle-sector approach. There is no implied public security guarantee.','DOCX: Plat.EN_MID; mountains on overview'),
 'peak':place('PEAK.EN_PERCEPT Boundary',9,-2,'CITY_CLOUD_S','survey','Permission indicators sit above the mountain passages. A reputation record cannot substitute for institutional clearance.','DOCX: PEAK.EN_PERCEPT; upper mountain placement interpretation'),
 'triad':place('CHECKPOINT.triad',-2,5,'AETHERGALE','shelter board trade','The first tent routes open into jade and rose currents. NanoClad scouts compare the cost of each dustland crossing.','DOCX: CHECKPOINT.triad; overview: tent forms near southern open land'),
 'resid':place('CHECKPOINT.RESID',2,8,'AETHERGALE','shelter free_provision care','Pilgrim provision is offered freely under PAMAN DAL’s guidance. A lightPROKT< tree marks filtered water and shared refuge.','DOCX: CHECKPOINT.RESID; southern dustland waypoint inferred'),
 'gale':place('CHECKPOINT.GALE',5,6,'AETHERGALE','survey board craft','Crystallin instruments register the AETHER swirls represented by the drawing’s southern curling marks.','DOCX: CHECKPOINT.GALE; overview: southern swirl field'),
 'casc':place('CHECKPOINT.CASC',8,9,'AETHERGALE','shelter survey','At the eastern dustland edge, light manifestations mingle with the field. Lila’s presence is a source character; Stem does not resolve Khi’s documented condition.','DOCX: CHECKPOINT.CASC; eastern dustland placement inferred'),
 'undertow':place('CHECKPOINT.UNDERTOW',12,10,'AETHERGALE','shelter board remote','NanoClad observers maintain a border-facing record. Remote percept is distinguished from travel through the barrier.','DOCX: CHECKPOINT.UNDERTOW; southern/eastern border interpretation'),
 'red_gate':place('RED>GATE> Observation Line',14,11,'AETHERGALE','remote survey','The gate resists crossing and integration. These coordinates identify an observation approach, not the gate’s interior.','DOCX: RED>GATE>; inferred border placement'),
 'northern_spiral':place('Northern Spiral Observation',11,-8,'ENACT_HILLS','survey','A chain-linked spiral and unusual structures appear in the northeastern drawing. The handwritten label is not confidently transcribed, so no canonical identity is assigned.','overview: northeastern spiral feature','visible shape / uncertain label'),
}
ALIASES={'wn tower':'wn_tower','wn_tower':'wn_tower','needle':'wn_tower','thorns encampment':'thorns','the thorns':'thorns','city cloud s':'base_kho','city_cloud_s':'base_kho','kho':'ed_net','pyri':'runehills','black dot':'blackdot','resid':'resid','red gate':'red_gate','foothill cusp':'foothills','the harvet':'harvet','the vines':'vines'}
RIVER=[(-7,-10),(-4,-8),(0,-9),(4,-8),(7,-6),(9,-5)]

def norm(s):return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
def resolve(s):
 n=norm(s)
 for k,v in LANDMARKS.items():
  if n in [norm(k),norm(v['name'])]:return k
 for alias,k in ALIASES.items():
  if n==norm(alias):return k
 return None

def landmark(x,y):return next((dict(v,id=k) for k,v in LANDMARKS.items() if v['pos']==[x,y]),None)
def river_cells():
 cells=set()
 for (x0,y0),(x1,y1) in zip(RIVER,RIVER[1:]):
  n=max(abs(x1-x0),abs(y1-y0))
  for i in range(n+1):cells.add((round(x0+(x1-x0)*i/n),round(y0+(y1-y0)*i/n)))
 return cells
RIVER_CELLS=river_cells();BRIDGES={(-4,-8),(4,-8),(7,-6)}
def info(x,y):
 lm=landmark(x,y)
 if not(MIN_X<=x<=MAX_X and MIN_Y<=y<=MAX_Y):return dict(terrain='outside drawing',passable=False,region='AETHERGALE',cost=1,landmark=None)
 if y<=-11:return dict(terrain='northern water',passable=False,region='ENACT_HILLS',cost=1,landmark=lm)
 if y>=12 and x>=12:return dict(terrain='RED>GATE> barrier',passable=False,region='AETHERGALE',cost=1,landmark=lm)
 if (x,y) in RIVER_CELLS and (x,y) not in BRIDGES and not lm:return dict(terrain='river channel',passable=False,region='ENACT_HILLS',cost=1,landmark=lm)
 if lm:return dict(terrain='landmark approach',passable=True,region=lm['region'],cost=1,landmark=lm)
 if (x,y) in BRIDGES:return dict(terrain='interpreted bridge',passable=True,region='ENACT_HILLS',cost=1,landmark=None)
 if x>=5 and -3<=y<=3:
  terrain='mountain path';region='CITY_CLOUD_S';cost=2
 elif (x>=10 and -1<=y<=8) or (x<=-8 and y>=6):terrain='woodland';region='WN_TOWER';cost=2
 elif x<-7 and y<6:terrain='Needle hinterland';region='WN_TOWER';cost=1
 elif y>=4:terrain='dustland';region='AETHERGALE';cost=2
 else:terrain='foothill';region='ENACT_HILLS';cost=1
 return dict(terrain=terrain,passable=True,region=region,cost=cost,landmark=None)
def route(start,goal):
 if not info(*goal)['passable']:raise ValueError('That destination is not physically accessible.')
 q=deque([tuple(start)]);prev={tuple(start):None};goal=tuple(goal)
 while q:
  node=q.popleft()
  if node==goal:break
  for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]:
   dest=(node[0]+dx,node[1]+dy)
   if dest not in prev and info(*dest)['passable']:prev[dest]=node;q.append(dest)
 if goal not in prev:raise ValueError('No traversable route was found within the interpreted map.')
 path=[];node=goal
 while prev[node] is not None:path.append(list(node));node=prev[node]
 return list(reversed(path))
def public(p):
 return dict(bounds=[MIN_X,MAX_X,MIN_Y,MAX_Y],landmarks=[dict(v,id=k) for k,v in LANDMARKS.items()],position=p['pos'],route=p.get('route',[]),destination=p.get('destination'),note='Interpreted from your photographs; exact scale, unlabeled features and district placement are provisional. Travel follows land, bridges and mountain approaches one sector at a time.')
def project(x,y):return (40+(x-MIN_X)*22,40+(y-MIN_Y)*22)
def svg():
 width=880;height=620;parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">Stem interpreted world routes</title><desc id="desc">Western Needle and THORNS encampment, northern foothills, eastern mountain construction and woodland, southern dustlands, river channels and border observation.</desc><rect width="880" height="620" fill="#0d1617"/>']
 colors={'WN_TOWER':'#263e31','ENACT_HILLS':'#4a4030','CITY_CLOUD_S':'#2c455a','AETHERGALE':'#3d3447'}
 for y in range(MIN_Y,MAX_Y+1):
  for x in range(MIN_X,MAX_X+1):
   a,b=project(x,y);t=info(x,y);color=colors[t['region']] if t['passable'] else '#101e2d';parts.append(f'<rect x="{a-10}" y="{b-10}" width="21" height="21" fill="{color}"/>')
   if t['terrain']=='woodland':parts.append(f'<path d="M{a-4},{b+4} L{a},{b-5} L{a+4},{b+4}" fill="none" stroke="#6b9675" stroke-width="1"/>')
   if t['terrain']=='mountain path':parts.append(f'<path d="M{a-6},{b+5} L{a},{b-6} L{a+6},{b+5}" fill="none" stroke="#9cb6c5" stroke-width="1"/>')
 for k,v in LANDMARKS.items():
  a,b=project(*v['pos']);parts.append(f'<circle cx="{a}" cy="{b}" r="4" fill="#e4c98b"/>')
 # Carefully spaced major region labels; detailed labels stay in the interactive list.
 for label,x,y in [('WN_TOWER',-16,-6),('ENACT_HILLS',-2,-1),('CITY_CLOUD_S',5,-4),('AETHERGALE',-1,11)]:
  a,b=project(x,y);parts.append(f'<text x="{a}" y="{b}" fill="#edf0df" font-family="monospace" font-size="13">{label}</text>')
 parts.append('<text x="30" y="607" fill="#aebead" font-family="monospace" font-size="10">Map interpretation / one sector per step / gold points identify anchored landmarks</text></svg>');return ''.join(parts)
