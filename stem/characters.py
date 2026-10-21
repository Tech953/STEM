"""THORNS-derived character rules for Stem v2. Numerical scales are adaptations."""
import copy
ROLES={'Needlurgist': {'body': 1, 'tech': 4, 'percept': 2, 'rapport': 1}, 'NanoClad Scout': {'body': 4, 'tech': 1, 'percept': 2, 'rapport': 1}, 'Fractech Archivist': {'body': 1, 'tech': 3, 'percept': 3, 'rapport': 1}, 'Seam Mediator': {'body': 1, 'tech': 2, 'percept': 1, 'rapport': 4}, 'Metal-kin Artisan': {'body': 3, 'tech': 3, 'percept': 1, 'rapport': 1}, 'Light Reader': {'body': 1, 'tech': 1, 'percept': 4, 'rapport': 2}}
ATTRIBUTES={'body':'Physical resilience, movement and practical execution.','tech':'Craft, repair, node integration and technical control.','percept':'Observation, pattern discrimination and environmental interpretation.','rapport':'Negotiation, teaching, cooperation and voluntary communication.'}
ORIGINS=['WN_TOWER','CITY_CLOUD_S','ENACT_HILLS','AETHERGALE','Unspecified / itinerant']
FORMS=['Biological / augmented','Metal-kin','lightPROKT< concept','Other / unspecified']
AFFILIATIONS=['Independent','THORNS associate','Embrite associate','Sap Core associate','Lifestring.CO associate','Druid-Sec associate','Fractech student','WN_EDU student','ED.NET student','Harvet contractor','ANC.NI apprentice','MOD_OP apprentice','SPIDREsec pilgrim','NanoClad pilgrim','INTERnode researcher','MMTX< associate','WN_LAW aspirant','WN_MED aspirant','MILI_WN aspirant','OMNI-META.OPEND aspirant','SEC.IO aspirant']
# Ratings buy training, never unrestricted permission. Empty scopes mean recorded only in this chapter.
def skill(label,source,section,stat,nodes,description):
 return dict(label=label,source=source,section=section,stat=stat,nodes=nodes,description=description,active=bool(nodes))
SKILLS={
 'transversal':skill('Transversal','WN_TOWER','Leg|Spikes; SPIDREsec','body',['undercroft','mid'],'Movement through steep or compromised infrastructure.'),
 'fieldcraft':skill('Pilgrimage fieldcraft','AETHERGALE','CHECKPOINT.triad; CHECKPOINT.UNDERTOW','body',['fractlands'],'Practical route protection and expedition movement.'),
 'ballistics':skill('Wirelet / crystallin< ballistics','WN_TOWER','MOD_OP; Wirelet','body',['field_encounter'],'Registered crystallin ranged field encounters; this does not grant unrestricted weapons or institutional entry.'),
 'needlurgy':skill('Needlurgy / bio-nano ink','WN_TOWER','Needlurgy; ANC.NI','tech',['foothills','contact'],'Fine interface craft; does not authorize restricted augmentation.'),
 'seamllurgy':skill('seamLLurgy / seam control','WN_TOWER','seamLLurgy','tech',['web','contact'],'Bounded seam-interface control, not an exemption from meta regulation.'),
 'fractech':skill('Fractech / nodeTECH','WN_TOWER','Fractech; Greatweb','tech',['web','kho','peak','undertow'],'Node integration and safe parameter handling.'),
 'metallurgy':skill('Metallurgy / salvage','CITY_CLOUD_S','base.EN_KHO','tech',['mid','foothills','pyri'],'Repair, extraction and construction training.'),
 'crystallin':skill('Crystallin< / enneract craft','WN_TOWER','Crystallin<','tech',['gale','contact'],'Crystalline apparatus and enneract-reference handling.'),
 'resource':skill('Meta-break resource acquisition','AETHERGALE','Regional introduction; CHECKPOINT.triad','tech',['foothills'],'Provisioning knowledge; no infinite portable inventory.'),
 'arcane':skill('arcaneTECH / siphon_protocol','AETHERGALE','CHECKPOINT.GALE','tech',['gale'],'AETHER apparatus and energy-acquisition technique.'),
 'archive':skill('Archival / INTERnode analysis','ENACT_HILLS','INTERnode','tech',['archive','kho'],'Index analysis and narrative data comparison.'),
 'rune':skill('runeTECH / spark-core craft','ENACT_HILLS','UPPER RUNEHILLS','tech',['pyri'],'Training with metal-kin patterns; not authority over a person.'),
 'medtech':skill('medTech / extraction care','WN_TOWER','WN_MED','tech',['wn_med'],'Field treatment proficiency; client care at WN_MED has a separate contract gate.'),
 'necra':skill('Necramancer / necra-mod theory','ENACT_HILLS','Necramancer','tech',[],'Theory only at creation. MERC.DOT and other applicable verification are required for practice.'),
 'lifestring':skill('Life Strings / Corded Bio-Glass','WN_TOWER','Lifestring.CO; Corded Bio-Glass','tech',[],'Training record; does not permit extraction or grant resurrection.'),
 'druid':skill('Druid-Sec fractal ecology','WN_TOWER','Druid-Sec; The Harvet','percept',['fractlands'],'Read ecological geometry without assuming faction immunity.'),
 'percept':skill('Percept / semblance discrimination','CITY_CLOUD_S','ED.NET','percept',['undercroft','kho','archive'],'Distinguish representations from evidence.'),
 'light':skill('lightPROKT< interpretation','AETHERGALE','CHECKPOINT.CASC','percept',['kho','undertow'],'Interpret light manifestations without treating them as property.'),
 'aether':skill('AETHER / fractURAL affinity study','AETHERGALE','CHECKPOINT.GALE','percept',['gale','undertow'],'Learn to read concentrations and LYLINE / LLYINE relationships.'),
 'nullsurvey':skill('NULL_FIELD remote survey','NULL_FIELD.OMNI','CONTRAIL_UNDER>CONTRAIL>CONTRAIL; CASCADE.net','percept',['undertow'],'Remote observation only; no access to an unknown interior.'),
 'history':skill('Historical narrative analysis','CITY_CLOUD_S','ED.NET','percept',['archive','kho'],'Evaluate narrative fragments and context.'),
 'contracts':skill('Contract mediation / Merc Tag literacy','WN_TOWER','Merc Tag; The Arcturion','rapport',['web','peak'],'Negotiate within actual scope of a contract.'),
 'community':skill('Community craft / provision','ENACT_HILLS','FOOTHILL CUSP','rapport',['foothills','fractlands'],'Cooperative work and practical mutual assistance.'),
 'teaching':skill('Teaching / integration dialogue','ENACT_HILLS','PYRI; UPPER RUNEHILLS','rapport',['pyri','contact'],'Communicate an offer with room for refusal.'),
 'memetic':skill('Memetic analysis / contract rhetoric','ENACT_HILLS','ADMIN.COA; MMTX<','rapport',['peak'],'Interpret institutional rhetoric; does not grant coercive command.'),
}
MODS={
 'none':dict(label='No installed mod',nodes=[],stat=None,source='Prototype option',gate=None),
 'leg_spikes':dict(label='LEG|SPIKES',nodes=['undercroft','mid'],stat='body',source='WN_TOWER / SPIDREsec',gate='registered'),
 'meta_fingers':dict(label='Meta-Fingers (regulated)',nodes=['web','contact'],stat='tech',source='WN_TOWER / MOD_OP',gate='registered'),
 'bio_glass':dict(label='Corded Bio-Glass interface',nodes=['contact'],stat='tech',source='WN_TOWER / Corded Bio-Glass',gate='registered'),
 'crystallin':dict(label='Crystallin< retrofit',nodes=['gale'],stat='tech',source='WN_TOWER / >CRYSTL-IN',gate='registered'),
}
AFFINITIES=['None declared','Metallurgy','Fractech','Druid-Sec geometry','fractURAL / AETHER','Bio-nano','lightPROKT< study','Necra-mod theory']
PERMITS=['black.dot','Merc Tag','WN_EDU','ED.NET','MERC.DOT','admin.OS','adminENACT']
PRESETS={
 'Needlurgist':{'needlurgy':2,'seamllurgy':1,'crystallin':1,'metallurgy':1,'contracts':1},
 'NanoClad Scout':{'transversal':2,'fieldcraft':2,'aether':1,'nullsurvey':1},
 'Fractech Archivist':{'fractech':2,'archive':2,'percept':1,'history':1},
 'Seam Mediator':{'contracts':2,'teaching':2,'community':1,'memetic':1},
 'Metal-kin Artisan':{'metallurgy':2,'rune':2,'community':1,'transversal':1},
 'Light Reader':{'light':2,'percept':2,'aether':1,'history':1},
}

LEGACY_ROLES={'Surveyor':'Fractech Archivist','Wayfarer':'NanoClad Scout','Artisan':'Metal-kin Artisan','Mediator':'Seam Mediator'}
TEXT_LIMITS={'pronouns':40,'bio':10000,'goal':500,'boundary':500,'appearance':1000,'voice':500,'mannerisms':500,'age':50}
ACTIVE_SKILLS={'transversal','fieldcraft','needlurgy','seamllurgy','fractech','metallurgy','crystallin','resource','arcane','archive','rune','medtech','druid','percept','light','aether','nullsurvey','history','contracts','community','teaching','memetic'}
ACTIVE_SKILLS.add('ballistics')
EQUIPMENT={
 'leg_spikes':dict(label='LEG|SPIKES',skill='transversal'),
 'meta_fingers':dict(label='Meta-Fingers',skill='fractech'),
 'bio_glass':dict(label='Corded Bio-Glass',skill='medtech'),
 'crystallin':dict(label='Crystallin< retrofit',skill='crystallin'),
 'survey_lens':dict(label='Survey lens [adaptation]',skill='percept'),
 'filter_graft':dict(label='Filter graft [adaptation]',skill='fieldcraft'),
 'rest_regulator':dict(label='Rest regulator [adaptation]',skill='fieldcraft'),
 'resonance_link':dict(label='Resonance link [adaptation]',skill='contracts'),
}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def default(role='Fractech Archivist'):
 role=LEGACY_ROLES.get(role,role);require(role in ROLES,'Unknown discipline.')
 c=dict(schema=2,role=role,origin='WN_TOWER',form='Metal-kin' if role=='Metal-kin Artisan' else FORMS[0],affiliation=AFFILIATIONS[0],affinity=AFFINITIES[0],attributes=copy.deepcopy(ROLES[role]),skills=copy.deepcopy(PRESETS[role]),mod='none')
 c.update({k:'' for k in TEXT_LIMITS});return c
def validate(raw,role=None):
 require(type(raw)==dict,'Character must be an object.')
 role=LEGACY_ROLES.get(role or raw.get('role','Fractech Archivist'),role or raw.get('role','Fractech Archivist'))
 c=default(role);allowed=set(c)|{'legacy'};require(set(raw)<=allowed,'Unexpected field: experience, possessions and credentials are server managed.')
 require(type(raw.get('schema',2))==int and raw.get('schema',2) in [1,2],'Unsupported character schema.')
 c.update({k:v for k,v in raw.items() if k!='legacy'});c['schema']=2;c['role']=role
 for k,limit in TEXT_LIMITS.items():
  v=c[k];require(isinstance(v,str) and len(v)<=limit and all(ord(ch)>=32 or ch in '\n\t' for ch in v),'Invalid or oversized '+k+'.');c[k]=v.strip()
 for k,values in [('origin',ORIGINS),('form',FORMS),('affiliation',AFFILIATIONS),('affinity',AFFINITIES),('mod',MODS)]:require(isinstance(c[k],str) and c[k] in values,'Invalid '+k+'.')
 a=c['attributes'];require(type(a)==dict and set(a)==set(ATTRIBUTES) and all(type(v)==int and 1<=v<=4 for v in a.values()) and sum(a.values())==8,'Use four integer attributes 1–4 totaling 8.')
 skills=c['skills'];require(type(skills)==dict and set(skills)<=set(SKILLS) and all(type(v)==int and 0<=v<=3 for v in skills.values()) and sum(skills.values())<=6,'Use proficiency ratings 0–3 totaling at most 6.')
 c['skills']={k:v for k,v in skills.items() if v};return c
def ensure(p):
 if 'character' not in p:p['character']=default(p.get('build','Surveyor'))
 p.setdefault('credentials',[]);p.setdefault('loadout',[]);p.setdefault('care_benefits',0);p.setdefault('dialogue_log',[]);p.setdefault('relationships',{});p.setdefault('contract_history',[])
 return p['character']
def bonus(p,stat,skill=''):
 c=ensure(p);stat={'craft':'tech','voice':'rapport'}.get(stat,stat)
 attribute=c['attributes'][stat];training=min(2,c['skills'].get(skill,0));equipment=min(2,sum(EQUIPMENT[m]['skill']==skill for m in p.get('loadout',[]) if m in EQUIPMENT and 'black.dot' in p['credentials']))
 xp=min(2,p.get('xp',0)//3);conditions=min(5,len(p.get('injuries',[]))+len(p.get('ailments',[]))+sum(p.get(k,0)>=70 for k in ['thirst','food_need','sleep']))
 return dict(attribute=attribute,training=training,equipment=equipment,experience=xp,conditions=conditions,total=attribute+min(2,training+equipment)+xp-conditions)
def sheet(p):
 c=copy.deepcopy(ensure(p));c.update(credentials=p['credentials'][:],loadout=p['loadout'][:],injuries=p.get('injuries',[])[:],ailments=p.get('ailments',[])[:],sleep=p.get('sleep',0),care_benefits=p['care_benefits']);return c
def catalog():
 skills=copy.deepcopy(SKILLS)
 for k,v in skills.items():v['active']=k in ACTIVE_SKILLS;v['description']=v['description'].split(';')[0];v['usage']='Used by Stem checks' if v['active'] else 'Recorded only; necra practice and Life String extraction are not implemented'
 return dict(attributes=ATTRIBUTES,roles=ROLES,origins=ORIGINS,forms=FORMS,affiliations=AFFILIATIONS,affinities=AFFINITIES,skills=skills,mods=MODS,equipment=EQUIPMENT,presets={k:default(k) for k in ROLES},text_limits=TEXT_LIMITS)
