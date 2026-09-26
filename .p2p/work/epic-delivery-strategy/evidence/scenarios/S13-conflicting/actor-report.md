# BLOCKED: deliver-issue work/lookup.md
Agent context: /root/scenario_routing_batch (shared host context; fixtures are separate)
Run ID: S13-conflicting-453e800c-e886-42d9-8d7e-5440f4bf7296
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: 444ddc899308dc7233896b2af2837009edb795fc
Plan: .p2p/work/parent/slicing.md v1 sha256:872102c609b812ff57246efa700e44330789de9bfd25c8cce27c36672d184e4a; exact text retained in command-evidence.txt.

Destination epic/example; final destination trunk. Approved integration origin 444ddc899308dc7233896b2af2837009edb795fc.
Local and remote epic/example point to 58fb141b100c837ead68b810ddb469fec407451e. git merge-base --is-ancestor 444ddc899308dc7233896b2af2837009edb795fc epic/example exits 1. This is unrelated integration history, despite identical product tree bytes; it cannot be reused as the approved origin. Preserve the conflicting branch and do not force/reset it.
No branch/remote/product changes, acceptance or readiness claim.
Next steps:
1. Reconcile the unrelated epic/example ref under explicit authority or approve a different integration ref via /slice-contract work/parent.md, then resume /deliver-issue work/lookup.md.

Retained command evidence: .p2p/work/lookup/evidence/scenario-command-evidence.txt sha256:96ebb19a4ccbc7d22400bcb9858ec2e9563e0b2a6877735ae8a936c7344b8830
