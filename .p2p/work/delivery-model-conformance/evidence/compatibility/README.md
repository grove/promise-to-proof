# Disposable compatibility experiment

Result: FizzBee v0.5.3 model graphs are consumable by FizzBee MBT v0.2.0 with the TypeScript @fizzbee/mbt 0.1.2 package on this macOS arm64 host. Node 26.9.0, npm 11.19.1, Python 3.9.6, TypeScript 5.9.3. package-lock.json pins all npm dependencies by version and integrity.

The counter adapter invokes operation.py as a new Python subprocess on each action and logs parsed state. Seed 42 passes. Adding one to the observed Get return value fails at action 2, expected 2, actual 3. Replaying seed 42 yields the same failure.

The controller adapter invokes the real public p2p_delivery.py CLI, status work/tiny.md, against controller-fixture. The fixture has a Git base and an acceptance work item but no delivery invocation. The controller returns exit 1 and JSON status BLOCKED, blocker no delivery invocation exists. MBT accepts the real returned status. Replacing only the adapter observation with STATUS_WRONG fails at action 0, expected BLOCKED, actual STATUS_WRONG. Seed 42 reproduces that mismatch. Each run invokes the real status CLI three times.

This establishes transport and return-value validation only. It does not establish lifecycle conformance, post-action white-box state validation, concurrency safety, agent execution, or acceptance of issue 30. The controller fixture is intentionally an unstarted item.

## Reproduction

Run from .p2p/tmp/issue-30/compatibility in this repository. The two release directories must exist at the paths used in reproduce.py. The verified MBT release archive SHA-256 is ae9296700d3b22aa67510cb5d3fe9e4f2b2cc2ecaa688cf14168cb5721888102. SHA256SUMS.json records binaries, model graphs, sources, dependencies lock and logs. Tool pins also match checks/delivery-model/check.py.

```sh
npm ci --ignore-scripts --cache .npm-cache
python3 reproduce.py
```

reproduce.py starts and stops the server for each model, compiles adapters, runs good/bad/replay at seed 42, checks process exit statuses and runner verdicts, and records exact commands in commands.json. It requires localhost sockets. The initial sandbox denied port binding and network resolution. Scoped tool escalations enabled downloads and localhost sockets; no global environment changes or agent sandbox bypasses occurred.

Initial graph generation and scaffolding used:

```sh
python3 /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/mbt_gen.zip --lang typescript --gen-adapter --out-dir generated counter.fizz
python3 /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/mbt_gen.zip --lang typescript --gen-adapter --out-dir controller-generated controller.fizz
```

Original generated adapter templates are retained beside the implemented scratch adapters. The fizz mbt-scaffold wrapper calls python, which is absent here. Calling the identical pinned generator zip with installed python3 works. No new language toolchain was installed. npm installed only the local trial dependencies.

The controller fixture was created using the existing repo() fixture helper in checks/test_p2p_delivery.py, with Git init and one fixture commit inside scratch. To recreate in an empty scratch location, load that module with importlib.util and call repo(Path('controller-fixture').resolve()). No fixture transport or monkey patch is used by either runtime adapter.

## Evidence

- commands.json records return codes for both model checks, compilations and all six runner trials.
- controller-good-verified.log, controller-bad-verified.log, controller-replay-verified.log retain raw CLI observations and runner verdicts.
- counter-good-verified.log, counter-bad-verified.log, counter-replay-verified.log retain subprocess states and runner verdicts.
- graph/ and controller-graph/ retain complete tiny generated state graphs in scratch. Durable evidence may retain their hashes and regenerate them with reproduce.py.
- package-lock.json records exact npm package identities. SHA256SUMS.json records tool and artifact hashes.

Sources consulted: https://fizzbee.io/testing/tutorials/quick-start/ and node_modules/@fizzbee/mbt/README.md. Binary versions identify MBT commit 5548168990633d9fffc4b7d836466aaff03c9591, build time 2025-11-05T17:53:54Z.
