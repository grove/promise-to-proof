# Archived supporting records

Recovery commit: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`

Top-level reports and the candidate record remain in this checkout.
The paths below are retained at the recovery commit. Archiving changes
storage only; it establishes no new review, proof, or completion verdict.

| Repository-relative path | Git object | Archived files | Bytes |
|---|---|---:|---:|
| `.p2p/work/delivery-completion-integrity/evidence` | `842006e28eab55bf6b0305fd155e3a1f2d28127e` | 880 | 10912269 |
| `.p2p/work/delivery-completion-integrity/history` | `8da07d1d9e7493ee3feea5ead5aca3481a63f843` | 15 | 2231737 |
| `.p2p/work/delivery-completion-integrity/host` | `72ca7ac0a6834fe40cc70423879be77af23c9dfd` | 4 | 4963 |
| `.p2p/work/delivery-completion-integrity/publication.bundle` | `7cd82dc6c1a46d7f47de19b8cbe04eeb23dd4d06` | 1 | 1029363 |
| `.p2p/work/delivery-completion-integrity/snapshots` | `298c4a7c5ef58d07387a7c68bf353ee468dc444c` | 3 | 3083481 |

Recovery was tested by extracting this commit with `git archive` and
comparing every removed file byte-for-byte, including executable modes
and symlink targets, before removal. Untracked files were left untouched.

From the repository root, inspect the historical records in a new directory:

```sh
recovery_dir=$(mktemp -d)
git archive cc27a47f5ee765cff3cf13b21c36f974cb1234ae .p2p/work/delivery-completion-integrity | tar -x -C "$recovery_dir"
```

The referenced commit must be available. Full clones retain this ancestor;
shallow clones and source exports may need the missing Git history.
Before verification or resume, recover the required paths. Preserve newer
local records when copying files back. Missing or unrecoverable evidence
blocks reuse. Existing reports remain bound to their original candidates.

Git history retains the original data; this cleanup reduces checkout size.
