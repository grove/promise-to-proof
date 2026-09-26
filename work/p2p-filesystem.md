# Acceptance contract: work/p2p-filesystem.md

Contract revision: v1
Source: [Filesystem implementation specification](../plans/p2p-filesystem-implementation-spec.md)

Intended outcome: Plan, deliver, verify, and resume work from repository files,
with durable P2P records and exact candidate identities, without a required tracker.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Spec check 1 | Durable directories are trackable and only P2P temporary files are ignored. | Existing repository, local, or global ignore conflicts. | Helper setup and Git check-ignore. | Git effective rules. | Disposable repository checks. | planned |
| R2 | Spec check 2 | Work paths resolve predictably without overwriting unrelated work. | Invalid slugs, traversal, symlinks, collisions. | Helper create/resolve/save. | Spec naming rules. | Collision and path checks. | planned |
| R3 | Spec check 3 | Local work can be planned, implemented, reviewed, and proven without a tracker. | Standalone input, optional specification, individual skill installation. | Manual stages and bundled helpers. | Matching exact stage reports and CLI behavior. | Live local delivery plus packaging checks. | planned |
| R4 | Spec check 4 | Slicing creates linked local children and contribution mappings by default. | No remote publication or redundant specifications. | Slice skill and helper link discovery. | Parent and child outcomes and links. | Instruction review and parent/child fixture. | planned |
| R5 | Spec check 5 | Required evidence survives scratch cleanup. | OS temp paths and reruns before a commit. | Durable report saving and clone resume. | Evidence remains retrievable. | History, cleanup, and fresh-checkout checks. | planned |
| R6 | Spec check 6 | Secret-bearing evidence is excluded or redacted, and unsuitable evidence uses safe durable references. | No safe external storage available. | Stage evidence retention rules. | No secrets in retained fixtures; unavailable evidence remains a gap. | Instruction review and safe retained live evidence. | planned |
| R7 | Spec check 7 | Artifact-only commits preserve the original report-bound candidate. | Complete tree includes modes, symlinks, and deletions. | Helper capture/validate. | Exact Git tree or snapshot manifest. | Candidate A and artifact B regression. | planned |
| R8 | Spec check 8 | Changed product, work, binding source/parent, or base rejects stale reuse. | Staged/unstaged ambiguity and mutable stored refs. | Helper validate. | Exact bytes, modes, hashes, and full base SHA. | Stale-input regressions. | planned |
| R9 | Spec check 9 | A fresh checkout can discover durable state from the work-item path. | Retained snapshots and comparison-base objects must be available. | Helper resolve/resume and delivery instructions. | Full records and identities retrievable after transfer. | Fresh clone and live delivery bundle. | planned |
| R10 | Spec check 10 | Local record creation causes no implicit Git or external publication effects. | Existing separate user authority remains valid. | Helper commands and skill authority rules. | Index, HEAD, and remote state unchanged by helper operations. | Disposable Git state checks and instruction review. | planned |

## Scope

Implement the supplied filesystem spec, retaining the existing acceptance matrix
and snapshot format. Shared helpers use the Python standard library. No workflow
engine, database, synchronization service, or automatic commits/pushes.

## Change notes

Initial contract. The user authorized full implementation and a final repository
commit. No issue, PR, push, merge, or deployment was requested.
