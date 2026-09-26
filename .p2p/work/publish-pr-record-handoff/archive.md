# Archived supporting records

Recovery commit: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`

Top-level reports and the candidate record remain in this checkout.
The paths below are retained at the recovery commit. Archiving changes
storage only; it establishes no new review, proof, or completion verdict.

| Repository-relative path | Git object | Archived files | Bytes |
|---|---|---:|---:|
| `.p2p/work/publish-pr-record-handoff/evidence` | `80694e61d3beacc905ef2d19ace95ad29bdcdc1b` | 21 | 35531 |
| `.p2p/work/publish-pr-record-handoff/history` | `c4502e834d961e5ffaa3856ef42498784156abd0` | 4 | 2112609 |
| `.p2p/work/publish-pr-record-handoff/host` | `e33ecc925018f75568944810972a1b93913d0c35` | 2 | 1954 |
| `.p2p/work/publish-pr-record-handoff/snapshots` | `6b135101f365d3025718d9ccf8b70c69baa1d80a` | 2 | 2062642 |

Recovery was tested by extracting this commit with `git archive` and
comparing every removed file byte-for-byte, including executable modes
and symlink targets, before removal. Untracked files were left untouched.

From the repository root, inspect the historical records in a new directory:

```sh
recovery_dir=$(mktemp -d)
git archive cc27a47f5ee765cff3cf13b21c36f974cb1234ae .p2p/work/publish-pr-record-handoff | tar -x -C "$recovery_dir"
```

The referenced commit must be available. Full clones retain this ancestor;
shallow clones and source exports may need the missing Git history.
Before verification or resume, recover the required paths. Preserve newer
local records when copying files back. Missing or unrecoverable evidence
blocks reuse. Existing reports remain bound to their original candidates.

Git history retains the original data; this cleanup reduces checkout size.
