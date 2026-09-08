import re, json, csv, collections, os
from bs4 import BeautifulSoup
CACHE=r"C:\Users\BelaSuranyi\Projects\szm-product-images\_temp\_cache\studioszel_ro_3_produse_resultsPerPage_2000_eb7267114e31e3d1.html"
OUT=os.path.dirname(os.path.abspath(__file__))
soup=BeautifulSoup(open(CACHE,encoding="utf-8",errors="replace").read(),"html.parser")

refs=soup.select("span.ce-product-meta__reference span.ce-product-meta__value")
print("reference values found:", len(refs))
vals=[r.get_text(strip=True) for r in refs]
print("sample:", vals[:10])

# Build product entries: walk each reference up to its enclosing product block, find link + img
entries=[]
for r in refs:
    val=r.get_text(strip=True)
    node=r; link=None; img=None
    for _ in range(14):
        node=node.parent
        if node is None: break
        a=node.find("a", href=re.compile(r"studioszel\.ro|^/"))
        im=node.find("img")
        if a is not None and link is None: link=a.get("href")
        if im is not None and img is None: img=im.get("src") or im.get("data-src")
        if link and img: break
    entries.append({"ref":val,"url":link,"img":img})

def norm(r):
    r=r.strip().upper()
    if r.startswith("E-"): r=r[2:]
    return r
seen=collections.OrderedDict()
for e in entries:
    k=norm(e["ref"])
    if k not in seen: seen[k]=e
print("distinct normalised site codes:", len(seen))
with_url=sum(1 for e in seen.values() if e["url"])
print("of those with a product URL:", with_url)

C=r"C:\Users\BelaSuranyi\Projects\szm-ia-agents\eva\knowledge-base\visual-catalogue.csv"
rows=list(csv.DictReader(open(C,newline="",encoding="utf-8-sig")))
empty=[r for r in rows if not (r.get("Image_File") or "").strip()]
def key(c): return c.strip().upper().replace("/","").replace(" ","").replace("+","")
sk={key(k):k for k in seen}
hit=[r for r in empty if key(r["Code"]) in sk]
print()
print(f"uncovered catalogue rows (no Image_File) : {len(empty)}")
print(f"  exact ref match on studioszel.ro       : {len(hit)}")
print(f"  NOT found on site                      : {len(empty)-len(hit)}")
print()
print("matched examples:")
for r in hit[:15]:
    e=seen[sk[key(r['Code'])]]
    print(f"  {r['Code']:<20} -> {e['ref']:<20} {str(e['url'])[:62]}")
json.dump({"site":{k:v for k,v in seen.items()}}, open(os.path.join(OUT,"sitemap_cache.json"),"w",encoding="utf-8"), indent=1)
print("\nsaved sitemap_cache.json")
