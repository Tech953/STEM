import copy,json,sys,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import world as w,geography as g,characters as c,adventure as a,server as s

class IntegratedTests(unittest.TestCase):
 def setUp(self):
  dice=patch('world.secrets.randbelow',return_value=19);dice.start();self.addCleanup(dice.stop)
  self.w=w.new_world('integrated-map', ruleset='legacy');self.w['code']='TEST';self.p=w.add_player(self.w,'Joss','Needlurgist');self.w['started']=True
 def act(self,text):
  i,e=w.parse(text);self.assertIsNone(e,text);return w.act(self.w,self.p,i,text)
 def relocate(self,k):
  self.p['pos']=g.LANDMARKS[k]['pos'][:];w.visit(self.w,*self.p['pos'])
 def test_every_landmark_has_actual_land_route(self):
  for k,l in g.LANDMARKS.items():
   prev=g.SPAWN
   for node in g.route(g.SPAWN,l['pos']):
    self.assertTrue(g.info(*node)['passable']);self.assertEqual(abs(node[0]-prev[0])+abs(node[1]-prev[1]),1);prev=node
   self.assertEqual(prev,l['pos'])
  self.assertFalse(g.info(14,12)['passable']);self.assertFalse(g.info(0,-12)['passable'])
  ET.fromstring(g.svg())
 def test_map_does_not_use_original_quadrants(self):
  self.assertEqual(w.region_at(13,5,'atlas'),'WN_TOWER');self.assertEqual(w.region_at(13,5,'legacy'),'AETHERGALE')
  self.assertEqual(w.visit(self.w,13,5)['title'],'The Harvet Woodland');self.assertEqual(self.p['pos'],g.SPAWN)
 def test_route_planning_is_free_step_costs_time(self):
  original=self.p['pos'][:];cycle=self.w['tick'];result=self.act('go to Black.Dot Outpost');self.assertFalse(result['time_spent']);self.assertEqual(self.p['pos'],original)
  path=self.p['route'][:];self.assertEqual(len(path),5)
  with patch('world.secrets.randbelow',return_value=19):
   self.act('travel next');self.assertEqual(self.p['pos'],path[0]);self.assertGreater(self.w['tick'],cycle);self.assertEqual(len(self.p['route']),4)
  self.assertEqual(self.p['destination'],'Black.Dot Outpost')
 def test_physical_river_and_border_rejection(self):
  self.p['pos']=[14,11];w.visit(self.w,14,11)
  before=self.w['tick']
  with self.assertRaises(ValueError):self.act('south')
  self.assertEqual(self.w['tick'],before);self.assertEqual(self.p['pos'],[14,11])
 def test_thorns_template_and_budget_validation(self):
  template=c.default('NanoClad Scout');template['schema']=1;template.pop('role')
  loaded=c.validate(template,'NanoClad Scout');self.assertEqual(loaded['schema'],2);self.assertEqual(len(c.SKILLS),25)
  for attack in ['privilege','points','bool','training']:
   raw=copy.deepcopy(loaded)
   if attack=='privilege':raw['credentials']=['admin.OS']
   elif attack=='points':raw['attributes']['tech']=4
   elif attack=='bool':raw['attributes']['tech']=True
   else:raw['skills']={'fieldcraft':3,'contracts':3,'percept':1}
   with self.assertRaises(ValueError):c.validate(raw)
 def test_character_registered_in_place_and_dialogue_history(self):
  self.p['character'].update(appearance='Weathered bio-plast coat',voice='quiet and exact',mannerisms='checks every seam',goal='Restore exhausted routes',boundary='No memory extraction')
  self.act('ask about place');self.act('ask about history')
  record=self.p['dialogue_log'][-1];self.assertEqual(record['character']['appearance'],'Weathered bio-plast coat');self.assertIn('Restore exhausted routes',record['response']);self.assertIn('No memory extraction',record['response']);self.assertEqual(record['npc'],'Iri Thread');self.assertEqual(len(self.p['dialogue_log']),2)
  self.relocate('ed_net');self.act('ask about history');self.assertEqual(self.p['dialogue_log'][-1]['npc'],'KHO');self.assertEqual(len(self.p['relationships']),2)
 def test_every_named_place_has_characterized_dialogue(self):
  for k in g.LANDMARKS:
   self.relocate(k);before=len(self.p['dialogue_log']);self.act('ask about place');self.assertEqual(len(self.p['dialogue_log']),before+1);self.assertTrue(w.snapshot(self.w,self.p)['dialogue_options'])
 def test_delivery_costs_and_once_only_reward(self):
  self.act('accept delivery contract');cm=copy.deepcopy(self.p['contract']);self.p['pos']=cm['target'][:];w.visit(self.w,*self.p['pos']);before=self.p['inventory'].copy()
  self.act('fulfill');self.assertIsNone(self.p['contract']);self.assertEqual(self.p['inventory']['food'],before['food']);self.assertEqual(self.p['inventory']['water'],before['water']+1);self.assertEqual(len(self.p['contract_history']),1);self.assertEqual(self.p['care_benefits'],1)
  with self.assertRaises(ValueError):self.act('fulfill')
 def test_restoration_requires_successful_work_at_target(self):
  self.act('accept restoration contract');before=self.p['pos'][:];route=self.act('go to commitment');self.assertFalse(route['time_spent']);self.assertEqual(self.p['pos'],before);self.assertEqual(self.p['route'][-1],self.p['contract']['target']);self.p['pos']=self.p['contract']['target'][:];cell=w.local(self.w,self.p);cell['stability']=30
  with self.assertRaises(ValueError):self.act('fulfill')
  with patch('world.secrets.randbelow',return_value=19):self.act('repair the habitat')
  self.assertEqual(self.p['contract']['progress'],1);self.act('fulfill');self.assertIsNone(self.p['contract'])
 def test_diplomacy_reputation_and_failure(self):
  self.act('accept diplomacy contract');self.p['pos']=self.p['contract']['target'][:];w.local(self.w,self.p);f=self.p['contract']['faction'];self.w['reputation'][f]=6
  with patch('world.secrets.randbelow',return_value=0):result=self.act('fulfill')
  self.assertIsNotNone(self.p['contract']);self.assertIn('rapport',result['mechanics']);self.assertIn('reputation +1',result['mechanics']);self.assertIn('vs 10',result['mechanics'])
  with patch('world.secrets.randbelow',return_value=19):self.act('fulfill')
  self.assertEqual(self.w['reputation'][f],8)
 def test_abandon_and_care_benefits_are_personal(self):
  other=w.add_player(self.w,'Other','Light Reader');self.act('accept survey contract');f=self.p['contract']['faction'];self.act('abandon contract');self.assertEqual(self.w['reputation'][f],-1);self.assertEqual(self.p['karma'],-1);self.assertEqual(other['care_benefits'],0)
 def test_registered_mods_and_slots(self):
  self.p['character']['mod']='meta_fingers';self.relocate('blackdot');before=c.bonus(self.p,'tech','fractech');self.assertEqual(before['equipment'],0)
  self.act('register');self.assertIn('black.dot',self.p['credentials']);self.assertIn('meta_fingers',self.p['loadout']);self.assertEqual(c.bonus(self.p,'tech','fractech')['equipment'],1)
  self.p['inventory']['scrap']=10;self.act('install survey_lens');self.act('install filter_graft')
  with self.assertRaises(ValueError):self.act('install bio_glass')
  self.act('remove filter_graft');self.act('install bio_glass');self.assertEqual(len(self.p['loadout']),3)
 def test_sleep_injuries_ailments_change_checks_and_treatment(self):
  self.p['sleep']=75;self.p['injuries']=['strained leg'];self.p['ailments']=['particulate irritation'];self.assertEqual(c.bonus(self.p,'tech','medtech')['conditions'],3)
  with patch('world.secrets.randbelow',return_value=19):self.act('treat')
  self.assertFalse(self.p['injuries']);self.assertTrue(self.p['ailments']);self.act('rest');self.assertEqual(self.p['sleep'],3)
 def test_resid_free_provision_and_wn_med_scope(self):
  self.relocate('resid');self.p.update(food_need=80,thirst=90);self.p['inventory']['scrap']=0;self.act('provision');self.assertEqual(self.p['thirst'],0);self.assertEqual(self.p['food_need'],0)
  self.relocate('wn_med')
  with self.assertRaises(ValueError):self.act('clinic')
  with self.assertRaises(ValueError):self.act('accept survey contract')
  self.act('accept delivery contract');target=self.p['contract']['target'];self.p['pos']=target[:];w.local(self.w,self.p);self.act('fulfill');self.assertIn('WN_MED care relationship',self.p['credentials'])
 def test_survival_recovery_never_claims_route_arrival(self):
  self.p['route']=[[-10,2]];self.p['destination']='A different site';self.p.update(health=1,thirst=100)
  out=self.act('travel next');self.assertEqual(self.p['pos'],g.SPAWN);self.assertNotIn('reached the registered route destination',out['text'])

class IntegratedPersistenceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'world.db');s.init_db(self.db);s.ACTIVE.clear()
  ch=c.default('Light Reader');ch.update(appearance='Prismatic layered coat',bio='A caravan witness',voice='reflective')
  self.h=s.request(dict(op='create',ruleset='legacy',name='Witness',build='Light Reader',character=ch,seed='atlas-persistence'))
 def tearDown(self):s.DB.close();self.tmp.cleanup();s.ACTIVE.clear()
 def call(self,op,**kw):
  state=s.fetch(self.h['code']);return s.request(dict(**self.h,op=op,revision=state['revision'],**kw))
 def test_restart_keeps_character_dialogue_route_and_contract(self):
  self.call('start');self.call('act',text='ask about history');self.call('act',text='accept delivery contract');self.call('act',text='go to Black.Dot Outpost');before=self.call('state');s.DB.close();s.init_db(self.db);after=self.call('state')
  for k in ['me','character_sheet','atlas','reputation']:self.assertEqual(before[k],after[k])
  self.assertEqual(len(after['reputation']),25);self.assertNotIn(self.h['token'],json.dumps(after))
 def test_legacy_world_migrates_without_moving_its_character(self):
  saved=s.fetch(self.h['code']);saved.pop('layout');saved.pop('spawn');saved['players'][0]['pos']=[20,-4];saved['cells']={};w.visit(saved,20,-4);saved['players'][0].pop('character');saved['players'][0]['build']='Surveyor';s.save(saved)
  state=self.call('state');self.assertIsNone(state['atlas']);self.assertEqual(state['me']['pos'],[20,-4]);self.assertEqual(state['character_sheet']['role'],'Fractech Archivist')
 def test_creation_template_rejects_forged_permissions(self):
  ch=c.default('Light Reader');ch['credentials']=['admin.OS']
  with self.assertRaises(ValueError):s.request(dict(op='create',ruleset='legacy',name='Forgery',build='Light Reader',character=ch))
 def test_edit_locks_and_character_template_works(self):
  ch=c.default('Light Reader');ch['appearance']='New appearance';self.call('character',build='Light Reader',character=ch);self.call('start')
  with self.assertRaises(ValueError):self.call('character',build='Light Reader',character=ch)
if __name__=='__main__':unittest.main()
