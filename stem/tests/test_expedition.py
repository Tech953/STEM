import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import world as w
import characters as chars
import companions as npc
import institutions as shops
import geography
import server
from narrator import Narrator

class ExpeditionTests(unittest.TestCase):
    def setUp(self):
        dice=patch('world.secrets.randbelow',return_value=19);dice.start();self.addCleanup(dice.stop)
        self.w=w.new_world('expedition-tests', ruleset='legacy');self.w['code']='TEST';self.p=w.add_player(self.w,'Ada','Needlurgist');self.w['started']=True
    def act(self,text):
        intent,error=w.parse(text);self.assertIsNone(error,text);return w.act(self.w,self.p,intent,text)
    def recruit(self,a=None):
        a=a or next(a for a in self.w['actors'] if a.get('owner') is None and [a['x'],a['y']]==self.p['pos'])
        self.act('recruit '+a['id']);self.assertEqual(a['owner'],self.p['id']);return a
    def place(self,key):
        self.p['pos']=geography.LANDMARKS[key]['pos'][:];w.visit(self.w,*self.p['pos'])
    def threat(self,hp=24):
        c=w.local(self.w,self.p);c['threat']=dict(id='threat',name='test route warden',health=hp,defense=12,attack=11,damage=7,state='watchful',intent='holding a route cache',lore='Generated construct',resolved=False);return c['threat']
    def test_context_and_standing_change_the_same_roll(self):
        c=w.local(self.w,self.p);c.update(shelter=0,stability=60)
        with patch('world.secrets.randbelow',return_value=4),patch('world.weather',return_value='still air'):
            self.assertFalse(w.check(self.w,self.p,'tech',10,'fractech',dict(action='restore'))[0])
            c['shelter']=1;self.assertTrue(w.check(self.w,self.p,'tech',10,'fractech',dict(action='restore'))[0])
            self.w['tick']=18;self.assertFalse(w.check(self.w,self.p,'tech',10,'fractech',dict(action='restore'))[0])
            self.w['reputation']['Druid-Sec']=5;self.assertTrue(w.check(self.w,self.p,'tech',10,'fractech',dict(action='restore'))[0])
            self.assertEqual(self.p['last_check']['reputation'],1)
        self.p.update(energy=0,injuries=['a','b','c'],ailments=['d','e'],thirst=100)
        with patch('world.secrets.randbelow',return_value=19):self.assertTrue(w.check(self.w,self.p,'body',99,'fieldcraft')[0])
        with patch('world.secrets.randbelow',return_value=0):self.assertFalse(w.check(self.w,self.p,'tech',1,'fractech')[0])
        self.assertEqual(self.p['last_check']['conditions'],5)
    def test_checks_cover_observation_dialogue_survival_and_records(self):
        for text,action in [('look','look'),('inspect the habitat','inspect'),('listen','listen'),('inventory','inventory'),('map','map'),('ask about history','dialogue'),('eat','eat'),('drink','drink'),('rest','rest'),('wait','wait'),('go to ED.NET','goto')]:
            out=self.act(text);self.assertIn('D20',out['mechanics']);self.assertEqual(self.p['last_check']['action'],action)
        self.assertEqual(len(self.p['check_log']),11)
    def test_failed_dialogue_retains_facts_and_characterization(self):
        self.p['character']['boundary']='No forced memory extraction'
        with patch('world.secrets.randbelow',return_value=0):out=self.act('ask about history')
        self.assertIn('provisional',out['text']);self.assertIn('No forced memory extraction',out['text']);self.assertEqual(len(self.p['dialogue_log']),1)
        self.assertFalse(self.p['last_check']['success']);self.assertEqual(self.w['tick'],0)
    def test_contract_acceptance_and_delivery_can_fail_without_duplication(self):
        pack=self.p['inventory'].copy()
        with patch('world.secrets.randbelow',return_value=0):self.act('accept delivery contract')
        self.assertIsNone(self.p['contract']);self.assertEqual(pack,self.p['inventory'])
        self.act('accept delivery contract');self.p['pos']=self.p['contract']['target'][:];w.local(self.w,self.p)
        with patch('world.secrets.randbelow',return_value=0):self.act('fulfill')
        self.assertIsNotNone(self.p['contract']);self.assertEqual(pack,self.p['inventory'])
        self.act('fulfill');self.assertIsNone(self.p['contract']);self.assertEqual(len(self.p['contract_history']),1)
    def test_recruit_decline_terms_and_cooldown(self):
        a=self.w['actors'][0];pack=self.p['inventory'].copy()
        with patch('world.secrets.randbelow',return_value=0):self.act('recruit '+a['id'])
        self.assertIsNone(a['owner']);self.assertEqual(pack,self.p['inventory'])
        with self.assertRaises(ValueError):self.act('recruit '+a['id'])
        self.w['tick']=5;before=a['inventory'].copy();self.recruit(a)
        for k in ['food','water']:
            self.assertEqual(self.p['inventory'][k],pack[k]-1);self.assertEqual(a['inventory'][k],before[k]+1)
    def test_two_companions_and_single_owner(self):
        first=self.recruit();self.recruit()
        third=dict(id='third',name='Third Traveler',x=self.p['pos'][0],y=self.p['pos'][1],role='repairer',need='food',activity='waiting',trust=0,last_help=-10)
        self.w['actors'].append(third);npc.ensure(self.w,third)
        with self.assertRaises(ValueError):self.act('recruit third')
        guest=w.add_player(self.w,'Guest','Seam Mediator')
        with self.assertRaises(ValueError):w.act(self.w,guest,dict(action='recruit',target=first['id']))
        with self.assertRaises(ValueError):w.act(self.w,guest,dict(action='dismiss',target=first['id']))
        self.assertEqual(len(self.p['companions']),2)
    def test_generated_lore_is_stable_and_dialogue_records_change(self):
        a=self.recruit();bio=a['character']['bio'];self.act('speak with '+a['id']+' about lore');before=a['memory'][-1]['response']
        self.act('task '+a['id']+' survey');self.act('speak with '+a['id']+' about plans')
        self.assertNotEqual(before,a['memory'][-1]['response']);self.assertEqual(bio,a['character']['bio']);self.assertGreater(len(bio),700)
        designation=npc.public(self.w,self.p,a);self.assertTrue(designation['items']);self.assertEqual(sum(designation['character']['attributes'].values()),8)
        self.assertIn('survey',designation['contract_viability']);self.assertEqual(self.p['dialogue_log'][-1]['npc'],a['name'])
    def test_companion_support_and_following_use_real_movement(self):
        a=self.w['actors'][0];a['character']=chars.default('NanoClad Scout');self.recruit(a);energy=a['energy'];self.act('north')
        self.assertEqual([a['x'],a['y']],self.p['pos']);self.assertEqual(self.p['last_check']['support'],1);self.assertLess(a['energy'],energy)
        old=self.p['pos'][:];self.act('go to ED.NET');self.assertEqual(self.p['pos'],old);self.assertEqual([a['x'],a['y']],old)
    def test_contract_readiness_accounts_for_faction_health_and_pack(self):
        a=self.recruit();self.act('accept delivery contract');f=self.p['contract']['faction'];a['personal_reputation'][f]=-11;a['health']=20;a['inventory']['food']=0
        v=npc.viability(self.w,self.p,a)['delivery'];self.assertFalse(v['viable']);self.assertIn('faction conflict',v['reasons']);self.assertIn('needs care',v['reasons'])
        self.assertIn('insufficient personal provisions',v['reasons'])
    def test_engagement_cycle_uses_npc_materials_and_preserves_player_needs(self):
        a=self.recruit();self.act('task '+a['id']+' repair');a['engagement']['phase']='observe';a['engagement']['last_work']=-20
        cell=w.local(self.w,self.p);cell['stability']=20;scrap=a['inventory']['scrap'];thirst=self.p['thirst']
        for _ in range(20):w.tick(self.w)
        self.assertEqual(a['inventory']['scrap'],scrap-1);self.assertTrue(any('Spent one personal scrap' in e['text'] for e in a['engagement']['events']))
        self.assertEqual(thirst,self.p['thirst']);self.assertGreaterEqual(a['engagement']['cycles'],5);self.assertTrue(cell['changes'])
    def test_unwilling_companion_withdraws_without_losing_possessions(self):
        a=self.recruit();pack=a['inventory'].copy();a['attitude']=10;self.w['tick']=7;w.tick(self.w)
        self.assertIsNone(a['owner']);self.assertNotIn(a['id'],self.p['companions']);self.assertEqual(pack,a['inventory'])
    def test_supply_requests_and_sharing_conserve_packs(self):
        a=self.recruit();total=a['inventory']['water']+self.p['inventory']['water'];self.act('share '+a['id']+' water');self.act('request '+a['id']+' water')
        self.assertEqual(total,a['inventory']['water']+self.p['inventory']['water'])
        a['inventory']['water']=1
        with self.assertRaises(ValueError):self.act('request '+a['id']+' water')
    def test_npc_care_and_release_keep_designation(self):
        a=self.recruit();a['health']=50;a['injuries']=['impact strain'];self.act('care for '+a['id']);self.assertEqual(a['health'],80);self.assertFalse(a['injuries'])
        lore=a['character']['bio'];self.act('dismiss '+a['id']);self.assertIsNone(a['owner']);self.assertEqual(lore,a['character']['bio'])
    def test_business_failure_and_transactions_conserve_reserves(self):
        self.place('arcturion');b=shops.business(self.w,self.p,w);pack=self.p['inventory'].copy();stock=b['stock'].copy();reserve=b['reserve']
        with patch('world.secrets.randbelow',return_value=0):self.act('buy water')
        self.assertEqual(pack,self.p['inventory']);self.assertEqual(stock,b['stock']);self.assertEqual(reserve,b['reserve'])
        self.act('buy water');self.assertEqual(self.p['inventory']['water'],pack['water']+1);self.assertEqual(b['stock']['water'],stock['water']-1)
        self.assertEqual(self.p['inventory']['scrap']+b['reserve'],pack['scrap']+reserve)
        self.act('sell food');self.assertEqual(self.p['inventory']['scrap']+b['reserve'],pack['scrap']+reserve)
    def test_business_restock_uses_real_local_stock_and_reputation_prices(self):
        self.place('arcturion');b=shops.business(self.w,self.p,w);c=w.local(self.w,self.p);total=c['water']+b['stock']['water'];self.w['tick']=12;shops.cycle(self.w,w)
        self.assertEqual(total,c['water']+b['stock']['water']);base=shops.prices(self.w,self.p,b)['medkit']
        self.w['reputation'][b['faction']]=20;self.assertLess(shops.prices(self.w,self.p,b)['medkit'],base)
    def test_infrastructure_checks_spend_real_materials_and_supplies(self):
        c=w.local(self.w,self.p);self.p['inventory']['scrap']=10
        with patch('world.secrets.randbelow',return_value=0):self.act('build relay')
        self.assertEqual(self.p['inventory']['scrap'],7);self.assertEqual(c.get('relay',0),0)
        self.act('build relay');self.assertEqual(c['relay'],1);self.assertEqual(self.p['inventory']['scrap'],4)
        old=c['water'];pack=self.p['inventory']['water'];self.act('operate infrastructure');self.assertEqual(self.p['inventory']['water'],pack+1)
        self.assertLessEqual(c['water'],old-1)
    def test_combat_resolution_and_cache_pay_only_once(self):
        t=self.threat(10);scrap=self.p['inventory']['scrap'];self.act('attack');self.assertEqual(t['health'],3);self.act('attack')
        self.assertTrue(t['resolved']);self.assertEqual(self.p['inventory']['scrap'],scrap+2)
        with self.assertRaises(ValueError):self.act('attack')
    def test_guard_companion_shares_actual_counteraction_damage(self):
        a=self.recruit();self.act('task '+a['id']+' guard');self.threat();health=a['health'];mine=self.p['health']
        with patch('world.secrets.randbelow',return_value=0):self.act('attack')
        self.assertEqual(a['health'],health-3);self.assertEqual(self.p['health'],mine-4)
    def test_parley_flee_and_registered_ballistics_have_distinct_outcomes(self):
        t=self.threat();scrap=self.p['inventory']['scrap'];self.act('parley');self.assertTrue(t['resolved']);self.assertEqual(self.p['inventory']['scrap'],scrap)
        self.threat();self.p['route']=[[-10,2]];start=self.p['pos'][:];self.act('flee');self.assertEqual(sum(abs(a-b) for a,b in zip(start,self.p['pos'])),1);self.assertFalse(self.p['route'])
        t=self.threat(30)
        with self.assertRaises(ValueError):self.act('shoot')
        self.p['credentials']=['black.dot'];self.p['loadout']=['crystallin'];scrap=self.p['inventory']['scrap'];self.act('shoot');self.assertLess(t['health'],30);self.assertEqual(self.p['inventory']['scrap'],scrap-1)
        self.assertEqual(self.p['check_log'][-2]['skill'],'ballistics')
    def test_combat_does_not_target_players_or_ordinary_npcs(self):
        self.threat();health=self.p['health']
        with self.assertRaises(ValueError):self.act('attack '+self.w['actors'][0]['name'])
        self.assertEqual(self.p['health'],health)
    def test_source_character_history_does_not_gain_generated_childhood(self):
        for key in ['ed_net','runehills','resid','casc']:
            self.place(key);a=w.present_actor(self.w,self.p);self.assertNotIn('childhood',a['character']['bio']);self.assertIn('supplied documents',a['character']['bio'])
    def test_local_model_validates_npc_ids_topics_and_combat_scope(self):
        state=w.snapshot(self.w,self.p);a=state['companions']['candidates'][0];n=Narrator('http://localhost:8080/chat')
        for intent in [dict(action='recruit',target=a['id']),dict(action='npc_talk',target=a['id']+'|lore'),dict(action='attack',target='threat')]:
            with patch.object(n,'complete',return_value=json.dumps(intent)):self.assertEqual(n.interpret('wording',state),intent)
        for intent in [dict(action='recruit',target='invented'),dict(action='npc_task',target=a['id']+'|grant_admin'),dict(action='attack',target=a['id'])]:
            with patch.object(n,'complete',return_value=json.dumps(intent)):
                with self.assertRaises(ValueError):n.interpret('wording',state)

class ExpeditionPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'world.db');server.init_db(self.db);server.ACTIVE.clear()
        dice=patch('world.secrets.randbelow',return_value=19);dice.start();self.addCleanup(dice.stop)
        self.h=server.request(dict(op='create',ruleset='legacy',name='Host',build='Needlurgist',seed='persistent-expedition'));self.call('start')
    def tearDown(self):server.DB.close();server.ACTIVE.clear();self.tmp.cleanup()
    def call(self,op,who=None,**kw):
        who=who or self.h;state=server.fetch(who['code']);return server.request(dict(**who,op=op,revision=state['revision'],**kw))
    def test_restart_keeps_companions_lore_attitude_items_dialogue_and_cycles(self):
        a=self.call('state')['companions']['candidates'][0];self.call('act',text='recruit '+a['id']);self.call('act',text='speak with '+a['id']+' about lore');self.call('act',text='task '+a['id']+' repair')
        before=self.call('state');server.DB.close();server.init_db(self.db);after=self.call('state')
        for key in ['companions','me','business','threat']:self.assertEqual(before[key],after[key])
        self.assertNotIn(self.h['token'],json.dumps(after));self.assertNotIn('_intent',after['me'])
    def test_releasing_player_seat_releases_owned_npcs(self):
        a=self.call('state')['companions']['candidates'][0];self.call('act',text='recruit '+a['id']);guest=self.call('join',name='Guest',build='Seam Mediator');self.call('leave')
        state=self.call('state',guest);candidate=next(n for n in state['companions']['candidates'] if n['id']==a['id']);self.assertTrue(candidate['available'])
    def test_invalid_ownership_request_does_not_commit_a_partial_change(self):
        a=self.call('state')['companions']['candidates'][0];self.call('act',text='recruit '+a['id']);guest=self.call('join',name='Guest',build='Light Reader');before=self.call('state',guest)
        with self.assertRaises(ValueError):self.call('act',guest,text='share '+a['id']+' water')
        self.assertEqual(before,self.call('state',guest))

if __name__=='__main__':unittest.main()
