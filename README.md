# Szelmob Product Image Catalogue

This repository is Szelmob's product image catalogue: product photos and product
metadata, organised by product code.

## Structure

One folder per product:

```
images/<CODE>/main.jpg          main product image
images/<CODE>/<variant-slug>.jpg   optional colour/finish variant image(s)
catalog.csv                     manifest of products and metadata
```

`<CODE>` is the product code in slug form (see below). Every product has a `main.jpg`;
colour and finish variants are added alongside it as additional images.

## Slug rule

The product code is derived from the image filename without its extension:

1. Uppercase the code.
2. Replace spaces, `+`, and any character outside `[A-Z0-9-]` with `-`.
3. Collapse repeated `-`.
4. Strip leading and trailing `-`.

Examples:

- `MPS003BAS+SUP` becomes `MPS003BAS-SUP`
- `PS1001-180-TOP OAK` becomes `PS1001-180-TOP-OAK`

## catalog.csv columns

The manifest holds product metadata only. Column names use dashes, not underscores.

| column | meaning |
| --- | --- |
| `code` | original product code (filename stem) |
| `slug` | product code in slug form (the folder name) |
| `variant` | `main` for the main image, or the variant slug for a variant image |
| `finish-description` | description of the finish |
| `body-colour` | main body colour |
| `accent-colours` | accent colour(s) |
| `top-material` | top material |
| `dimensions-cm` | dimensions in centimetres |
| `accessories` | included accessories |
| `source-file` | original source image filename |
| `path` | path to the image within this repository |

The metadata columns (`finish-description` through `accessories`) are blank on the seed rows
and are filled in over time as variants and metadata are added. Any future metadata column
names must also use dashes, not underscores.

## Adding a colour or finish variant

1. Add the optimized image at `images/<CODE>/<variant-slug>.jpg`.
2. Add a matching row to `catalog.csv` with:
   - `variant` set to the variant slug (matching the filename),
   - `path` set to `images/<CODE>/<variant-slug>.jpg`,
   - the colour, material, finish, dimensions and accessory columns filled in.

## Image requirements

- Images must be web-optimized: RGB JPEG, longest side at most 1000 px (never upscaled),
  quality 80, with EXIF metadata stripped.
- Git LFS must **not** be used. All images are committed directly as regular files.
