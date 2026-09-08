import csv, os, json, collections

CSV = r"C:\Users\BelaSuranyi\Projects\szm-ia-agents\eva\knowledge-base\visual-catalogue.csv"
REPO = r"C:\Users\BelaSuranyi\Projects\szm-product-images"
IMG = os.path.join(REPO, "images")
OUT = os.path.dirname(os.path.abspath(__file__))

def slugify(image_file):
    base = image_file.strip()
    if base.lower().endswith(".jpg"):
        base = base[:-4]
    return base.upper().replace(" ", "-").replace("+", "-")

rows = []
with open(CSV, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append(r)

total_rows = len(rows)
no_img = [r for r in rows if not (r.get("Image_File") or "").strip()]
with_img = [r for r in rows if (r.get("Image_File") or "").strip()]

# slug -> list of codes
slug_codes = collections.OrderedDict()
for r in with_img:
    s = slugify(r["Image_File"])
    slug_codes.setdefault(s, []).append(r["Code"].strip())

existing = set(d for d in os.listdir(IMG) if os.path.isdir(os.path.join(IMG, d)))
# which existing folders actually have main.jpg
existing_with_main = set(d for d in existing if os.path.isfile(os.path.join(IMG, d, "main.jpg")))

target_slugs = list(slug_codes.keys())
present = [s for s in target_slugs if s in existing_with_main]
missing = [s for s in target_slugs if s not in existing_with_main]
orphan = sorted(existing - set(target_slugs))

print("=" * 62)
print("STEP 1 — TARGET LIST")
print("=" * 62)
print(f"catalogue rows (data)          : {total_rows}")
print(f"  rows with Image_File         : {len(with_img)}")
print(f"  rows with EMPTY Image_File   : {len(no_img)}")
print(f"distinct catalogue Codes       : {len(set(r['Code'].strip() for r in rows))}")
print("-" * 62)
print(f"distinct SLUGs required        : {len(target_slugs)}")
print(f"  already present (main.jpg)   : {len(present)}")
print(f"  MISSING -> to download       : {len(missing)}")
print("-" * 62)
print(f"folders in images/             : {len(existing)}")
print(f"  of which have main.jpg       : {len(existing_with_main)}")
print(f"folders NOT in catalogue       : {len(orphan)}")
print("=" * 62)

# how many catalogue codes are covered / uncovered
codes_missing = sorted({c for s in missing for c in slug_codes[s]})
print(f"catalogue Codes awaiting an image: {len(codes_missing)}")
print()
print("Sample of 20 missing SLUGs (slug <- codes):")
for s in missing[:20]:
    print(f"  {s:<34} <- {', '.join(slug_codes[s][:3])}")

if orphan:
    print()
    print(f"Folders present but not referenced by the catalogue ({len(orphan)}):")
    for o in orphan[:15]:
        print("  " + o)

json.dump({"slug_codes": slug_codes, "missing": missing, "present": present,
           "orphan": orphan},
          open(os.path.join(OUT, "target.json"), "w", encoding="utf-8"), indent=1)
print()
print("saved target.json")
