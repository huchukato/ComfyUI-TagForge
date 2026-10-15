# Changelog

## 2.3.3 — 2026-10-15
- Dropped bundled `pmp/prmpt.yaml` and its fallback-list entry: `rndm_ponyxl` was unused and carried a broken wildcard reference. Deployed copies self-clean via the Garage boot-sync (stale-file removal).

## 2.3.2 — 2026-10-09
- Fix settings panel on new ComfyUI frontend

## 2.3.1 — 2026-10-09
- Mirror-sync Garage wildcards at every ComfyUI boot (adds, updates, deletes)
- Bundle mmh3 wildcard set

## 2.3.0 — 2026-10-07
- Slim quality presets, opt-in dynamic wildcards
