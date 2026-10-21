"""Shared behavior tests run independently against each game's real server."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import characters
import field_rules as f
import server
import world

STEM = hasattr(server, 'request')


class FieldGuideTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.init_db(str(Path(self.tmp.name)/'field.sqlite3'))
        d = dict(op='create', name='Field Witness', seed='guide-integration')
        d.update(dict(build='NanoClad Scout') if STEM else
                 dict(role='NanoClad Scout', mode='open', hardcore=True, procedural=False))
        self.h = self.request(d)
        self.call('start')

    def tearDown(self):
        server.DB.close()
        if STEM:server.ACTIVE.clear()
        self.tmp.cleanup()

    def request(self,d):
        return server.request(d) if STEM else server.mutate(d)

    def fetch(self):
        return server.fetch(self.h['code'])

    def player(self,w):
        return next(p for p in w['players'] if p['id']==self.h['id'])

    def call(self,op,who=None,**kwargs):
        h = who or self.h
        return self.request(dict(**h, op=op, revision=self.fetch()['revision'], **kwargs))

    def field(self,name,target='',who=None):
        return self.call('field',who,action=name,target=target)

    def state(self):
        return self.call('state')

    def public_guide(self):
        s=self.state()
        return s['field_guide'] if STEM else next(p for p in s['players'] if p['id']==self.h['id'])['field_guide']

    def local(self,w,p):
        if STEM:return world.local(w,p)
        import field_adventure
        return field_adventure.cell(w,p)

    def encounter(self,w,p,pid='FOE01',**values):
        a=copy.deepcopy(f.PROFILES[pid]);a.update(instance_id='test:'+pid,max_health=a['health'],
            hex=[3,0],state='present',disposition='wary',variant='typical',morale_tested=False,
            energy=100,injuries=[],ailments=[],initiative=0,present_need='a clear return route')
        a.update(values)
        e=dict(id='test:scene',watch=0,habitat='needle',budget=8,actors=[a],resolved=False,
               combat=None,declined=[],events=[],loot_paid=False,event='A controlled test encounter.')
        w['field_sites'].setdefault(f.site_key(p),{})['encounter']=e
        return e,a

    def test_new_campaign_live_panel_and_starting_pack(self):
        guide=self.public_guide();self.assertTrue(guide['enabled'])
        self.assertEqual(guide['bulk']['used'],8)
        p=self.player(self.fetch())
        self.assertEqual(f.pack(p),dict(food=4,water=5,scrap=3,seed=2,medkit=2))
        self.assertEqual(p['progression']['earned_xp'],0)

    def test_exact_twenty_face_grades_and_all_caps(self):
        self.assertEqual(f.odds(4,12),dict(complication=15,setback=20,success=25,strong=40,pass_percent=65))
        for bonus in range(-8,15):
            for dc in [6,8,10,11,12,13,14,16,18,24]:
                q=f.odds(bonus,dc)
                self.assertEqual(sum(q[k] for k in ['complication','setback','success','strong']),100)
                self.assertEqual(q['pass_percent'],5*max(1,min(19,21+bonus-dc)))
                self.assertEqual(f.grade(1,bonus,dc),'complication')
                self.assertEqual(f.grade(20,bonus,dc),'strong')

    def test_rng_sequence_replays_after_json_and_counter_continues(self):
        w=self.fetch();clone=json.loads(json.dumps(w))
        expected=[f.die(w,n,'case:'+str(i)) for i,n in enumerate([6,20,12,6]*50)]
        actual=[f.die(clone,n,'case:'+str(i)) for i,n in enumerate([6,20,12,6]*50)]
        self.assertEqual(actual,expected)
        resumed=json.loads(json.dumps(w))
        self.assertEqual(f.die(w,20,'next'),f.die(resumed,20,'next'))
        self.assertEqual(w['field_rules']['rng_counter'],201)

    def test_catalog_and_habitat_world_boundaries(self):
        self.assertEqual(len(f.CATALOG),48);self.assertEqual(len(f.PROFILES),48)
        self.assertEqual(sum(WEIGHT for WEIGHT in f.WEIGHTS),12)
        self.assertEqual(len(f.HABITATS),9)
        self.assertEqual(f.HABITATS['campus'].count('FOE22'),2)
        for region in ['WN_TOWER','CITY_CLOUD_S','ENACT_HILLS','AETHERGALE']:
            h=f.habitat(dict(region=region,title='ordinary route'))
            for identity in f.HABITATS[h]:
                self.assertEqual(f.PROFILES[identity]['world'],'Thorns / Stem / Rose')
        self.assertIsNone(f.habitat(dict(region='OMNI-META-INFI-PARTICULATE')))

    def test_seeded_encounters_fit_budget_and_cannot_reroll(self):
        original=self.fetch()
        for index in range(240):
            w=copy.deepcopy(original);w['seed']='case:'+str(index);p=self.player(w)
            n=index%6+1
            w['players']=[p]+[dict(copy.deepcopy(p),id='guest'+str(i)) for i in range(n-1)]
            region=['WN_TOWER','CITY_CLOUD_S','ENACT_HILLS','AETHERGALE'][index%4]
            c=dict(region=region,title='ordinary route',stability=20)
            w['field_rules']['cycle']=4
            e=f.generate(w,p,c);before=w['field_rules']['rng_counter']
            self.assertIs(e,f.generate(w,p,c));self.assertEqual(before,w['field_rules']['rng_counter'])
            self.assertLessEqual(sum(a['planning_cost'] for a in e['actors']),e['budget'])
            self.assertLessEqual(len(e['actors']),3)
            for a in e['actors']:
                self.assertEqual(a['world'],'Thorns / Stem / Rose')

    def test_observation_and_polling_do_not_advance_rng_or_xp(self):
        w=self.fetch();before=copy.deepcopy(w['field_rules'])
        for _ in range(8):self.state()
        self.assertEqual(before,self.fetch()['field_rules'])
        if STEM:
            for text in ['look','map','inventory','listen','inspect']:
                self.call('act',text=text)
            after=self.fetch()
            self.assertEqual(before,after['field_rules'])
            self.assertEqual(self.player(after)['xp'],0)

    def test_award_cap_goal_and_growth_preserve_earned_xp(self):
        w=self.fetch();p=self.player(w)
        for i in range(5):f.award(w,p,'resolved:'+str(i))
        self.assertEqual(p['xp'],3)
        self.assertEqual(f.award(w,p,'goal:1',goal=True),1)
        self.assertEqual(f.award(w,p,'second-goal:1',goal=True),0)
        f.grow(w,p,'skill:ballistics')
        self.assertEqual(p['xp'],4);self.assertEqual(p['progression']['spent_growth'],1)
        self.assertEqual(f.breakdown(w,p,'body','ballistics')['experience'],1)
        w['field_rules']['session']+=1
        self.assertEqual(f.award(w,p,'resolved:0'),0)
        self.assertEqual(f.award(w,p,'new-resolution',2),2)

    def test_contract_award_replaces_ordinary_award(self):
        w=self.fetch();p=self.player(w)
        self.assertEqual(f.award(w,p,'contract:C1',2),2)
        self.assertEqual(f.award(w,p,'contract:C1',2),0)
        self.assertEqual(f.award(w,p,'other-scene'),1)
        self.assertEqual(f.award(w,p,'beyond-cap'),0)

    def test_practice_standing_conditions_and_fatigue_are_bounded(self):
        w=self.fetch();p=self.player(w);p['character']['skills']['fieldcraft']=3
        p['credentials']=['black.dot'];p['loadout']=['filter_graft','rest_regulator']
        w['reputation']['test']=-20;p['personal_reputation']['test']=-20
        v=f.vitals(p);v.update(energy=24,injuries=['a','b','c'],ailments=['d','e'])
        b=f.breakdown(w,p,'body','fieldcraft',situation=50,faction='test')
        self.assertEqual(b['practice'],2);self.assertEqual(b['equipment'],1)
        self.assertEqual(b['context'],3);self.assertEqual(b['reputation'],-2)
        self.assertEqual(b['conditions'],5);self.assertEqual(b['fatigue'],-2)

    def test_eating_applies_personal_cycle_before_recovery(self):
        w=self.fetch();p=self.player(w);v=f.vitals(p);v.update(thirst=50,energy=98)
        server.save(w)
        with patch('field_rules.die',return_value=20):self.field('field_drink')
        w=self.fetch();p=self.player(w)
        self.assertEqual(f.vitals(p)['thirst'],9)
        self.assertEqual(f.vitals(p)['energy'],100)
        self.assertEqual(f.pack(p)['water'],4)
        self.assertEqual(w['field_rules']['cycle'],1)

    def test_full_rest_reserves_real_rations_and_four_cycles(self):
        w=self.fetch();p=self.player(w);v=f.vitals(p)
        v.update(health=40,energy=10,thirst=50,sleep=50)
        v['food_need' if STEM else 'hunger']=50;server.save(w)
        with patch('field_rules.die',return_value=6):self.field('field_rest')
        w=self.fetch();p=self.player(w);v=f.vitals(p)
        self.assertEqual(w['field_rules']['cycle'],4)
        self.assertEqual(v['energy'],100);self.assertEqual(v['health'],65)
        self.assertEqual(v['thirst'],21);self.assertEqual(v['sleep'],0)
        self.assertEqual(f.pack(p)['food'],3);self.assertEqual(f.pack(p)['water'],4)

    def test_medkit_spent_on_failure_no_condition_removed(self):
        w=self.fetch();p=self.player(w);f.vitals(p)['injuries']=['strained leg'];server.save(w)
        with patch('field_rules.die',return_value=1):self.field('field_treat')
        p=self.player(self.fetch());self.assertEqual(f.pack(p)['medkit'],1)
        self.assertEqual(f.vitals(p)['injuries'],['strained leg'])

    def test_ap_combat_has_no_counterattack_after_each_pc_action(self):
        w=self.fetch();p=self.player(w);e,a=self.encounter(w,p,health=100,max_health=100,morale=20)
        f.start_combat(w,p,e);self.assertEqual(e['combat']['round'],1)
        self.assertEqual(f.current(w,p),p['id']);hp=f.vitals(p)['health']
        f.handle(w,p,'field_approach',a['instance_id'],self.local(w,p))
        f.handle(w,p,'field_approach',a['instance_id'],self.local(w,p))
        with patch('field_rules.die',return_value=1):
            f.handle(w,p,'field_attack',a['instance_id'],self.local(w,p))
        self.assertEqual(f.vitals(p)['health'],hp);self.assertEqual(p['gear']['staff']['condition'],98)
        self.assertEqual(e['combat']['ap'][p['id']],5)
        with patch('field_rules.die',return_value=1):f.handle(w,p,'field_end','',self.local(w,p))
        self.assertLess(f.vitals(p)['health'],hp)

    def test_tactical_board_is_stable_axial_and_rng_independent(self):
        w=self.fetch();p=self.player(w);e,_=self.encounter(w,p)
        counter=w['field_rules']['rng_counter']
        board=f.tactical_board(w,p,e)
        self.assertEqual(w['field_rules']['rng_counter'],counter)
        self.assertEqual(board,f.tactical_board(w,p,e))
        self.assertEqual(board['topology'],'axial-hex')
        self.assertEqual(board['projection'],'isometric')
        self.assertEqual(board['terrain_effects'],'visual-only')
        self.assertEqual((board['radius'],len(board['cells'])),(5,91))
        f.start_combat(w,p,e)
        self.assertEqual(e['combat']['board'],board)

    def test_tactical_board_expands_without_changing_saved_terrain(self):
        w=self.fetch();p=self.player(w);e,_=self.encounter(w,p)
        f.start_combat(w,p,e)
        original={(c['q'],c['r']):c for c in e['combat']['board']['cells']}
        e['combat']['positions'][p['id']]=[0,7]
        board=f.ensure_tactical_board(w,p,e)
        expanded={(c['q'],c['r']):c for c in board['cells']}
        self.assertEqual((board['radius'],len(board['cells'])),(7,169))
        self.assertEqual({k:expanded[k] for k in original},original)

    def test_energy_attack_ignores_armor_and_preserves_health(self):
        w=self.fetch();p=self.player(w);p['field_armor']=5
        e,a=self.encounter(w,p,'FOE31',hex=[0,1]);f.start_combat(w,p,e)
        hp=f.vitals(p)['health'];energy=f.vitals(p)['energy']
        with patch('field_rules.die',return_value=1):f.handle(w,p,'field_end','',self.local(w,p))
        self.assertEqual(f.vitals(p)['health'],hp)
        self.assertEqual(f.vitals(p)['energy'],energy-a['damage'])
        self.assertEqual(a['ammo'],2)

    def test_stationary_out_of_range_and_finite_ammo(self):
        w=self.fetch();p=self.player(w);e,a=self.encounter(w,p,'FOE36',hex=[10,0],ammo=1)
        f.start_combat(w,p,e);hp=f.vitals(p)['health']
        with patch('field_rules.die',return_value=1):f.handle(w,p,'field_end','',self.local(w,p))
        self.assertEqual(a['hex'],[10,0]);self.assertEqual(a['ammo'],1);self.assertEqual(f.vitals(p)['health'],hp)
        a['hex']=[1,0]
        with patch('field_rules.die',return_value=1):
            f.handle(w,p,'field_end','',self.local(w,p));after=f.vitals(p)['health']
            f.handle(w,p,'field_end','',self.local(w,p))
        self.assertEqual(a['ammo'],0);self.assertEqual(f.vitals(p)['health'],after)

    def test_disabled_actor_salvage_pays_only_once_after_reload(self):
        w=self.fetch();p=self.player(w);e,a=self.encounter(w,p,health=0,state='disabled');e['resolved']=True
        server.save(w);before=f.pack(p)['scrap'];self.field('field_salvage')
        self.assertEqual(f.pack(self.player(self.fetch()))['scrap'],before+a['salvage_budget'])
        with self.assertRaises(ValueError):self.field('field_salvage')

    def test_truce_does_not_pay_salvage_or_grant_credentials(self):
        w=self.fetch();p=self.player(w);e,a=self.encounter(w,p);server.save(w)
        with patch('field_rules.die',return_value=20):self.field('field_parley',a['instance_id'])
        p=self.player(self.fetch());self.assertEqual(p['credentials'],[])
        with self.assertRaises(ValueError):self.field('field_salvage')

    def test_morale_runs_once_and_natural_twenty_withdraws(self):
        w=self.fetch();p=self.player(w);e,a=self.encounter(w,p,health=10,max_health=30)
        with patch('field_rules.die',return_value=20) as dice:
            f.morale(w,e,a);f.morale(w,e,a)
        self.assertEqual(dice.call_count,1);self.assertEqual(a['state'],'withdrawn')

    def test_material_wear_threshold_and_repair_spend_real_scrap(self):
        self.assertEqual(f.damage(10,60,False,2),8)
        self.assertEqual(f.damage(10,59,True,2),8)
        self.assertEqual(f.damage(10,29,False,2),3)
        w=self.fetch();p=self.player(w);p['gear']['staff']['condition']=59;server.save(w)
        with patch('field_rules.die',return_value=20):self.field('field_repair','staff')
        p=self.player(self.fetch());self.assertEqual(p['gear']['staff']['condition'],84)
        self.assertEqual(f.pack(p)['scrap'],2)

    def test_readiness_support_cost_and_personal_pack(self):
        w=self.fetch();p=self.player(w)
        a=copy.deepcopy(p);a.update(id='ready-ally',owner=p['id'],health=100,energy=100,
                                  attitude=55,pos=f.position(p)[:],x=f.position(p)[0],y=f.position(p)[1],
                                  engagement=dict(phase='observe',task='support'),inventory=dict(food=3,water=4,scrap=1,seed=1,medkit=1))
        a.pop('vitals',None);a['character']['skills']['fieldcraft']=1
        f.people(w).append(a);f.begin_action(p)
        with patch('field_rules.die',return_value=20):
            f.roll(w,p,'body','fieldcraft',10,'work',support=True)
            self.assertEqual(a['energy'],98)
            f.roll(w,p,'body','fieldcraft',10,'work2',support=True)
            self.assertEqual(p['last_check']['support'],0)
        f.companion_cycle(w,p,1);self.assertEqual(a['energy'],98)
        a['energy']=14;self.assertFalse(f.ready(w,p,a,'fieldcraft'))

    def test_recruitment_failure_never_transfers_offer_and_dismissal_is_free(self):
        w=self.fetch();p=self.player(w);a=next(a for a in f.people(w) if f.position(a)==f.position(p))
        before=copy.deepcopy(f.pack(p));npcpack=copy.deepcopy(f.pack(a))
        with patch('field_rules.die',return_value=1):
            f.handle(w,p,'field_recruit',a['id'],self.local(w,p))
        self.assertEqual(f.pack(p),before);self.assertEqual(f.pack(a),npcpack)
        a['owner']=p['id'];p['companions']=[a['id']]
        counter=w['field_rules']['rng_counter']
        out=f.handle(w,p,'field_dismiss',a['id'],self.local(w,p))
        self.assertIsNone(a['owner']);self.assertEqual(out['cycles'],0)
        self.assertEqual(w['field_rules']['rng_counter'],counter);self.assertEqual(f.pack(a),npcpack)

    def test_multiuser_inactive_vitals_and_host_authority(self):
        d=dict(name='Second Witness')
        d.update(dict(build='Light Reader') if STEM else dict(role='Light Reader'))
        if not STEM:
            w=self.fetch();w['started']=False;server.save(w)
        guest=self.call('join',**d)
        if not STEM:self.call('start')
        w=self.fetch();p=next(p for p in w['players'] if p['id']==guest['id']);before=copy.deepcopy(f.vitals(p))
        self.field('field_watch')
        after=next(p for p in self.fetch()['players'] if p['id']==guest['id'])
        self.assertEqual(f.vitals(after),before)
        with self.assertRaises(ValueError):self.call('field_session',who=guest)
        with self.assertRaises(ValueError):self.call('field_goal',who=guest,target=self.h['id'])

    def test_migration_retains_old_campaign_until_host_adopts(self):
        w=self.fetch();p=self.player(w);w.pop('field_rules');w.pop('field_sites')
        p['xp']=9;p.pop('progression');f.pack(p)['scrap']=17
        original=copy.deepcopy(p['character']);position=f.position(p)[:];server.save(w)
        self.assertFalse(self.public_guide()['enabled'])
        self.call('field_adopt');w=self.fetch();p=self.player(w)
        self.assertTrue(f.active(w));self.assertEqual(p['xp'],9)
        self.assertEqual(f.pack(p)['scrap'],17);self.assertEqual(p['character'],original)
        self.assertEqual(f.position(p),position)
        with self.assertRaises(ValueError):self.call('field_adopt')


    def test_later_legacy_xp_is_synchronized_when_adopting(self):
        w=self.fetch();w['field_rules']['enabled']=False;p=self.player(w)
        p['xp']=11;p['progression']['earned_xp']=0;server.save(w)
        self.call('field_adopt');p=self.player(self.fetch())
        self.assertEqual(p['progression']['earned_xp'],11)

    def test_mastery_softens_one_complication_without_creating_success(self):
        w=self.fetch();p=self.player(w);p['character']['skills']['fieldcraft']=3
        with patch('field_rules.die',return_value=1):f.roll(w,p,'body','fieldcraft',12,'test')
        self.assertFalse(p['last_check']['success'])
        f.handle(w,p,'field_mastery','',self.local(w,p))
        self.assertEqual(p['last_check']['grade'],'setback')
        self.assertFalse(p['last_check']['success']);self.assertTrue(p['check_log'][-1]['mastery'])
        with self.assertRaises(ValueError):f.handle(w,p,'field_mastery','',self.local(w,p))

    def test_native_contract_reserves_real_reward_and_pays_once(self):
        w=self.fetch();p=self.player(w);before=copy.deepcopy(f.pack(p))
        if STEM:
            source=self.local(w,p);initial=source['food'];server.save(w)
            with patch('field_rules.die',side_effect=lambda w,n,label:n):self.call('act',text='accept delivery contract')
            w=self.fetch();p=self.player(w);cm=p['contract']
            self.assertEqual(w['cells'][','.join(map(str,cm['issuer_pos']))]['food'],initial-2)
            p['pos']=cm['target'][:];world.visit(w,*p['pos']);server.save(w)
            with patch('field_rules.die',side_effect=lambda w,n,label:n):self.call('act',text='fulfill')
            with self.assertRaises(ValueError):self.call('act',text='fulfill')
            p=self.player(self.fetch());self.assertEqual(f.pack(p)['food'],before['food'])
        else:
            self.call('ow_contract');w=self.fetch();p=self.player(w);cm=p['contract']
            self.assertEqual(w['field_sites']['0,0']['stock']['food'],4)
            p['grid']=cm['target'][:];server.save(w)
            with patch('field_rules.die',side_effect=lambda w,n,label:n):self.call('ow_complete')
            with self.assertRaises(ValueError):self.call('ow_complete')
            p=self.player(self.fetch());self.assertEqual(f.pack(p)['food'],before['food']+2)
        self.assertEqual(p['xp'],2);self.assertIsNone(p['contract'])
        self.assertEqual(len(p['paid_contracts']),1)

    def test_same_native_resource_work_is_not_an_xp_farm(self):
        if not STEM:return
        with patch('field_rules.die',side_effect=lambda w,n,label:n):
            self.call('act',text='forage');self.call('act',text='forage')
        self.assertEqual(self.player(self.fetch())['xp'],1)

    def test_free_state_does_not_recover_incapacitation(self):
        w=self.fetch();p=self.player(w);f.vitals(p)['health']=0;server.save(w)
        for _ in range(3):self.state()
        self.assertEqual(f.vitals(self.player(self.fetch()))['health'],0)

    def test_party_companion_cap_applies_to_other_owners(self):
        w=self.fetch();p=self.player(w);a=copy.deepcopy(f.people(w)[0])
        for i in range(2):
            copy_a=copy.deepcopy(a);copy_a.update(id='other:'+str(i),owner='another-player')
            f.people(w).append(copy_a)
        candidate=next(x for x in f.people(w) if not x.get('owner') and f.position(x)==f.position(p))
        with self.assertRaises(ValueError):f.handle(w,p,'field_recruit',candidate['id'],self.local(w,p))


    def test_departing_active_seat_does_not_strand_combat(self):
        w=self.fetch();p=self.player(w);guest=copy.deepcopy(p)
        guest.update(id='leaving-seat',name='Departing explorer')
        w['players'].append(guest);e,a=self.encounter(w,p,health=50,max_health=50)
        f.start_combat(w,p,e)
        e['combat']['cursor']=e['combat']['order'].index(guest['id'])
        w['players'].remove(guest);f.release_seat(w,guest['id'])
        self.assertNotEqual(f.current(w,p),guest['id'])
        self.assertIn(guest['id'],e['combat']['escaped'])

    def test_darkwood_is_not_mistaken_for_the_ark(self):
        self.assertEqual(f.habitat(dict(region='WN_TOWER',title='route',feature='splintered darkwood trellis')),'needle')
        self.assertEqual(f.habitat(dict(region='WN_TOWER',title='wood',terrain='woodland')),'shellwood')


    def test_ruined_replacement_retires_id_and_spends_real_inputs(self):
        w=self.fetch();p=self.player(w);p['gear']['staff']['condition']=0
        old=p['gear']['staff']['id'];server.save(w)
        with patch('field_rules.die',side_effect=lambda w,n,label:n):self.field('field_replace','staff')
        p=self.player(self.fetch());self.assertEqual(p['gear']['staff']['condition'],100)
        self.assertNotEqual(p['gear']['staff']['id'],old)
        self.assertEqual(p['retired_gear'][0]['id'],old);self.assertEqual(f.pack(p)['scrap'],1)

    def test_legacy_reads_do_not_add_materials_to_old_packs(self):
        w=self.fetch();p=self.player(w);w['field_rules']['enabled']=False
        if not STEM:p['supplies']=dict(food=4,water=6,medkit=2)
        before=copy.deepcopy(f.pack(p));server.save(w)
        for _ in range(2):self.state()
        self.assertEqual(f.pack(self.player(self.fetch())),before)


if __name__=='__main__':
    unittest.main()
