from importlib.machinery import SourceFileLoader
import pathlib,hashlib,json,re,datetime
m=SourceFileLoader('actor','../actor-run.py').load_module(); root=m.root; repo=m.repo
sha='2a7733c6ac449ab6203d856f090c2e67173daace'; base='928231303f30c9c01d93754ce5653e9b27b42399'
def digest(b):return hashlib.sha256(b).hexdigest()
def save(slug,name,data,skill='prove'):
 if isinstance(data,str):data=data.encode()
 p=root/('stage-'+slug+'-'+name.replace('/','-')); p.write_bytes(data)
 r=m.run(['python3',f'../installed/{skill}/scripts/p2p_filesystem.py','--repo','.', 'save',f'work/{slug}.md',name,'--from',str(p)]); assert r.returncode==0
 out=repo/f'.p2p/work/{slug}'/name
 assert out.read_bytes()==data
 m.run(['python3','-c',f"import pathlib,hashlib; p=pathlib.Path({str(out)!r}); print(str(p),len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest())"])
 return out
hashes={str(p.relative_to(root)):digest(p.read_bytes()) for skill in ['prove','review-implementation','publish-pr','merge-readiness'] for p in sorted((root/'installed'/skill).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
save('parent','evidence/installed-package-hashes.json',json.dumps(hashes,indent=2)+'\n')
plan=(repo/'.p2p/work/parent/slicing.md').read_bytes(); sections=re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)',plan,re.M|re.S); assert len(sections)==1; section=sections[0]; ph=digest(section)
for name in ['publication','merge-readiness']:
 save('parent',f'evidence/{name}-approved-section.md',section,name if name=='publish-pr' else 'prove')
assert (repo/'.p2p/work/parent/approval.md').is_file()
records=[json.loads(l) for l in m.log.read_text().splitlines()]
checks=[r for r in records if r['command'][:2]==['python3','check.py'] or (r['command'][:2]==['python3','-c'] and 'child boundaries PASS' in r.get('stdout',''))]
evidence='\n'.join('Command: '+json.dumps(r['command'])+'\nExit: '+str(r['returncode'])+'\nstdout:\n'+r['stdout']+'\nstderr:\n'+r['stderr'] for r in checks)
save('parent','evidence/behavior.txt',evidence)
common=f'''Actor context: /root/scenario_parent_repaired; single actor, no delegated reviewers.
Candidate: git:{sha}; recoverable with git show {sha}:<path>.
Parent comparison base / merge base: {base} (observed local and origin trunk).
Plan: .p2p/work/parent/slicing.md, v1, approved-section sha256:{ph}; approval receipt .p2p/work/parent/approval.md retained.
All children route grouped to epic/example at {sha}. Parent routes to trunk.
Environment: Python 3, disposable local fixture repository, PYTHONDONTWRITEBYTECODE=1; exact version and commands in evidence log.
Source reconciliation: specs/registry.md and all four v1 contracts inspected in full; no pending amendments found. ASCII scope; no network/persistence/automatic merge. Functions use ordinary in-memory string/dictionary operations. No unspecified architecture required.
Candidate and contract stability: unchanged. Helper validate passed with exact captured bases and binding hashes; git diff HEAD outside .p2p was empty and git status showed only .p2p.
Evidence: .p2p/work/parent/evidence/behavior.txt contains exact behavioral commands, observations, independent literal assertions, exit codes and stderr. Command transcript retained separately.
'''
for slug,parentid,obs in [('capture','R1',"capture('Ada') == {'ada': 'Ada'}"),('lookup','R2',"lookup({'ada':'Ada'},'ADA') == 'Ada'; lookup({},'ADA') is None"),('summary','R3',"summary('Ada') == 'Welcome Ada'")]:
 c=json.loads((repo/f'.p2p/work/{slug}/candidate.json').read_text())
 text=f'''# PROVEN: work/{slug}.md

Requirements: 1/1
Contract: work/{slug}.md v1 sha256:{c['work_item_sha256']}; exact bytes recoverable at {sha}:work/{slug}.md.
Binding inputs: {json.dumps(c['binding_inputs'])}
Comparison base: {sha}, current approved integration target. Lookup's previous base metadata is retained by helper history; no historical implementation/publication report was rewritten.
{common}
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada. Child R1 contributes parent {parentid}; decomposition keeps R4 for assembled-parent verification. Lookup prerequisite capture was exercised against the actual candidate, not inferred from issue state. Capture and summary have no prerequisites.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | {obs}; assertion matched literal contract examples, with empty and mixed-case boundaries | python3 check.py {slug}, exit 0; boundary command in parent/evidence/behavior.txt | proven |

## Counterexamples and limits

Empty input, mixed-case Ada/aDA and uppercase BOB preserved each original value through each child's public seam. Lookup also covered missing and many-key dictionaries. No child counterexample found. Parent greet('Ada') returns Welcome ADA; that assembled R4 failure does not add an unrelated sibling requirement to this child contract. No parent acceptance or child publication is asserted.

## Unresolved gaps

None for this child's complete contract.

## Repairs needed

None for this child.

Next steps:
1. `/review-implementation work/{slug}.md` against {sha} if child publication is requested; no child review was invoked here.
2. Complete parent R4 repair and fresh assembled-parent review/proof before parent publication.
'''
 save(slug,'proof.md',text)
parentc=json.loads((repo/'.p2p/work/parent/candidate.json').read_text()); parentid=f"work/parent.md v1 sha256:{parentc['work_item_sha256']}; immutable contract {sha}:work/parent.md; binding inputs {json.dumps(parentc['binding_inputs'])}"
review=f'''# CHANGES NEEDED: work/parent.md

Contract: {parentid}
{common}
Coverage: full R1–R4, actual registry.py, callers and assertions in check.py; full diff from trunk inspected. R1 capture lines 3–4, R2 lookup lines 6–7, R3 summary lines 9–10 implement promised primitive outcomes. R4 greet lines 12–13 loses original casing. All contributions exist in the single assembled candidate; trunk is an ancestor and no independent contribution is missing.

## Contract fidelity

F1 (R4, specs/registry.md original-case workflow): registry.py:13 passes name.upper() into capture. greet('Ada') produces Welcome ADA instead of literal Welcome Ada. check.py:13 fails. The direct primitive composition passes; the public assembled workflow still violates the source promise. Smallest correction: pass name itself to capture in greet, then rerun full proof. No repair performed.

## Scope and simplicity

No material change-required finding. The one-line diff adds no dependencies or framework. EXPERIMENTAL is unchanged pre-existing code without a new effect; no speculative redesign is required.

## Engineering quality

F1 is a concrete regression from trunk's case-preserving greet. Existing check.py detects it; reporting passing child commands alone would conceal it. No separate engineering finding beyond F1.

## Checks and limitations

Read every contract/source and full implementation/callers. Existing child checks exit 0; parent check exits 1 at greet('Ada'). Boundary observations independently corroborate loss of mixed case. One actor performed separate contract/scope/engineering passes; no independent-reviewer claim. Full scope examined; no identity unknown prevents this conclusion.

## Handoff

Report storage: .p2p/work/parent/review.md. Review only; acceptance and readiness are separate.

Next steps:
1. `/implement-contract work/parent.md; findings .p2p/work/parent/review.md` to correct F1 under separately authorized repair scope.
2. Capture the changed candidate, then refresh `/review-implementation work/parent.md` against current trunk and `/prove work/parent.md` for all R1–R4.
'''
save('parent','review.md',review,'review-implementation')
proof=f'''# NOT PROVEN: work/parent.md

Requirements: 3/4
Contract: {parentid}
{common}
## Outcome

All three child primitives behave as promised, but the assembled greeting destroys original case. Existing child proofs are supporting references, not an aggregated parent verdict.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | Ada maps to literal {{ada: Ada}}; empty and aDA preserve original values | check.py capture exit 0; boundary assertions | proven |
| R2 | Captured Ada read using ADA returns Ada; missing is None; many-key BOB lookup returns Bob | check.py lookup exit 0; boundary assertions using actual capture | proven |
| R3 | Ada maps to literal Welcome Ada; empty yields Welcome followed by one space | check.py summary exit 0; boundary assertions | proven |
| R4 | direct composition returns Welcome Ada, but actual greet('Ada') returns Welcome ADA; aDA also loses case | check.py parent exit 1 at line 13; independent printed/asserted boundary result | disproven |

## Counterexamples tested

Four name boundaries (empty, Ada, aDA, BOB), empty/missing dictionary and multi-key lookup; direct composition and public greet compared. Concrete counterexamples: Ada and aDA greeting casing. No persistence/restart/concurrency behavior promised; no invented requirement imposed.

## Unresolved gaps

R4 complete case-preserving public workflow fails. Candidate includes all contributions and final trunk ancestry, so this is an actual interaction defect, not missing child evidence.

## Repairs needed

R4: remove premature uppercasing at registry.py:13 so capture receives original name. No product, test or contract edits were made.

Next steps:
1. `/repair-gaps .p2p/work/parent/proof.md` under an authorized repair request.
2. Capture repaired candidate and run full `/review-implementation work/parent.md` against current trunk and `/prove work/parent.md` before publication/readiness.
'''
save('parent','proof.md',proof)
# Recheck live fixture read-only immediately before readiness record.
r=m.run(['gh','pr','view','https://fixture.invalid/epic/pull/18','--json','url,state,headRefName,headRefOid,baseRefName,baseRefOid,title,body,isDraft,reviewDecision,statusCheckRollup']); pr=json.loads(r.stdout)
assert pr['headRefOid']==sha and pr['baseRefOid']==base
for name,skill in [('publication','publish-pr'),('merge-readiness','merge-readiness')]:
 sectionref=f'.p2p/work/parent/evidence/{name}-approved-section.md'
 text=f'''# BLOCKED: parent {name}

Contract: {parentid}
{common}
Review: .p2p/work/parent/review.md, full CHANGES NEEDED (F1/R4).
Proof: .p2p/work/parent/proof.md, full NOT PROVEN (R4 disproven).
Destination: trunk at {base}; actual PR18 base matches approved final destination.
Head: epic/example at {sha}; PR https://fixture.invalid/epic/pull/18 is OPEN and draft.
Approved plan revision: v1
Approved section SHA-256: {ph}
Exact retained section: {sectionref}; byte-for-byte saved readback matches canonical extraction, including separator before Contributions.
Approval receipt: .p2p/work/parent/approval.md, SHA-256 {digest((repo/'.p2p/work/parent/approval.md').read_bytes())}. Strategy approval grants no publication effects.
Effects authorized: local report retention only; draft preparation and read-only readiness. Effects observed: no commit/ref/PR/tracker writes; checkout remains epic/example at original HEAD, original index and product unchanged; local .p2p records added/updated.
'''
 if name=='publication':
  text+='''\nMatching full REVIEWED and PROVEN reports do not exist. Therefore no executable publication preview can be prepared; draft-only does not override the missing admission pair. Existing PR18 is observed, not created by this stage. No proposed new title/body or duplicate PR is needed while blocked.
Merge readiness: NOT ASSESSED

Next steps:
1. Repair R4 through `/repair-gaps .p2p/work/parent/proof.md`, then obtain fresh full parent review/proof for the repaired candidate.
2. `/publish-pr work/parent.md; review .p2p/work/parent/review.md; proof .p2p/work/parent/proof.md; target trunk; draft only` after matching successful reports exist.
'''
 else:
  text+=f'''\nObservation time: {datetime.datetime.now(datetime.timezone.utc).isoformat()}.
Fixture gates supplied by request: required-ci SUCCESS at exact head and repository reviewDecision APPROVED. Current PR-head status rollup reports required-ci COMPLETED/SUCCESS and current reviewDecision APPROVED, read twice without drift. The checks projection contains no independent headSha; the current PR-head rollup is the available association. These statuses cannot replace failed assembled-parent acceptance.
Decision: BLOCKED for F1/R4, failed parent proof and change-required parent review. Parent integration, review and proof are distinct from all child completion. No merge authority granted.
Synchronization: skipped, explicitly read-only; PR body unchanged.
Proposed entry: Merge readiness: BLOCKED at this observation; head {sha}, base {base}; local .p2p/work/parent/merge-readiness.md; R4 case-preservation failure leaves parent review/proof unsatisfied. Applies only to this observed state.

Next steps:
1. `/repair-gaps .p2p/work/parent/proof.md` under explicit repair authority.
2. `/review-implementation work/parent.md` against current trunk and `/prove work/parent.md` on the changed candidate, covering all requirements.
3. `/merge-readiness https://fixture.invalid/epic/pull/18; review .p2p/work/parent/review.md; proof .p2p/work/parent/proof.md; read-only` after reports and head match.
'''
 save('parent',name+'.md',text,skill)
 saved=(repo/sectionref).read_bytes(); recorded=(repo/f'.p2p/work/parent/{name}.md').read_text(); assert saved==section and digest(saved)==ph and ph in recorded
 m.run(['python3','-c',f"import pathlib,re,hashlib; a=pathlib.Path('.p2p/work/parent/slicing.md').read_bytes(); s=re.findall(rb'^## Approved delivery plan\\r?\\n.*?(?=^## |\\Z)',a,re.M|re.S); b=pathlib.Path({sectionref!r}).read_bytes(); assert len(s)==1 and s[0]==b; assert hashlib.sha256(b).hexdigest()=={ph!r}; print('saved approved-section bytes and hash match:',len(b),{ph!r})"])
report=f'''# Parent repair actor report

Actor: /root/scenario_parent_repaired. Actual installed skills invoked: prove (three children and full parent), review-implementation (full parent), publish-pr (draft-only admission), merge-readiness (read-only PR18). No delegation. No repair executed.

Candidate: {sha}; parent base {base}; child metadata recovered/captured against current approved integration tip {sha}. Lookup prior candidate metadata retained in helper history. No product/ref/contract/tracker edits.

Actual outcomes: capture PROVEN 1/1; lookup PROVEN 1/1; summary PROVEN 1/1; parent review CHANGES NEEDED; parent proof NOT PROVEN 3/4, R4 disproven; parent publication BLOCKED; PR18 readiness BLOCKED despite current successful required-ci rollup and APPROVED repository decision.

Root cause observed: registry.py:13 calls capture(name.upper()). greet('Ada') actually returns Welcome ADA. The independent literal oracle requires Welcome Ada. Full parent check fails; direct primitive composition and all child checks pass. Exact commands, exit statuses and output are retained in parent-repair-command-evidence.jsonl and behavior evidence, including initial helper validate invocations missing --base and successful corrected validations. No outcome inferred from fixture name.

Plan extraction: exact repaired-protocol regex; revision v1; sha256:{ph}. Both publication/readiness retained section files are read back and compared byte-for-byte and by digest, including trailing separator. Approval receipt remains retrievable. Package hashes: .p2p/work/parent/evidence/installed-package-hashes.json.

Durable reports saved and reread via installed filesystem helpers with history: .p2p/work/{{capture,lookup,summary}}/proof.md and .p2p/work/parent/{{review,proof,publication,merge-readiness}}.md. Commands use only supplied fixture gh, EPIC_TRACKER_ROOT and bin PATH; origin is local bare repo. No oracle/tracker/builder/main-project reads.

Next steps:
1. Repair parent R4 only when authorized, then capture fresh candidate and refresh full parent review and proof.
2. Reconsider publication/readiness only with matching successful reports and current gates.
'''
(root/'parent-repair-actor-report.md').write_text(report)
save('parent','parent-repair-actor-report.md',report)
for slug in ['capture','lookup','summary','parent']:
 m.run(['python3','../installed/prove/scripts/p2p_filesystem.py','--repo','.','validate',f'work/{slug}.md','--base',base if slug=='parent' else sha])
m.run(['git','status','--short']); m.run(['git','diff','HEAD','--','.',':!.p2p']); m.run(['git','show-ref'])
save('parent','evidence/parent-repair-command-evidence.jsonl',m.log.read_bytes())
print('FINISHED',ph)
