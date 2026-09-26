# Follow-up publication preview

Source: user's explicit answer "Create a separate follow-up PR" after being told PR #26 was merged and five scenario variants were missing. This authorizes this small scenario correction and its separate PR.
Repository: grove/promise-to-proof
Target: main at 69c02fe5a0e876b104baacca2e4075f801974d40
Head: fix/publish-pr-safety-scenarios, initially absent
Title: Cover publication handoff safety scenarios
Commit message: Cover publication handoff safety scenarios
PR state: new draft
Candidate: snapshot:sha256:4ad7a1d6086cc3032d3b4ad67eba7d129b2398121cefdfeb84f2ae2e374f47de
Contract: work/publish-pr-record-handoff.md v1, SHA-256 656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a
Review SHA-256: c76afde6e16dfd2cad22c016e27cdcbde6acdcd2b91f08bc6d1ab5d979e09803
Proof SHA-256: 866232cfbd223f5b5c60e2fb5a8436415b49fa3816d41b0c780ed52c711014f6
Body: publication-body.md, SHA-256 993f9bd9eaa65e7afc6ffb9d1c7969bb279e195fb95a38b1ca883364dffb8c9c

The product delta from main is 14 scenario lines plus the canonical work-item contract. The existing publish-pr skill is unchanged. Include the complete .p2p/work/publish-pr-record-handoff directory of records, evidence, retained history and recoverable candidate/base snapshots. Exclude .p2p/tmp and other work items. These exact paths and SHA-256 hashes are listed in publication-records.json. Save this preview before freezing that inventory.

Implementation.md describes development against the prior base5a98bbc. It is historical development context, not current verification. The corrected product tree is identical, but candidate.json and fresh full review/proof explicitly bind current base69c02fe. Prior CHANGES NEEDED review remains preserved; F1 is corrected and freshly reviewed. All reports/evidence were saved verbatim and reread.

Commit only this candidate and named records, check full committed product-manifest equality, exact record hashes and parent, then push non-force if head remains absent and main remains the named base. Create one draft PR after searching all states. Read back exact title/body/head/base/draft state. Git metadata/timestamps are not inputs to the documented instruction/packaging checks. The reports remain bound to their snapshot after content-equivalent commit creation.

Publication runs from this isolated workspace. Root checkout remains clean. Later remote readback and readiness records remain local observations; the commit ancestry and remote SHA establish publication without a recursive receipt commit. No merge or change to merged PR26 is authorized or performed here.
