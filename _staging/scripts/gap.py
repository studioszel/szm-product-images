import csv, json, collections, os
from bs4 import BeautifulSoup
import re
OUT=os.path.dirname(os.path.abspath(__file__))
CACHE=r"C:\Users\BelaSuranyi\Projects\szm-product-images\_temp\_cache\studioszel_ro_3_produse_resultsPerPage_2000_eb7267114e31e3d1.html"
C=r"C:\Users\BelaSuranyi\Projects\szm-ia-agents\eva\knowledge-base\visual-catalogue.csv"
soup=BeautifulSoup(open(CACHE,encoding="utf-8",errors="replace").read(),"html.parser")
site={}
for r in soup.select("span.ce-product-meta__reference span.ce-product-meta__value"):
    val=r.get_text(strip=True); node=r; link=None
    for _ in range(14):
        node=node.parent
        if node is None: break
        a=node.find("a",href=re.compile(r"studioszel\.ro"))
        if a is not None: link=a.get("href"); break
    k=val.upper()
    if k.startswith("E-"): k=k[2:]
    site.setdefault(k,{"ref":val,"url":link})
def key(c): return c.strip().upper().replace("/","").replace(" ","").replace("+","")
sk={key(k):v for k,v in site.items()}
rows=list(csv.DictReader(open(C,newline="",encoding="utf-8-sig")))
empty=[r for r in rows if not (r.get("Image_File") or "").strip()]
matched=[]; unmatched=[]
for r in empty:
    e=sk.get(key(r["Code"]))
    (matched if e else unmatched).append((r,e))

lines=[]
A=lines.append
A("# Image backfill - gap report")
A("")
A("Run date 2026-09-07. Nothing was downloaded and nothing was committed: under the SLUG rule")
A("as specified there is no work to do, and the real gap needs a decision from Attila/Gabor.")
A("")
A("## What step 1 found")
A("")
A("| Measure | Count |")
A("| --- | --- |")
A("| Catalogue rows (visual-catalogue.csv) | 1095 |")
A("| Rows with a non-empty Image_File | 517 |")
A("| Distinct SLUGs those 517 rows require | 302 |")
A("| Of those SLUGs already present with a valid main.jpg | 302 |")
A("| **SLUGs missing under the stated rule** | **0** |")
A("| Rows with an EMPTY Image_File (the real gap) | 578 |")
A("")
A("All 302 existing folders were verified: every main.jpg is a valid JPEG, none are corrupt,")
A("no folder holds gallery images. Eight are low resolution and could be re-pulled if wanted:")
A("OPS742, PS287, PS641-TOP-OAK, PS734, PS738, PS742, PS789-180X200, PS806 (400x400 or smaller;")
A("PS806 is only 332x173).")
A("")
A("## Why the scrape cannot simply continue")
A("")
A("The 302 folders are not a half-finished scrape. They are the complete set that")
A("visual-catalogue.csv asks for. The 698 codes without a photo are the 578 rows whose")
A("Image_File cell is blank, and a blank cell yields no SLUG.")
A("")
A("The SLUG cannot be recovered from the Code. Tested against the 517 rows that do have an")
A("Image_File, a code-derived SLUG matches the real one in only 293 cases (56.7 percent).")
A("Image_File is a deliberate many-to-one editorial mapping: 118 SLUGs are shared by several")
A("codes, because visually identical variants are meant to reuse one photo. Examples:")
A("")
A("- PS1003-120.jpg serves 7 codes (PS1003-120, PS1003-140, the TOP OAK and TOP Z tops, the GAL variants)")
A("- PS16BAS-PS294SUP.jpg serves 5 codes, including PS16BAS on its own and PS16BAS/PS57SUP")
A("- PS2001 points at PS2001-TOP Z.jpg, not at a PS2001.jpg")
A("")
A("Deriving SLUGs from codes would create roughly 400 wrongly named folders and break the")
A("intended photo sharing. That is why the brief says not to invent a SLUG from the code.")
A("")
A("## What is available on the site (crawl already solved)")
A("")
A("The category crawl and pagination are done: studioszel.ro answers")
A("`/3-produse?resultsPerPage=2000` with the whole catalogue in one page, giving 919 distinct")
A("product references each with a product-page URL. Matching those against the 578 blank rows:")
A("")
A(f"- {len(matched)} codes have an exact reference match on studioszel.ro, so photos are obtainable today")
A(f"- {len(unmatched)} codes have no match on the site")
A("")
A("Reference convention confirmed: studioszel.ro prefixes the internal code with `E-`")
A("(`E-PS36` = PS36) and writes combinations with `+` where the catalogue uses `/`")
A("(`E-PS10BAS+SUP` = PS10BAS/SUP). Some references carry no prefix at all (`PS4003`, `PS24BAS`).")
A("")
A("## The decision needed")
A("")
A("Someone with catalogue authority has to supply the Image_File value for the 578 blank rows,")
A("i.e. decide which photo each code should show and which codes share a photo. Once those cells")
A("are filled in visual-catalogue.csv, the backfill is mechanical and I can run it end to end")
A(f"for the {len(matched)} codes that match the site immediately.")
A("")
A("I did not edit visual-catalogue.csv: it lives in szm-ia-agents, the runtime master, and the")
A("brief was read-only on it.")
A("")
A(f"## Codes with a blank Image_File that DO match studioszel.ro ({len(matched)})")
A("")
A("These are ready to download as soon as their Image_File / SLUG is assigned.")
A("")
A("| Code | Designation | Type | Site reference | Product page |")
A("| --- | --- | --- | --- | --- |")
for r,e in matched:
    A(f"| {r['Code']} | {r['Designation'][:44]} | {r['Type']} | {e['ref']} | {e['url'] or ''} |")
A("")
A(f"## Codes with a blank Image_File and NO match on studioszel.ro ({len(unmatched)})")
A("")
A("These need a photo from Attila, or confirmation that the product is retired.")
A("")
A("| Code | Designation | Type | Standard WxDxH cm |")
A("| --- | --- | --- | --- |")
for r,e in unmatched:
    A(f"| {r['Code']} | {r['Designation'][:44]} | {r['Type']} | {r['Standard_WxDxH_cm']} |")
open(os.path.join(OUT,"image-backfill-gap-report.md"),"w",encoding="utf-8").write("\n".join(lines))
print("matched:",len(matched)," unmatched:",len(unmatched))
print("report lines:",len(lines))
# also a csv for Attila
with open(os.path.join(OUT,"blank-image-file-rows.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["Code","Designation","Type","Standard_WxDxH_cm","Site_Reference","Product_URL","On_Site"])
    for r,e in matched+unmatched:
        w.writerow([r["Code"],r["Designation"],r["Type"],r["Standard_WxDxH_cm"],
                    e["ref"] if e else "", (e["url"] or "") if e else "", "yes" if e else "no"])
print("wrote blank-image-file-rows.csv")
