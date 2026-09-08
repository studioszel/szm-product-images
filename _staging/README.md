# _staging - product photos awaiting a SLUG

These are real product photos fetched from studioszel.ro on 2026-09-07/08. They are staged here,
NOT in `images/`, because their final folder name is not yet decided.

## Why they are not in images/

The store convention is `images/<SLUG>/main.jpg`, where SLUG derives from the `Image_File` value
in `eva/knowledge-base/visual-catalogue.csv` (drop `.jpg`, uppercase, space and `+` become `-`).
All 373 codes staged here have a BLANK `Image_File`, so no SLUG exists for them yet.

The SLUG cannot be inferred from the product Code. Measured against the 517 catalogue rows that
do have an `Image_File`, a code-derived SLUG is right only 293 times (56.7 percent), because
`Image_File` is a deliberate many-to-one mapping: 118 SLUGs are shared by several codes so
visually identical variants reuse one photo (`PS1003-120.jpg` serves 7 codes; `PS2001` points at
`PS2001-TOP Z.jpg`). Publishing code-derived folder names would create roughly 400 wrongly named
public folders and break that sharing.

So the bytes are committed here to keep them safe and resumable, and `images/` and the GitHub
Pages URLs are left untouched and correct.

## Layout

- `photos-by-code/<CODE>/` - `main.jpg` plus up to 4 gallery images. Folder name is the catalogue
  Code with `/` and space replaced by `_`.
- `scrape-log.md` - per-code run log: Code, SLUG (PENDING), site SKU, source URL, result, files.
- `target-list.csv` - the 578 blank-`Image_File` catalogue rows with site reference, product URL
  and an `On_Site` yes/no column. This is the file to send Attila.
- `download-state.json` - machine-readable per-code result; `scripts/download.py` resumes from it.
- `scripts/` - target list, site map, gap report and downloader.

## To finish

1. Get `Image_File` filled in for the blank rows of `visual-catalogue.csv`. The decision per code
   is which photo it shows, and which codes share a photo.
2. Recompute each SLUG: drop `.jpg`, uppercase, replace space and `+` with `-`.
3. `git mv _staging/photos-by-code/<CODE> images/<SLUG>`. Where codes share one `Image_File`,
   only one folder survives; drop the duplicates.
4. Delete this `_staging/` folder in the same commit and merge to `main`.

## Not downloaded

- `PS714` and `OPS232BAS/SUP` matched a site reference but their product pages now return 404.
- 203 further catalogue codes have no matching reference on the site. Of those, 43 are genuinely
  absent products; the rest are top-material variants (`-TOP Z`, `-TOP OAK`, `GAL`) or standalone
  `SUP` upper units that the webshop does not sell separately and that most likely just need an
  `Image_File` pointing at the base product's photo. See `target-list.csv`.
