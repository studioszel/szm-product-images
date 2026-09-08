import csv, os, re, json, time, sys, struct
import requests
OUT=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(OUT,"blank-image-file-rows.csv")
STAGE=os.path.join(OUT,"staging")
LOG=os.path.join(OUT,"scrape-log.md")
STATE=os.path.join(OUT,"download-state.json")
os.makedirs(STAGE,exist_ok=True)
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
MAXG=4          # up to 4 gallery images beyond main
SIZE="thickbox_default"

def jpeg_dims(p):
    try:
        with open(p,'rb') as f:
            if f.read(2)!=b'\xff\xd8': return None
            while True:
                b=f.read(1)
                if not b: return None
                if b!=b'\xff': continue
                while b==b'\xff': b=f.read(1)
                m=b[0]
                if m in (0xd8,0xd9) or 0xd0<=m<=0xd7: continue
                ln=struct.unpack('>H',f.read(2))[0]
                if 0xc0<=m<=0xcf and m not in (0xc4,0xc8,0xcc):
                    d=f.read(5); h,w=struct.unpack('>HH',d[1:5]); return w,h
                f.seek(ln-2,1)
    except Exception: return None

state=json.load(open(STATE)) if os.path.isfile(STATE) else {}
rows=[r for r in csv.DictReader(open(SRC,newline="",encoding="utf-8-sig")) if r["On_Site"]=="yes"]
print(f"products to fetch: {len(rows)}", flush=True)

sess=requests.Session(); sess.headers.update(H)

def fetch_product(url):
    r=sess.get(url,timeout=40)
    if r.status_code!=200: return None,f"page HTTP {r.status_code}"
    t=r.text
    ld=re.search(r'"image"\s*:\s*"https://studioszel\.ro/(\d+)-[a-z_]+/([^"]+\.jpg)"',t)
    if not ld: return None,"no JSON-LD image"
    cid,cname=ld.group(1),ld.group(2)
    sku=re.search(r'"sku":\s*"([^"]*)"',t)
    pairs=set(re.findall(r'https://studioszel\.ro/(\d+)-[a-z_]+/([^"\'\s?]+\.jpg)',t))
    ids=sorted({i for i,n in pairs if n==cname},key=int)
    if cid in ids: ids.remove(cid)
    ordered=[cid]+ids
    return {"cover":cid,"name":cname,"sku":sku.group(1) if sku else "","ids":ordered},None

def dl(iid,name,dest):
    u=f"https://studioszel.ro/{iid}-{SIZE}/{name}"
    r=sess.get(u,timeout=40)
    if r.status_code!=200 or len(r.content)<3000: return False,f"HTTP {r.status_code} len {len(r.content)}"
    if not r.content.startswith(b'\xff\xd8'): return False,"not JPEG"
    open(dest,"wb").write(r.content)
    d=jpeg_dims(dest)
    if d is None: os.remove(dest); return False,"unreadable JPEG"
    return True,f"{len(r.content)//1024}K {d[0]}x{d[1]}"

done=0; failed=[]
for n,r in enumerate(rows,1):
    code=r["Code"]; url=r["Product_URL"]
    if state.get(code,{}).get("status")=="downloaded":
        done+=1; continue
    folder=os.path.join(STAGE,code.replace("/","_").replace(" ","_"))
    info,err=fetch_product(url)
    if err:
        failed.append((code,url,err)); state[code]={"status":"failed","reason":err,"url":url}
        print(f"[{n}/{len(rows)}] FAIL {code}: {err}", flush=True)
        json.dump(state,open(STATE,"w"),indent=1); time.sleep(0.4); continue
    os.makedirs(folder,exist_ok=True)
    got=[]
    ok,msg=dl(info["cover"],info["name"],os.path.join(folder,"main.jpg"))
    if not ok:
        failed.append((code,url,"main: "+msg)); state[code]={"status":"failed","reason":"main: "+msg,"url":url}
        print(f"[{n}/{len(rows)}] FAIL {code}: main {msg}", flush=True)
        json.dump(state,open(STATE,"w"),indent=1); time.sleep(0.4); continue
    got.append("main.jpg")
    for k,iid in enumerate(info["ids"][1:1+MAXG],1):
        ok2,_=dl(iid,info["name"],os.path.join(folder,f"{k}.jpg"))
        if ok2: got.append(f"{k}.jpg")
        time.sleep(0.15)
    state[code]={"status":"downloaded","url":url,"sku":info["sku"],
                 "files":got,"cover":info["cover"],"name":info["name"]}
    done+=1
    print(f"[{n}/{len(rows)}] OK {code} sku={info['sku']} files={len(got)} ({msg})", flush=True)
    if n%10==0: json.dump(state,open(STATE,"w"),indent=1)
    time.sleep(0.25)

json.dump(state,open(STATE,"w"),indent=1)
print(f"\nDONE downloaded={done} failed={len(failed)}", flush=True)
