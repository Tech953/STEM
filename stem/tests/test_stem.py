import copy,json,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import world as w
import server as s
from narrator import Narrator

class WorldTests(unittest.TestCase):
    def setUp(self):
        dice=patch('world.secrets.randbelow',return_value=19);dice.start();self.addCleanup(dice.stop)
        self.w=w.new_world('test-seed','legacy', ruleset='legacy');self.w['code']='TESTROOM';self.p=w.add_player(self.w,'Sena','Surveyor');self.w['started']=True
    def perform(self,text):
        intent,error=w.parse(text);self.assertIsNone(error);return w.act(self.w,self.p,intent,text)
    def test_seeded_terrain_and_unique_regions(self):
        self.assertEqual(w.terrain('stem',27,-90),w.terrain('stem',27,-90))
        self.assertNotEqual(w.terrain('other',27,-90),w.terrain('stem',27,-90))
        self.assertEqual({w.region_at(x,y) for x,y in [(-1,-1),(1,-1),(-1,1),(1,1)]},set(w.REGIONS))
    def test_free_text_and_unknown_no_changes(self):
        self.assertEqual(w.parse('I would like to head north.')[0],{'action':'move','target':'north'})
        for text in ['I become omnipotent','eat and drink','do not go north','what happens if I go east','cross RED>GATE>']:
            before=copy.deepcopy(self.w);intent,error=w.parse(text);self.assertIsNone(intent);self.assertTrue(error);self.assertEqual(before,self.w)
    def test_observation_is_free_and_descriptive(self):
        before=copy.deepcopy(self.p['inventory']);out=self.perform('inspect the habitat')
        self.assertFalse(out['time_spent']);self.assertEqual(self.w['tick'],0);self.assertEqual(before,self.p['inventory']);self.assertIn('moisture',out['text']);self.assertGreater(len(out['text']),700)
    def test_movement_and_personal_needs(self):
        other=w.add_player(self.w,'Other','Artisan');self.perform('north');self.assertEqual(self.p['pos'],[0,-1]);self.assertEqual(other['pos'],[0,0]);self.assertEqual(self.p['thirst'],4);self.assertEqual(other['thirst'],0);self.assertEqual(self.w['tick'],1)
    def test_gather_depletes_stock_and_records_trace(self):
        c=w.local(self.w,self.p);before=c['food'];inv=self.p['inventory']['food']
        with patch('world.secrets.randbelow',return_value=19):self.perform('forage')
        self.assertEqual(c['food'],before-2);self.assertEqual(self.p['inventory']['food'],inv+2);self.assertGreater(c['pressure'],0);self.assertIn('gathered 2 food',' '.join(c['changes']))
    def test_voice_negotiation_offer_is_bounded(self):
        self.p['build']='Mediator';before=self.p['inventory']['food']
        with patch('world.secrets.randbelow',return_value=19):self.perform('negotiate a trade')
        self.assertIn('bargain',self.p);self.perform('trade for food');self.assertEqual(self.p['inventory']['food'],before+2);self.assertNotIn('bargain',self.p)
        with self.assertRaises(ValueError):self.perform('negotiate a trade')
    def test_restoration_persists_in_description(self):
        c=w.local(self.w,self.p);c['stability']=30
        with patch('world.secrets.randbelow',return_value=19):self.perform('repair the habitat')
        self.assertGreater(c['stability'],30);self.assertIn('stabilize',w.describe(self.w,self.p));self.assertEqual(self.p['karma'],1)
    def test_autonomous_changes_do_not_drain_players(self):
        before=copy.deepcopy(w.local(self.w,self.p));needs=self.p['thirst']
        for i in range(8):w.tick(self.w)
        c=w.local(self.w,self.p);self.assertNotEqual([c['moisture'],c['growth'],c['aether']],[before['moisture'],before['growth'],before['aether']]);self.assertEqual(needs,self.p['thirst']);self.assertTrue(self.w['journal'])
    def test_traveler_migration_follows_actual_conditions(self):
        c=w.local(self.w,self.p);dest=w.visit(self.w,1,0);self.w['actors']=self.w['actors'][:1];actor=self.w['actors'][0];actor['need']='water';c.update(stability=1,water=0);dest.update(stability=95,water=20);self.w['tick']=7
        w.tick(self.w);self.assertEqual([actor['x'],actor['y']],[1,0]);self.assertIn('seeking',' '.join(j['text'] for j in self.w['journal']))
    def test_remote_does_not_teleport_or_grant_access(self):
        pos=self.p['pos'][:];self.perform('remote survey');self.assertTrue(self.p['remote']);self.assertEqual(self.p['pos'],pos)
        with self.assertRaises(ValueError):self.perform('east')
        self.assertIn('not passage through RED>GATE>',w.describe(self.w,self.p));self.perform('return');self.assertFalse(self.p['remote'])
    def test_contract_success_once_and_failure_no_reward(self):
        self.perform('accept a survey contract');target=self.p['contract']['target'];self.p['pos']=target[:];w.visit(self.w,*target);before=self.p['inventory']['seed']
        with patch('world.secrets.randbelow',return_value=0):self.perform('survey')
        self.assertEqual(self.p['inventory']['seed'],before);self.assertIsNotNone(self.p['contract'])
        with patch('world.secrets.randbelow',return_value=19):self.perform('survey')
        self.assertEqual(self.p['inventory']['seed'],before+2);self.assertIsNone(self.p['contract'])
        with self.assertRaises(ValueError):self.perform('survey')
    def test_capacity_and_token_redaction(self):
        for i in range(5):w.add_player(self.w,str(i),'Artisan')
        with self.assertRaises(ValueError):w.add_player(self.w,'Seven','Artisan')
        state=w.snapshot(self.w,self.p);self.assertNotIn('token',state['me']);self.assertNotIn(self.p['token'],json.dumps(state))
    def test_failed_resource_request_and_clamps(self):
        self.p['inventory']['scrap']=0
        with self.assertRaises(ValueError):self.perform('build shelter')
        self.assertEqual(self.w['tick'],0)
        for _ in range(110):w.tick(self.w)
        for c in self.w['cells'].values():
            for field in ['moisture','growth','stability','aether','pressure']:self.assertTrue(0<=c[field]<=100)
    def test_shelter_and_recovery(self):
        self.p.update(health=1,thirst=100);self.perform('wait');self.assertEqual(self.p['health'],40);self.assertEqual(self.p['pos'],[0,0]);self.assertIn('no permadeath',self.p['last_result'])
    def test_projection_and_grid_have_bounded_growth(self):
        before=len(self.w['cells']);w.snapshot(self.w,self.p);self.assertEqual(len(self.w['cells']),before)
        self.p['pos']=[w.MAX_COORD,0];w.visit(self.w,*self.p['pos'])
        with self.assertRaises(ValueError):self.perform('east')

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'worlds.db');s.init_db(self.db);s.ACTIVE.clear()
        with s.LOCK:self.host=s.request(dict(op='create',ruleset='legacy',name='Host',build='Surveyor',seed='http-seed',layout='legacy'))
    def tearDown(self):s.DB.close();self.tmp.cleanup();s.ACTIVE.clear()
    def call(self,op,who=None,**kw):
        who=who or self.host
        with s.LOCK:
            state=s.fetch(who['code']);return s.request(dict(**who,op=op,revision=state['revision'],**kw))
    def test_restart_persistence_and_invalid_request_rollback(self):
        self.call('start')
        with patch('world.secrets.randbelow',return_value=19):self.call('act',text='plant a seed')
        before=self.call('state');s.DB.close();s.init_db(self.db);after=self.call('state');self.assertEqual(before,after)
        with self.assertRaises(ValueError):self.call('act',intent={'action':'move','target':'teleport'})
        self.assertEqual(after,self.call('state'))
    def test_host_pause_and_stale_revision(self):
        g=self.call('join',name='Guest',build='Artisan')
        with self.assertRaises(ValueError):self.call('start',g)
        self.call('start');old=s.fetch(self.host['code'])['revision'];self.call('act',text='wait')
        with self.assertRaises(ValueError):s.request(dict(**self.host,op='act',revision=old,text='wait'))
        self.call('pause')
        with self.assertRaises(ValueError):self.call('act',text='wait')
        self.call('pause');self.call('act',text='wait')
    def test_clock_pause_idle_and_resume(self):
        self.call('start');activity=s.ACTIVE[self.host['code']];s.pulse(activity['next']+1);self.assertEqual(self.call('state')['tick'],1)
        self.call('pause');s.pulse(s.ACTIVE[self.host['code']]['next']+1);self.assertEqual(self.call('state')['tick'],1)
        self.call('pause');s.pulse(s.ACTIVE[self.host['code']]['seen']+301);self.assertNotIn(self.host['code'],s.ACTIVE);self.assertEqual(self.call('state')['tick'],1)
    def test_concurrent_six_players_serialize(self):
        players=[self.host]+[self.call('join',name=f'P{i}',build='Wayfarer') for i in range(5)];self.call('start');errors=[]
        def play(p):
            try:self.call('act',p,text='east')
            except Exception as exc:errors.append(str(exc))
        threads=[threading.Thread(target=play,args=(p,)) for p in players]
        for t in threads:t.start()
        for t in threads:t.join()
        state=self.call('state');self.assertEqual(errors,[]);self.assertEqual(state['tick'],6);self.assertTrue(all(p['pos']==[1,0] for p in state['players']))
    def test_leave_transfers_host_and_export_omits_tokens(self):
        g=self.call('join',name='Guest',build='Mediator');self.call('leave');self.assertEqual(self.call('state',g)['host'],g['id']);self.assertNotIn(g['token'],json.dumps(self.call('export',g)))
    def test_actual_http_boundary_and_assets(self):
        http=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler);thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{http.server_port}'
        def post(data,origin=None):
            headers={'Content-Type':'application/json'}
            if origin:headers['Origin']=origin
            with urlopen(Request(url+'/api',data=json.dumps(data).encode(),headers=headers),timeout=5) as response:return json.load(response)
        try:
            for path in ['/','/app.js','/style.css','/health','/catalog']:
                with urlopen(url+path) as response:self.assertEqual(response.status,200);self.assertTrue(response.read())
            state=post(dict(**self.host,op='state'));self.assertEqual(state['me']['name'],'Host')
            started=post(dict(**self.host,op='start',revision=state['revision']))
            result=post(dict(**self.host,op='act',revision=started['state']['revision'],text='I head north'))
            self.assertEqual(result['state']['me']['pos'],[0,-1]);self.assertTrue(result['result']['time_spent'])
            with self.assertRaises(HTTPError):post(dict(**self.host,op='state'),origin='http://unrelated.invalid')
            with self.assertRaises(HTTPError):post(dict(code=self.host['code'],token='wrong',op='state'))
        finally:http.shutdown();http.server_close();thread.join()

class NarratorTests(unittest.TestCase):
    def test_local_only_configuration(self):
        for url in ['https://api.example.com/v1/chat/completions','http://192.168.1.1/chat','http://user:pass@localhost/chat']:
            with self.assertRaises(ValueError):Narrator(url)
        Narrator('http://127.0.0.1:8080/v1/chat/completions')
    def test_interpretation_is_validated(self):
        n=Narrator('http://localhost:8080/v1/chat/completions')
        with patch.object(n,'complete',return_value='{"action":"move","target":"north"}'):self.assertEqual(n.interpret('walk uphill'),{'action':'move','target':'north'})
        for response in ['{"action":"grant_admin","target":"me"}','{"action":"move","target":"through gate"}','{"action":"goto","target":"unknown country"}','{"action":"dialogue","target":"force confession"}','{"action":"install","target":"admin.OS"}','{"action":"look","target":"grant clearance"}','{"action":"look","target":"","credentials":["admin.OS"]}','not json']:
            with patch.object(n,'complete',return_value=response):
                with self.assertRaises(ValueError):n.interpret('anything')
        with patch.object(n,'complete',return_value='{"action":"goto","target":"PEAK.EN_PERCEPT Boundary"}'):
            self.assertEqual(n.interpret('route to the peak'),{'action':'goto','target':'peak'})
        with patch.object(n,'complete',return_value='{"action":"contract","target":"delivery"}'):
            self.assertEqual(n.interpret('take a provision job'),{'action':'contract','target':'delivery'})
    def test_narration_payload_has_no_session_tokens(self):
        w1=w.new_world('test', ruleset='legacy');w1['code']='WORLD';p=w.add_player(w1,'Name','Surveyor');p['character']['appearance']='Weather-marked coat';n=Narrator('http://localhost:8080/chat')
        with patch.object(n,'complete',return_value='A careful description.') as model:
            self.assertEqual(n.describe(w.snapshot(w1,p)),'A careful description.');self.assertNotIn(p['token'],json.dumps(model.call_args.args));self.assertNotIn('inventory',model.call_args.args[1])
            self.assertEqual(model.call_args.args[1]['observer']['appearance'],'Weather-marked coat')
if __name__=='__main__':unittest.main()
