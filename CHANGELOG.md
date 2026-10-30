# Changelog

## 0.1.0-beta.2 — 2026-10-30

- Added Outline shape: Follow layout (default) or Rectangle, in the dialog and Data properties.
- Rectangle encloses expanded key footprints along X/Y without changing switch or relief cutters.
- Preview follows the selected outline; older documents retain their original layout-following mode.
- Verified staggered, rotated and separated layouts, rectangle volume, saved selection and older-object migration in FreeCAD 1.1.


## 0.1.0-beta.1 — 2026-10-30

First public early-beta release. Earlier v0.1/v0.2 macro labels and the internal v0.3.0 refactor label belong to development history; public release numbering starts here.

Author: eco-ergo.com

- Refactored v0.2 into parser, geometry, feature, preview and GUI modules.
- Preserved proven MX cutouts, retaining lip, relief construction and defaults.
- Centralized mechanical parameter definitions for the GUI and FreeCAD properties.
- Corrected persistent KLE rotation-cluster origins and consecutive modifiers.
- Added layout import, parameter editing, top-view preview and plate dimensions.
- Added planar seam refinement, geometry validation and transactional regeneration.
- Added source geometry guards and FreeCAD 1.1 runtime validation.
- Packaged a clean macro installation archive with a four-switch example.
- Clarified PCB assembly requirements and relief settings in the README and dialog.
- Added linked credit to [Keyboard Layout Editor](https://www.keyboard-layout-editor.com/#/) by Ian Prest and contributors.
- Documented AI-assisted development, DXF-to-FreeCAD motivation, physical test scope and possible future stabilizer support.
- Added demo.png to the README and release archive; made the absence of mounting holes explicit in the README and dialog.
