# R20 readiness boundary run record

- Run kind: merge-readiness model-skill execution against a disposable controlled fixture.
- Actor input: `actor-request.md` plus `controlled-input.json`, `actor-resources/merge-readiness-SKILL.md`, `actor-resources/acceptance-contract-protocol.md`, and `actor-resources/merge-readiness-scenarios.md`.
- The three actor resources were copied from the current checkout. Their hashes are recorded below.
- Oracle isolation: `expected-oracle.md` was kept outside the actor request/resources and was not included in actor input.
- No GitHub CLI, tracker, browser, network, or remote API was used. The fixture PR uses the reserved `.invalid` hostname. The local clone's origin was removed; `git remote -v` returned no remotes.
- This is acceptance-fixture candidate C′=`git:495bb1899b82f9d5c1b7c05d78fb15922b330a11`, not issue-37 candidate C.

## Report-pair check

The fixture's canonical contract bytes hash to `b490dc25a68ba6521282128bcf60bc3f77e8a11b907b0c9b385402fa230677cb`. `candidate.json` names that hash, candidate commit C′, comparison base A=`9384d662d425d222df3f5547bcbf84ba7cd10973`. The contract source `skills/productivity/review-implementation/SKILL.md` hashes to its bound digest `eabc51ad2ec4cb31aee379cc89a10b200f186cff730cc62ec25568a895a9b5ca`. The saved review starts `REVIEWED`, covers R1–R3, and names the same contract, candidate, and base. The saved proof starts `PROVEN`, states requirements 3/3, contains one `proven` verdict for each of R1, R2, and R3, and names the same contract, candidate, and base. Its referenced 35-test output is included in the fixture. A local assertion printed `PAIR VALID: exact contract/candidate identities match; full REVIEWED R1-R3 and PROVEN 3/3 reports; fixture head equals candidate.`

## Controlled PR and repository state

The fixture branch `fixture-pr` is at C′. The fixture branch `main` is B=`68c526be33642bca0f378bb90618632532cc1244`; both C′ and B descend from A, and their merge base is A. The fixture PR observation at 2026-09-27 21:12:17 UTC says OPEN, head C′, target `main` at B. The fixture's known `main` policy requires `controller-contract` and one approval; the recorded current state is check PENDING and approvals 0/1. The fixture description input is retained unchanged. No body write was attempted.

## Result

The exact saved response is `actor-response.md`; the same bytes are saved as the fixture's `.p2p/work/delivery-review-report-contract/merge-readiness.md`. The skill returned `BLOCKED`: review base A does not cover the current PR target B, the required check is pending, and repository approval is missing. It retained the exact valid REVIEWED/PROVEN pair and did not claim the pair was invalid. Synchronization is skipped, with a proposed BLOCKED paragraph shown. The first verification action is full review against B; passing CI and an approval remain separate gates.

## Limits

These are controlled local inputs and Git refs, not authentic GitHub observations. This run establishes the skill's decision over those observations; it does not establish live tracker parsing, API behavior, current GitHub rules, or any state for issue-37 candidate C. No product files or the source checkout were changed by this run; fixture report overlays and the readiness record are confined to `/private/tmp/issue37-r20-readiness-boundary/repo`.
