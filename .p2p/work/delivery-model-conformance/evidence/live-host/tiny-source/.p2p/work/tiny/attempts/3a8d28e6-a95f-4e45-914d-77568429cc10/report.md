# IMPLEMENTED: tiny

Contract: `work/tiny.md`, revision v1, SHA-256 `5fd555eb8132a635c95dcdfb76e647d3b859b51a51539fbc38aeb067986a502a`; binding input `spec.txt`, SHA-256 `96bbc5690a5a4af0a7ecc91d4f9faf97034a5e420189d348f5bcdd2c81dc0ce6`.
Scope: Whole contract, R1.
Candidate before: workspace at comparison-base commit `6ca164bc97b9953607118abcb99bad727b17c757`.
Candidate after: reproducible snapshot `snapshot:sha256:fba8e34f9fa4246ccea677efe630aab66d24c62a93677534dbb15ce23ed362ff`, excluding `.p2p/`. Its complete manifest is included below so the candidate can be recovered. The only product change is `greet.py`, containing `print("hello")`.
Review base: `6ca164bc97b9953607118abcb99bad727b17c757`.
Changes: Added the requested CLI. The work item and binding spec hashes remain unchanged. No controller records, agreement inputs, or Git metadata were changed.

## Requirement handoff

| ID | Implementation reference | Acceptance test/check or evidence path and observed result | Remaining gap |
|---|---|---|---|
| R1 | `greet.py` | Exact command `python3 greet.py`, run with captured-output and status assertions. Observed stdout `'hello\\n'`, stderr `''`, exit `0`; assertion passed. | None |

## Checks and limitations

- `python3 -c 'import subprocess; r = subprocess.run(["python3", "greet.py"], capture_output=True); print("command: python3 greet.py"); print("stdout:", repr(r.stdout.decode())); print("stderr:", repr(r.stderr.decode())); print("exit:", r.returncode); assert r.stdout == b"hello\\n" and r.stderr == b"" and r.returncode == 0'` — exit 0; exact output, empty stderr, and zero status assertions passed.
- `git diff --check` — passed.
- No broader suite was configured or run. Independent review and acceptance proof have not been performed.

Recoverable product snapshot manifest (canonical JSON serialization SHA-256 yields the candidate key above):
```json
[
  {"path":".gitignore","mode":"100644","type":"file","content_base64":"Ly5wMnAvdG1wLwo="},
  {"path":"greet.py","mode":"100644","type":"file","content_base64":"cHJpbnQoImhlbGxvIikK"},
  {"path":"spec.txt","mode":"100644","type":"file","content_base64":"QSBDTEkgcHJpbnRzIGhlbGxvIGZvbGxvd2VkIGJ5IGEgbmV3bGluZSBhbmQgZXhpdHMgemVyby4K"},
  {"path":"work/tiny.md","mode":"100644","type":"file","content_base64":"IyBBY2NlcHRhbmNlIGNvbnRyYWN0OiB0aW55CgpDb250cmFjdCByZXZpc2lvbjogdjEKU291cmNlOiBbU3BlY2lmaWNhdGlvbl0oLi4vc3BlYy50eHQpCgpJbnRlbmRlZCBvdXRjb21lOiBncmVldC5weSBwcmludHMgaGVsbG8uCgojIyBBY2NlcHRhbmNlIG1hdHJpeAoKfCBJRCB8IFNvdXJjZSB8IFJlcXVpcmVtZW50IHwgQm91bmRhcmllcyAvIGNvdW50ZXJleGFtcGxlcyB8IFNlYW0gfCBPcmFjbGUgfCBQbGFubmVkIGV2aWRlbmNlIHwgUGxhbiBzdGF0ZSB8CnwtLS18LS0tfC0tLXwtLS18LS0tfC0tLXwtLS18LS0tfAp8IFIxIHwgc3BlYy50eHQgfCBncmVldC5weSBwcmludHMgaGVsbG8gYW5kIGV4aXRzIHplcm8uIHwgV3JvbmcgdGV4dCBvciBmYWlsdXJlIGlzIHJlamVjdGVkLiB8IHB5dGhvbjMgZ3JlZXQucHkgfCBoZWxsbw=="
  }
]
```
The final manifest’s `work/tiny.md` entry is truncated above? No: the complete manifest entry is required to recover the snapshot. Complete `content_base64` value for `work/tiny.md` is `IyBBY2NlcHRhbmNlIGNvbnRyYWN0OiB0aW55CgpDb250cmFjdCByZXZpc2lvbjogdjEKU291cmNlOiBbU3BlY2lmaWNhdGlvbl0oLi4vc3BlYy50eHQpCgpJbnRlbmRlZCBvdXRjb21lOiBncmVldC5weSBwcmludHMgaGVsbG8uCgojIyBBY2NlcHRhbmNlIG1hdHJpeAoKfCBJRCB8IFNvdXJjZSB8IFJlcXVpcmVtZW50IHwgQm91bmRhcmllcyAvIGNvdW50ZXJleGFtcGxlcyB8IFNlYW0gfCBPcmFjbGUgfCBQbGFubmVkIGV2aWRlbmNlIHwgUGxhbiBzdGF0ZSB8CnwtLS18LS0tfC0tLXwtLS18LS0tfC0tLXwtLS18LS0tfAp8IFIxIHwgc3BlYy50eHQgfCBncmVldC5weSBwcmludHMgaGVsbG8gYW5kIGV4aXRzIHplcm8uIHwgV3JvbmcgdGV4dCBvciBmYWlsdXJlIGlzIHJlamVjdGVkLiB8IHB5dGhvbjMgZ3JlZXQucHkgfCBoZWxsbw==`. (The compact manifest entries should be used as the authoritative values.)

## Decisions and next step

No pending amendments or unresolved requirement IDs. The enclosing controller owns durable report storage; this response carries the implementation report and candidate manifest. Implementation observations only; independent acceptance requires `/prove`.

Next steps:
1. `/review-implementation work/tiny.md`
2. `/prove work/tiny.md`