# Krea 2 Turbo — Text-to-Image (Local)

**Added**: 2026-08-06
**Local endpoint**: `http://192.168.1.181:8100/workflows/krea2-turbo-t2i`
**Status**: Production-validated (The Regular rebuild 2026-06-27, roadtrip-nostalgia test)

## Endpoint contract (verified against live server 2026-08-06)

| Input | Type | Default | Range |
|-------|------|---------|-------|
| `prompt` | string | — | required |
| `width` | int | 1024 | 256–4096 |
| `height` | int | 1024 | 256–4096 |
| `seed` | int | random | pin for reproducibility |
| `steps` | int | 8 | 1–50 (distilled — keep 8) |
| `cfg` | float | 1 | 1–20 (distilled — keep 1) |

Fast 8-step distilled model at CFG 1. Don't raise steps/cfg; the distillation is
tuned for the defaults.

## Primary role: character turnarounds for reference sheets

Krea2 is the current best local model for **single-image character turnarounds**
feeding reference-conditioned video (`ltx2-3-ingredients`, `minimax-h3-r2v`).

**Rule (validated)**: generate each character's multi-view turnaround as **ONE
image** — front / three-quarter / profile side by side on a plain grey studio
background. Separate per-angle generations drift in identity even at the same
seed; a single image locks all views to the same face.

Prompt pattern:

> character turnaround reference of ONE {person description} ... the SAME {person}
> shown three times side by side in upper-body views: a front view, a
> three-quarter view, and a side profile view. plain seamless light grey studio
> background, consistent identical face across all views, character model sheet.

- Wide canvas (e.g. 1536×864) to fit the views.
- Characters on clean grey studio (no film grain); location panels keep their
  environmental/film look.
- Each character = one turnaround row/block in the composite reference sheet.

Origin: The Regular two-hander rebuild (2026-06-27) — mirrors the known-good
cyberpunk sheet's character block. Working scripts:
`projects/260226-the-regular/EXPERIMENTS/ic_lora_ingredients/gen_krea_grey.py`.

## Validated pipeline

Krea2 turnarounds → stitched reference sheet → `ltx2-3-ingredients` @ strength 1.4
(see `memory/ltx2_3_ingredients_endpoint.md` until that graduates). End-to-end
validated on 260627-roadtrip-nostalgia: 5 dialogue-free shots from ONE master
sheet, character + vehicle identity held across all shots.

With MiniMax H3, the stitching step may be unnecessary — turnarounds can go in
directly as separate `<Picture N>` references (to validate).
