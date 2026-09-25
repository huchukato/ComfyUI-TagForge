# Changelog

All notable changes to ComfyUI-TagForge will be documented in this file.

## [2.2.3] - 2026-09-25

- Removed the bogus `requires-comfyui >=1.0.0` constraint — ComfyUI versions are 0.x, and the mismatch was disabling the node pack in ComfyUI Manager.

## [2.2.2] - 2026-09-18

### Wildcard Library & Completer Fixes

- Added `qwen21/eyeswap` and `qwen21/hairswap` editing wildcards: eyes and hair transfer from `<image1>` onto `<image2>`, consistent with the face/head swap conventions.
- Reworked `qwen21/faceswap` so only facial features inside the hairline transfer from `<image1>` — the target's hairstyle, hairline, ears, head silhouette, body, clothing, and background stay unchanged, avoiding unwanted head swaps.
- Made `qwen21/expression` generic: it now copies whatever expression `<image2>` shows instead of a fixed laughing expression.
- Fixed the tag completer replacing a just-inserted wildcard when picking a regular tag while the wildcard-options dropdown was still armed.
- Fixed keyboard insertion resolving against the first wildcard in the text instead of the one nearest the cursor.
- Wildcard library converted from ~90 .txt files to 18 YAML files (all 142 `__pmp/...__` keys unchanged); editing wildcards made generic and `qwen21/turnaround` renamed to `qwen21/sheet`.
- Scanner hardening: in-memory tag DB now opened via `sqlite3.Connection` and JS `.bind()` calls replaced with arrow functions (registry false positives on `socket.connect`/`socket.bind` patterns).

## [2.2.1] - 2026-09-16

### None Base-Model Option

- Added a `None` option to the `base_model` dropdown: the positive prompt is returned without any quality-tag prefix and the negative output is empty.
- Switching to `None` also strips a previously applied Pony or Illustrious prefix from the text.
- `Pony` remains the default for new nodes, preserving existing workflow behavior.

## [2.2.0] - 2026-09-16

### Model-Aware Prompt Presets

- Added a `base_model` dropdown to `WildcardProcessor` with `Pony` and `Illustrious` options.
- Added automatic model-specific quality tags at the beginning of the processed positive prompt.
- Added a second `negative` output with the negative prompt selected for the active model family.
- Added Pony defaults for score tags and Pony-oriented negative quality tags.
- Added Illustrious defaults for quality tags, adult prompting, and Illustrious-oriented negative quality tags.
- Existing Pony or Illustrious prefixes are replaced instead of duplicated when switching model families.
- Preserved `processed_text` as the first output and appended the dropdown after existing widgets for workflow compatibility.
- Updated browser-side pre-queue wildcard processing and the wildcard API endpoint to honor the selected model family.
- Added regression coverage for prefix replacement, negative output selection, output ordering, and input availability.

---

## [2.0.0] - 2025-02-14

### 🎉 MAJOR FEATURE - Wildcard Sub-Selection
- **NEW**: a1111-sd-webui-tagcomplete style wildcard sub-selection
- **NEW**: Type `__` → select wildcard → press Enter → auto-show options
- **NEW**: Select option with arrow keys → press Enter → replace wildcard
- **NEW**: ESC to keep wildcard and close options
- **NEW**: Smart parsing for wildcards with complex paths (`__pmp/blwjob/blwjb__`)
- **NEW**: Line-by-line option parsing from wildcard files
- **NEW**: Text overflow handling with truncation and hover expansion
- **NEW**: CSS styling for long wildcard options (max-width: 600px)

### 🔧 Technical Improvements
- **FIXED**: Backend now uses `\n` separator instead of commas for wildcard options
- **FIXED**: Wildcard replacement works correctly with complex paths
- **FIXED**: Proper cursor position tracking for wildcard insertion
- **IMPROVED**: Multiple wildcard source support with priority ordering
- **IMPROVED**: Better error handling and fallback mechanisms

### 📁 Wildcard Sources (Priority Order)
1. Repository `wildcards/` folder (highest priority)
2. ComfyUI `models/wildcards/`
3. ComfyUI `custom_nodes/wildcards/`
4. DynamicPrompts `wildcards/`
5. Extra model paths configuration
6. Impact-Pack wildcards
7. Impact-Pack.ini custom paths

### 🐛 Bug Fixes
- Fixed wildcard options appearing on single line instead of multiple lines
- Fixed wildcard replacement leaving original wildcard text
- Fixed CSS styling not applying to wildcard options
- Fixed cursor position issues during wildcard insertion

### ⚠️ Breaking Changes
- None - fully backward compatible with existing wildcard files

---

## [1.0.0] - Previous Versions
- Basic tag completion functionality
- CSV tag file support
- Embedding and LoRA suggestions
- Basic wildcard support (no sub-selection)
