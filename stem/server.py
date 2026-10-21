#!/usr/bin/env python3
"""STEM server: shared room authority, persistence, timed ecological pulses."""
import argparse
import copy
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import urllib.error
import webbrowser
import world
import characters
import adventure
import companions
import field_rules
import field_adventure
from narrator import Narrator

ROOT=Path(__file__).resolve().parent
LOCK=threading.RLock()
DB=None
NARRATOR=Narrator()
ACTIVE={}
PULSE_SECONDS=30
STOP=threading.Event()

def init_db(path):
    global DB
    DB=sqlite3.connect(path,check_same_thread=False)
    DB.execute('CREATE TABLE IF NOT EXISTS worlds (code TEXT PRIMARY KEY, state TEXT NOT NULL)');DB.commit()
def save(w):
    DB.execute('INSERT OR REPLACE INTO worlds VALUES (?,?)',(w['code'],json.dumps(w)));DB.commit()
def fetch(code):
    row=DB.execute('SELECT state FROM worlds WHERE code=?',(code,)).fetchone()
    world.require(row is not None,'World not found. Check the room code and host address.')
    w=json.loads(row[0]);adventure.init(w);field_adventure.setup(w)
    for c in w['cells'].values():c.setdefault('fauna',3)
    companions.ensure_world(w)
    return w
def identify(w,token):
    world.require(isinstance(token,str),'Invalid session.')
    p=next((p for p in w['players'] if secrets.compare_digest(p['token'],token)),None)
    world.require(p is not None,'Session not recognized. Join this world or restore this browser’s session.')
    return p
def get_state(w,p):
    s=world.snapshot(w,p);s['narrator_enabled']=bool(NARRATOR.url);s['pulse_seconds']=PULSE_SECONDS
    return s

def request(d):
    op=d.get('op');code=str(d.get('code','')).upper().strip()
    if op=='create':
        world.require(DB.execute('SELECT COUNT(*) FROM worlds').fetchone()[0]<100,'Host limit reached: 100 saved worlds.')
        seed=d.get('seed','');world.require(isinstance(seed,str) and len(seed)<=80,'Use a seed of up to 80 characters.')
        w=world.new_world(seed or None,d.get('layout','atlas'),d.get('ruleset','field-guide-1'));p=world.add_player(w,d.get('name'),d.get('build'),d.get('character'))
        while True:
            code=''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            if not DB.execute('SELECT 1 FROM worlds WHERE code=?',(code,)).fetchone():break
        w['code']=code;save(w);ACTIVE[code]=dict(seen=time.monotonic(),next=time.monotonic()+PULSE_SECONDS)
        return dict(code=code,id=p['id'],token=p['token'])
    w=fetch(code)
    if op=='join':
        p=world.add_player(w,d.get('name'),d.get('build'),d.get('character'));w['revision']+=1;world.emit(w,p['name']+' joins the field station.','story');save(w)
        ACTIVE.setdefault(code,dict(seen=time.monotonic(),next=time.monotonic()+PULSE_SECONDS))['seen']=time.monotonic()
        return dict(code=code,id=p['id'],token=p['token'])
    p=identify(w,d.get('token'))
    ACTIVE.setdefault(code,dict(seen=time.monotonic(),next=time.monotonic()+PULSE_SECONDS))['seen']=time.monotonic()
    if op=='state':return get_state(w,p)
    if op=='export':
        return dict(title='Stem field journal',seed=w['seed'],tick=w['tick'],character={k:v for k,v in p.items() if k!='token'},journal=w['journal'],reputation=w['reputation'])
    if op=='narrate':return ('narrate',get_state(w,p))
    if op=='interpret':
        text=d.get('text');world.require(isinstance(text,str) and 0<len(text)<=1200,'Use 1–1,200 characters.');return ('interpret',dict(text=text,state=get_state(w,p)))
    world.require(type(d.get('revision'))==int and d['revision']==w['revision'],'The world changed. Review the new state and submit your action again; nothing was spent.')
    if op in ['start','pause']:
        world.require(p['id']==w['host'],'Only the host can change the world clock.')
        if op=='start':world.require(not w['started'],'Already started.');w['started']=True
        else:w['paused']=not w['paused']
        w['revision']+=1;ACTIVE[code]['next']=time.monotonic()+PULSE_SECONDS
        result=None
    elif op=='character':
        world.require(not w['started'],'Character editing locks when the expedition begins.')
        p['character']=characters.validate(d.get('character'),d.get('build',p['build']));p['build']=p['character']['role'];w['revision']+=1;result=None
    elif op in {'field_adopt','field_session','field_goal','field'}:
        if op=='field_adopt':
            world.require(p['id']==w['host'] and not field_rules.active(w),'Only the host can adopt the new rules once.')
            field_rules.enable(w);result=None
        elif op=='field_session':
            world.require(p['id']==w['host'] and field_rules.active(w),'Only the host can declare a new session.')
            world.require(not any(v.get('encounter',{}).get('combat') and not v['encounter']['combat']['finished'] for v in w['field_sites'].values()),'Finish active encounters first.')
            w['field_rules']['session']+=1;result=None
        elif op=='field_goal':
            world.require(p['id']==w['host'] and field_rules.active(w),'Only the host can record an agreed goal.')
            member=next((x for x in w['players'] if x['id']==d.get('target')),None);world.require(member,'Choose a party member.')
            field_rules.award(w,member,'goal:'+str(w['field_rules']['session']),1,goal=True);result=None
        else:
            name=d.get('action');target=d.get('target','')
            world.require(name in field_rules.ACTS and isinstance(target,str) and len(target)<=200,'Invalid field action.')
            world.require(w['started'] and not w['paused'],'Begin or resume the expedition first.')
            result=field_adventure.run(w,p,name,target,world)
        w['revision']+=1
    elif op=='act':
        raw=d.get('text','');world.require(isinstance(raw,str) and len(raw)<=1200,'Action text is too long.')
        intent=d.get('intent')
        if intent is not None:
            world.require(isinstance(intent,dict) and set(intent)=={'action','target'} and isinstance(intent['action'],str) and isinstance(intent['target'],str) and len(intent['target'])<=30,'Invalid proposed action.')
        else:
            intent,error=world.parse(raw)
            if error:return dict(state=get_state(w,p),result=dict(text=error,mechanics='',intent=None,time_spent=False))
        result=world.act(w,p,intent,raw)
    elif op=='chat':
        msg=d.get('text');world.require(isinstance(msg,str) and 0<len(msg.strip())<=500,'Chat uses 1–500 characters.');world.emit(w,p['name']+': '+msg.strip(),'chat');w['revision']+=1;result=None
    elif op=='leave':
        world.require(len(w['players'])>1,'The last player can disconnect; their saved world remains.')
        companions.release_all(w,p);w['players']=[a for a in w['players'] if a['id']!=p['id']]
        field_rules.release_seat(w,p['id'])
        if w['host']==p['id']:w['host']=w['players'][0]['id']
        w['revision']+=1;save(w);return dict(left=True)
    else:raise ValueError('Unknown operation.')
    save(w);return dict(state=get_state(w,p),result=result)

def pulse(now=None):
    now=time.monotonic() if now is None else now
    with LOCK:
        for code,activity in list(ACTIVE.items()):
            if now-activity['seen']>300:ACTIVE.pop(code,None);continue
            if now<activity['next']:continue
            activity['next']=now+PULSE_SECONDS
            w=fetch(code)
            if w['started'] and not w['paused'] and not any(v.get('encounter',{}).get('combat') and not v['encounter']['combat']['finished'] for v in w.get('field_sites',{}).values()):world.tick(w);save(w)
def run_clock():
    while not STOP.wait(1):pulse()

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,data,ctype='application/json; charset=utf-8'):
        body=data if isinstance(data,bytes) else json.dumps(data).encode()
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'");self.end_headers();self.wfile.write(body)
    def do_GET(self):
        files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8'),'/creator.js':('creator.js','text/javascript; charset=utf-8'),'/atlas.svg':('atlas.svg','image/svg+xml'),'/world-reference.jpg':('../reference/maps/world-reference-1.jpg','image/jpeg'),'/needle-reference.jpg':('../reference/maps/world-reference-2.jpg','image/jpeg')}
        if self.path=='/field-guide.js':return self.reply(200,(ROOT/'static/field-guide.js').read_bytes(),'text/javascript')
        if self.path=='/field-catalog':return self.reply(200,field_rules.CATALOG)
        if self.path=='/health':return self.reply(200,dict(ok=True,game='Stem',version=world.VERSION))
        if self.path=='/catalog':return self.reply(200,dict(builds=characters.ROLES,characters=characters.catalog(),help=world.HELP))
        if self.path not in files:return self.reply(404,dict(error='Not found'))
        name,mime=files[self.path];self.reply(200,(ROOT/'static'/name).read_bytes(),mime)
    def do_POST(self):
        try:
            world.require(self.path=='/api','Not found.')
            origin=self.headers.get('Origin')
            if origin:
                from urllib.parse import urlparse
                world.require(urlparse(origin).netloc==self.headers.get('Host'),'Cross-origin actions are not accepted.')
            world.require(self.headers.get('Content-Type','').split(';')[0]=='application/json','JSON required.')
            n=int(self.headers.get('Content-Length','0'));world.require(0<n<=65536,'Request must be at most 64 KiB.');self.connection.settimeout(10)
            d=json.loads(self.rfile.read(n));world.require(isinstance(d,dict),'JSON object required.')
            with LOCK:result=request(d)
            # Generation is intentionally outside the state lock; it has no write privileges.
            if isinstance(result,tuple):
                kind,payload=result
                result=dict(prose=NARRATOR.describe(payload),tick=payload['tick'],label='Optional model prose — not authoritative') if kind=='narrate' else dict(intent=NARRATOR.interpret(payload['text'],payload['state']))
            self.reply(200,result)
        except (ValueError,TypeError,KeyError,urllib.error.URLError,TimeoutError) as exc:self.reply(400,dict(error=str(exc)))
        except Exception:
            self.reply(500,dict(error='The server could not complete that operation. Your prior saved state is retained.'))
    def log_message(self,*args):pass

def main():
    global NARRATOR,PULSE_SECONDS
    parser=argparse.ArgumentParser(description='Stem text adventure host')
    parser.add_argument('--host',default='0.0.0.0');parser.add_argument('--port',type=int,default=8776);parser.add_argument('--db');parser.add_argument('--no-browser',action='store_true');parser.add_argument('--pulse-seconds',type=int,default=30);parser.add_argument('--narrator-url',default=os.getenv('STEM_NARRATOR_URL',''));parser.add_argument('--narrator-model',default=os.getenv('STEM_NARRATOR_MODEL','local'));args=parser.parse_args()
    if args.pulse_seconds<5:parser.error('World pulses must be at least 5 seconds apart.')
    PULSE_SECONDS=args.pulse_seconds;NARRATOR=Narrator(args.narrator_url,args.narrator_model)
    db=Path(args.db) if args.db else Path(os.getenv('LOCALAPPDATA',str(Path.home()/'.local'/'share')))/'Stem'/'worlds.sqlite3';db.parent.mkdir(parents=True,exist_ok=True);init_db(str(db))
    try:http=ThreadingHTTPServer((args.host,args.port),Handler)
    except OSError as exc:raise SystemExit(f'Cannot open port {args.port}: {exc}. Try --port 8777.')
    print(f'STEM {world.VERSION}\nOpen http://localhost:{args.port}\nWorlds: {db}\nKeep this window open. Ctrl+C stops the host.',flush=True)
    worker=threading.Thread(target=run_clock,daemon=True);worker.start()
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(f'http://localhost:{args.port}')).start()
    try:http.serve_forever()
    except KeyboardInterrupt:pass
    finally:STOP.set();worker.join(3);http.server_close();DB.close()
if __name__=='__main__':main()
