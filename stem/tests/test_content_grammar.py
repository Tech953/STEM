import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import generation as g


class GrammarTests(unittest.TestCase):
    def setUp(self):
        self.cell=dict(x=2,y=3,title='A known service verge',region='WN_TOWER',
                       feature='repair frame',moisture=40,stability=50,shelter=0)
        self.w=dict(seed='content-test',tick=12,cells={'2,3':self.cell},players=[])
        self.p=dict(id='p',name='Visitor',pos=[2,3],inventory={'water':4},credentials=[],character={})
        self.a=dict(id='a',name='Resident',x=2,y=3,character={'voice':'quiet','mannerisms':'pauses before answering'})

    def test_seeded_identity_survives_ticks_and_state_changes(self):
        g.ensure_site(self.w,self.cell);identity=copy.deepcopy(self.cell['presentation'])
        self.cell.update(moisture=90,stability=10);self.w['tick']=400
        g.ensure_site(self.w,self.cell)
        self.assertEqual(identity,self.cell['presentation'])
        other=dict(self.cell,x=3);self.assertNotEqual(identity,g.site_identity('content-test',other))

    def test_renderer_reads_conditions_without_mutating_any_state(self):
        before=copy.deepcopy(self.w)
        dry=g.describe_site(self.w,dict(self.cell,moisture=10),'daylight','still air')
        wet=g.describe_site(self.w,dict(self.cell,moisture=80),'night','rain')
        self.assertIn('powder-dry',dry);self.assertIn('Moisture darkens',wet)
        self.assertIn('night',wet);self.assertEqual(before,self.w)

    def test_projection_cannot_receive_an_ordinary_material_recipe(self):
        projected=dict(self.cell,region='OMNI-META-INFI-PARTICULATE')
        self.assertEqual(g.describe_site(self.w,projected,'daylight','still air'),'')
        self.assertEqual(g.site_identity('content-test',projected)['status'],'unverified projection')

    def test_dialogue_is_replayable_but_varies_on_repeated_topic(self):
        body='The documented boundary remains closed.'
        first=g.dialogue(self.w,self.p,self.a,'access',body,False)
        second=g.dialogue(self.w,self.p,self.a,'access',body,False)
        self.assertNotEqual(first,second)
        saved=json.loads(json.dumps(dict(w=self.w,p=self.p,a=self.a)))
        expected=g.dialogue(self.w,self.p,self.a,'access',body,False)
        self.assertEqual(expected,g.dialogue(saved['w'],saved['p'],saved['a'],'access',body,False))
        self.assertIn(body,first);self.assertEqual(self.p['credentials'],[])
        self.assertEqual(self.p['inventory'],{'water':4})

    def test_recall_is_personal_and_does_not_read_a_remote_journal(self):
        elsewhere=dict(self.a,id='b',x=4)
        self.w['journal']=[dict(text='A secret reward was given elsewhere')]
        g.witness(self.w,self.p,{'action':'restore'},self.cell,[self.a,elsewhere],False)
        self.assertNotIn('witness_log',elsewhere)
        answer=g.dialogue(self.w,self.p,self.a,'history','Public record.',True)
        self.assertIn('habitat-repair attempt',answer);self.assertIn('setback',answer)
        self.assertNotIn('secret reward',answer)
        other=dict(self.p,id='other')
        self.assertNotIn('habitat-repair attempt',g.dialogue(self.w,other,self.a,'history','Public record.',True))

    def test_remote_observer_and_chat_cannot_create_a_witness_event(self):
        for fields,action in [({'remote':True},'restore'),({'percept':{'address':'void:test'}},'restore'),({},'chat')]:
            p=dict(self.p,**fields)
            g.witness(self.w,p,{'action':action},self.cell,[self.a],True)
        self.assertNotIn('witness_log',self.a)

    def test_histories_are_bounded_and_readiness_cannot_be_talked_away(self):
        self.a.update(health=20,energy=5,attitude=10)
        for i in range(120):
            g.dialogue(self.w,self.p,self.a,str(i),'Public record.',True)
            g.witness(self.w,self.p,{'action':'restore'},self.cell,[self.a],True)
        self.assertEqual(len(self.p['content_memory']['dialogue_counts']),64)
        self.assertEqual(len(self.a['witness_log']),12)
        text=g.dialogue(self.w,self.p,self.a,'plans','Public record.',True)
        self.assertIn('need care',text);self.assertEqual(self.a['health'],20)

    def test_narrator_allowlist_excludes_hidden_measurements(self):
        state=dict(location=dict(self.cell,physics='HIDDEN_MEASUREMENT'),character_sheet={},particles={'metrics':'HIDDEN_MEASUREMENT'})
        self.assertNotIn('HIDDEN_MEASUREMENT',json.dumps(g.narrator_context(state)))

if __name__=='__main__':unittest.main()
