import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import adventure
import generation
import narrator
import world


class ContentIntegration(unittest.TestCase):
    def setUp(self):
        self.w=world.new_world('shared-content-integration', ruleset='legacy');self.w.update(code='CONTENT',started=True)
        self.p=world.add_player(self.w,'Visitor','Light Reader')
        self.c=world.local(self.w,self.p);self.a=adventure.resident(self.w,self.p)
        dice=patch('world.secrets.randbelow',return_value=19);dice.start();self.addCleanup(dice.stop)

    def act(self,text):
        intent,error=world.parse(text);self.assertIsNone(error)
        return world.act(self.w,self.p,intent,text)

    def test_npc_recalls_actual_work_without_inventing_source_biography(self):
        bio=self.a['character']['bio'];self.act('plant a seed')
        answer=self.act('ask about history')['text']
        self.assertIn('planting attempt',answer)
        self.assertEqual(self.a['character']['bio'],bio)

    def test_failed_conversation_preserves_facts_and_stocks(self):
        before=(copy.deepcopy(self.p['inventory']),self.p['credentials'][:],self.p['pos'][:])
        with patch('world.secrets.randbelow',return_value=0):answer=self.act('ask about access')['text']
        self.assertIn('no',answer.lower());self.assertIn('provisional',answer)
        self.assertEqual(before,(self.p['inventory'],self.p['credentials'],self.p['pos']))

    def test_legacy_migration_is_idempotent_and_preserves_world_work(self):
        self.c.pop('presentation');self.p.pop('content_memory')
        before=(self.p['inventory'].copy(),self.p['pos'][:],self.w['tick'])
        adventure.init(self.w);saved=copy.deepcopy(self.w);adventure.init(self.w)
        self.assertEqual(saved,self.w)
        self.assertEqual(before,(self.p['inventory'],self.p['pos'],self.w['tick']))

    def test_serialization_retains_exact_dialogue_sequence_and_site_identity(self):
        self.act('ask about place');saved=json.loads(json.dumps(self.w))
        intent,_=world.parse('ask about place')
        expected=world.act(self.w,self.p,intent)['text']
        actual=world.act(saved,saved['players'][0],intent)['text']
        self.assertEqual(expected,actual)
        self.assertEqual(self.c['presentation'],saved['cells'][world.key(*self.p['pos'])]['presentation'])

    def test_optional_prose_receives_shared_identity_and_no_particle_measurements(self):
        state=world.snapshot(self.w,self.p);state['particles']={'metrics':'HIDDEN_MEASUREMENT','photonics':{'temperature':'HIDDEN_MEASUREMENT'}}
        adapter=narrator.Narrator();seen={}
        adapter.complete=lambda system,payload:seen.update(payload=payload) or 'prose'
        self.assertEqual(adapter.describe(state),'prose')
        self.assertEqual(seen['payload']['content_context']['site'],self.c['presentation'])
        self.assertNotIn('HIDDEN_MEASUREMENT',json.dumps(seen))

if __name__=='__main__':unittest.main()
