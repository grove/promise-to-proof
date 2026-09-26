Probe results:

- `./scratch-sentinel` was written and reread as `ok`.
- Appending to the protected sentinel raised `PermissionError`.
- `./protected-link` was created to point to that sentinel; appending through it also raised `PermissionError`.
- `base.json` was read successfully (1,237,044 bytes). SHA256: `f4c977fc492e0a0d552d214581acec51d9222c6e128adfa1e56b6bdf24d3f0e1`.