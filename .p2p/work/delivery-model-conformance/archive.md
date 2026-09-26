# Archived supporting records

Recovery commit: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`

Top-level reports and the candidate record remain in this checkout.
The paths below are retained at the recovery commit. Archiving changes
storage only; it establishes no new review, proof, or completion verdict.

| Repository-relative path | Git object | Archived files | Bytes |
|---|---|---:|---:|
| `.p2p/work/delivery-model-conformance/evidence` | `228e6a163237394ca20e6ebb59ef9bdb7aee49ad` | 2849 | 92341717 |
| `.p2p/work/delivery-model-conformance/history` | `e348aaf4488843ee0b00efe1f6229a050651b6a0` | 11 | 1304409 |
| `.p2p/work/delivery-model-conformance/host` | `a537f174708b97a0ad6aa7b131a1baf137b35a35` | 68 | 15239041 |
| `.p2p/work/delivery-model-conformance/snapshots` | `0727e473bfb0c8c0f9ddb7159044300bdf071dfc` | 4 | 5571721 |

`evidence/issue-import.json` remains local because the current contract
references it directly. The evidence tree identity includes that file.

Recovery was tested by extracting this commit with `git archive` and
comparing every removed file byte-for-byte, including executable modes
and symlink targets, before removal. Untracked files were left untouched.

From the repository root, inspect the historical records in a new directory:

```sh
recovery_dir=$(mktemp -d)
git archive cc27a47f5ee765cff3cf13b21c36f974cb1234ae .p2p/work/delivery-model-conformance | tar -x -C "$recovery_dir"
```

The referenced commit must be available. Full clones retain this ancestor;
shallow clones and source exports may need the missing Git history.
Before verification or resume, recover the required paths. Preserve newer
local records when copying files back. Missing or unrecoverable evidence
blocks reuse. Existing reports remain bound to their original candidates.

Git history retains the original data; this cleanup reduces checkout size.
