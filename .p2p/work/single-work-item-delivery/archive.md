# Archived supporting records

Recovery commit: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`

Top-level reports and the candidate record remain in this checkout.
The paths below are retained at the recovery commit. Archiving changes
storage only; it establishes no new review, proof, or completion verdict.

| Repository-relative path | Git object | Archived files | Bytes |
|---|---|---:|---:|
| `.p2p/work/single-work-item-delivery/evidence` | `741b5bf60e128133902a5960f1a8626507847eed` | 6 | 51271 |
| `.p2p/work/single-work-item-delivery/host` | `4b3a0fa6496f97de795acd79dc4ab0d4fe4b96e5` | 35 | 4745052 |
| `.p2p/work/single-work-item-delivery/publication-evidence.tar.gz` | `1637938194f26a54e56604406fad478531c5351b` | 1 | 2401856 |
| `.p2p/work/single-work-item-delivery/snapshots` | `89b24f37f41f73dbe9ef4bb44d90bfdb714ee1e8` | 1 | 1100143 |

Recovery was tested by extracting this commit with `git archive` and
comparing every removed file byte-for-byte, including executable modes
and symlink targets, before removal. Untracked files were left untouched.

From the repository root, inspect the historical records in a new directory:

```sh
recovery_dir=$(mktemp -d)
git archive cc27a47f5ee765cff3cf13b21c36f974cb1234ae .p2p/work/single-work-item-delivery | tar -x -C "$recovery_dir"
```

The referenced commit must be available. Full clones retain this ancestor;
shallow clones and source exports may need the missing Git history.
Before verification or resume, recover the required paths. Preserve newer
local records when copying files back. Missing or unrecoverable evidence
blocks reuse. Existing reports remain bound to their original candidates.

Git history retains the original data; this cleanup reduces checkout size.
