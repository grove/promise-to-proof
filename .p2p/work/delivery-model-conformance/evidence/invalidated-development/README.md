# Invalidated development runs

These records are debugging history, not conformance evidence.

- mbt-first failed compilation.
- mbt-second could not bind localhost in the sandbox.
- mbt-third and mbt-all used require-disabled model operations with MBT 0.2's global action proposals. The driver could return success after an unmatched model link. Some controller processes also used Python 3.9, which cannot import tomllib. All apparent successes in these runs are invalidated.
- mbt-strict rejected an adapter assertion that omitted RUNNING from valid read-only status output.
- mbt-strict2 failed exact enabled-action coverage because the model's 32-proposal cap overrode the runner's larger budget.

The final model uses explicit DISABLED no-op returns, a 256-proposal cap, and exact enabled-action counts. The final runner rejects adapter failures and unmatched model links, and requires Python 3.11 or newer end-to-end. Only controller-conformance and controller-replay contain final successful development evidence.
