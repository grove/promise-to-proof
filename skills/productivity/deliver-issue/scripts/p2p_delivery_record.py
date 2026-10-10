#!/usr/bin/env python3
"""Validate existing P2P Delivery Record v1 and preview a landed-code extension.

Pure/read-only protocol operations for #50. Publishing, merger authority, and
durable receipt readback belong to #47. No second record format or state store.
"""
import argparse
import copy
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

import p2p_filesystem as fs
import verify_acceptance_bundle as bundle


SCHEMA = "promise-to-proof/delivery-record/v1"
LOCAL = "REVIEWED_AND_PROVEN"
LANDED = "LANDED"
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
GIT_SHA = re.compile(r"(?:[a-f0-9]{40}|[a-f0-9]{64})\Z")
PR_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/[1-9][0-9]*\Z")
METHODS = frozenset(("merge", "squash", "rebase", "direct", "integrated"))


def _need(ok, message):
    if not ok:
        raise ValueError(message)


def _keys(value, required, where):
    _need(isinstance(value, dict) and set(value) == set(required),
          where + " has missing or unsupported fields")


def _digest(value, label):
    _need(isinstance(value, str) and SHA256.fullmatch(value), "invalid " + label)
    return value


def _commit(root, value, label):
    _need(isinstance(value, str) and GIT_SHA.fullmatch(value), "invalid " + label)
    _need(fs.full_commit(root, value) == value, "unavailable exact " + label)
    return value


def _timestamp(value, name):
    _need(isinstance(value, str), "missing " + name)
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        raise ValueError("invalid ISO timestamp: " + name) from None
    _need(parsed.tzinfo is not None and parsed.utcoffset() is not None,
          "timestamp needs timezone: " + name)
    return parsed


def _encoded(value):
    # Match p2p_delivery.encoded used to hash final candidate.json.
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b"\n"


def _source_context(root, record, checkpoint, artifact_directory):
    indexed, cp = {}, None
    if checkpoint is not None:
        _need(isinstance(checkpoint, bytes), "checkpoint must contain exact bytes")
        try:
            cp, contents = fs.read_checkpoint(root, checkpoint)
        except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
            raise ValueError("exact portable checkpoint is invalid or incomplete: " + str(error)) from error
        _need(cp["work_item"] == record["work_item"],
              "portable checkpoint belongs to a different delivery")
        indexed = {(scope, path): data for scope, path, data in contents}
    directory = Path(artifact_directory) if artifact_directory is not None else None
    work = record["work_item"]
    slug = fs.work_slug(work)

    def saved(relative, *, scopes=("project",), artifact_name=None):
        for scope in scopes:
            data = indexed.get((scope, relative))
            if data is not None:
                return data
        if directory is not None and artifact_name:
            file = directory / artifact_name
            if file.is_file() and not file.is_symlink():
                return file.read_bytes()
        if checkpoint is None:
            file = fs.safe(root, relative)
            if file.is_file() and not file.is_symlink():
                return file.read_bytes()
        return None

    contract_bytes = saved(work, scopes=("project", "agreement"))
    _need(contract_bytes is not None, "exact original contract is not retrievable")
    try:
        contract_text = contract_bytes.decode("utf-8")
    except UnicodeError:
        raise ValueError("contract is not valid UTF-8") from None
    _need(fs.digest(contract_bytes) == record["contract"]["sha256"],
          "record contract differs from original accepted text")
    source = re.findall(r"^# Acceptance contract: ([^\r\n]+)\r?$", contract_text, re.M)
    revision = re.findall(r"^Contract revision: (v[1-9][0-9]*)\r?$", contract_text, re.M)
    _need(len(source) == len(revision) == 1 and
          record["contract"] == {"source": source[0], "revision": revision[0],
                                  "sha256": fs.digest(contract_bytes)},
          "contract identity/revision differs from accepted text")
    violations = []
    _, _, _, requirements = bundle._validate_contract(
        {"source": source[0], "revision": revision[0], "content": contract_text,
         "sha256": record["contract"]["sha256"]}, violations)
    _need(not violations and requirements, "contract requirements/coverage are invalid")
    binding_rows = record["binding_inputs"]
    _need(isinstance(binding_rows, list) and
          len(binding_rows) == len({row.get("path") for row in binding_rows if isinstance(row, dict)}),
          "binding input list is invalid or duplicated")
    for row in binding_rows:
        _keys(row, ("path", "sha256"), "binding input")
        _digest(row["sha256"], "binding digest")
        fs.safe(root, row["path"])
        data = saved(row["path"], scopes=("project", "agreement"))
        _need(data is not None and fs.digest(data) == row["sha256"],
              "binding input unavailable or changed: " + row["path"])
    _need(isinstance(record.get("agreement_paths"), list) and
          work in record["agreement_paths"] and
          len(record["agreement_paths"]) == len(set(record["agreement_paths"])),
          "record agreement-path exclusions are missing or duplicated")
    for name in record["agreement_paths"]:
        fs.safe(root, name)

    execution = cp.get("execution") if cp else None
    candidate_path = f".p2p/work/{slug}/artifacts/candidate.json"
    candidate_bytes = saved(candidate_path, artifact_name="candidate.json")
    if execution is not None:
        _need(execution.get("status") == LOCAL and
              execution.get("invocation_id") == record["invocation_id"] and
              execution.get("contract", {}).get("sha256") == record["contract"]["sha256"] and
              execution.get("binding_inputs") == binding_rows,
              "checkpoint execution differs from completed agreement or invocation")
        state_candidate = execution.get("candidate")
        _need(isinstance(state_candidate, dict),
              "checkpoint has no retained candidate")
        if candidate_bytes is None:
            candidate_bytes = _encoded(state_candidate)
        else:
            _need(json.loads(candidate_bytes) == state_candidate,
                  "retained final candidate differs from controller execution")
    _need(candidate_bytes is not None, "exact candidate record is not retrievable")
    _need(fs.digest(candidate_bytes) == record["candidate_record_sha256"],
          "candidate record bytes have changed")
    try:
        candidate = json.loads(candidate_bytes)
    except (ValueError, TypeError):
        raise ValueError("candidate record is malformed") from None
    _need(isinstance(candidate, dict) and candidate.get("key") == record["candidate_key"] and
          candidate.get("work_item") == work and
          candidate.get("work_item_sha256") == record["contract"]["sha256"] and
          candidate.get("comparison_base") == record["comparison_base"] and
          candidate.get("binding_inputs") == binding_rows and
          fs.digest(fs.canonical(candidate.get("changes"))) == record["candidate_changes_sha256"],
          "candidate identity, scope or base differs from the recorded acceptance")

    if execution is not None:
        review = execution.get("final_review")
        proof = execution.get("final_proof")
        _need(isinstance(review, str) and isinstance(proof, str),
              "checkpoint has no final independent review and proof text")
        review_bytes, proof_bytes = review.encode(), proof.encode()
    else:
        review_bytes = saved(f".p2p/work/{slug}/artifacts/review.md",
                             artifact_name="review.md")
        proof_bytes = saved(f".p2p/work/{slug}/artifacts/proof.md",
                            artifact_name="proof.md")
    _need(review_bytes is not None and proof_bytes is not None and
          fs.digest(review_bytes) == record["review_sha256"] and
          fs.digest(proof_bytes) == record["proof_sha256"],
          "independent review/proof content is missing or changed")
    return {"checkpoint": cp, "indexed": indexed, "execution": execution,
            "contract": contract_text, "requirements": sorted(requirements),
            "candidate": candidate, "review": review_bytes, "proof": proof_bytes}


def _independent_coverage(context, record):
    """A new landed claim needs the complete independent #82 stage receipts."""
    state = context["execution"]
    _need(isinstance(state, dict), "landed code needs a full verified #82 controller checkpoint")
    reports = state.get("reports")
    _need(isinstance(reports, dict), "retained independent reports are missing")
    attempts = state.get("attempts")
    _need(isinstance(attempts, list), "stage receipts are missing")
    sessions = []
    for name, expected in (("review", "REVIEWED"), ("proof", "PROVEN")):
        meta = reports.get(name)
        _need(isinstance(meta, dict) and isinstance(meta.get("path"), str),
              "missing retained " + name + " report")
        data = context["indexed"].get(("runtime", meta["path"]))
        _need(data is not None and fs.digest(data) == meta.get("sha256"),
              "unretrievable independent " + name + " report")
        report = json.loads(data)
        _need(report.get("status") == expected and not report.get("gaps") and
              (name != "review" or not report.get("findings")),
              "nonpassing or incomplete " + name + " verdict")
        rows = report.get("requirements")
        _need(isinstance(rows, list) and
              sorted(row.get("id") for row in rows if isinstance(row, dict)) ==
              context["requirements"] and len(rows) == len(context["requirements"]),
              name + " misses accepted requirements")
        if name == "proof":
            _need(all(row.get("verdict") == "proven" and
                      isinstance(row.get("evidence"), list) and row["evidence"] and
                      all(isinstance(e, dict) and
                          all(isinstance(e.get(k), str) and e[k].strip() for k in
                              ("assertion", "observation", "artifact")) for e in row["evidence"])
                      for row in rows),
                  "proof lacks complete requirement-by-requirement evidence")
        inputs = meta.get("inputs")
        try:
            returned_inputs = json.loads(report["input_identity_json"])
        except (ValueError, TypeError, KeyError):
            raise ValueError("invalid " + name + " identity") from None
        _need(returned_inputs == inputs and
              inputs.get("key") == record["candidate_key"] and
              inputs.get("comparison_base") == record["comparison_base"] and
              inputs.get("work_item_sha256") == record["contract"]["sha256"],
              "stale or conflicting " + name + " verdict identity")
        ids = [a for a in attempts if a.get("id") == meta.get("attempt_id") and
               a.get("stage") == name and a.get("status") == "complete"]
        _need(len(ids) == 1 and ids[0].get("report_validation") == "accepted",
              name + " has no completed, accepted independent stage")
        session = ids[0].get("session_id")
        receipt_data = context["indexed"].get(("runtime", "attempts/" + ids[0]["id"] +
                                               "/portable-receipt.json"))
        _need(receipt_data is not None, "missing independent host execution receipt")
        host = json.loads(receipt_data).get("host")
        _need(isinstance(host, dict) and host.get("session_id") == session,
              "independent host session does not match its stage receipt")
        if name == "proof":
            executions = host.get("executions")
            _need(isinstance(executions, list) and executions and
                  all(isinstance(e, dict) and isinstance(e.get("command"), str) and
                      e["command"].strip() and type(e.get("exit_code")) is int and
                      isinstance(e.get("output_sha256"), str) and
                      SHA256.fullmatch(e["output_sha256"]) for e in executions),
                  "proof lacks trusted execution observations in the retained host receipt")
        sessions.append(session)
    _need(len(set(sessions)) == 2 and all(isinstance(s, str) and s for s in sessions),
          "independent review and proof need distinct host sessions")


def _parents(root, sha):
    result = fs.git(root, "rev-list", "--parents", "-n", "1", sha).decode().split()
    _need(result and result[0] == sha, "Git history cannot identify landed commit")
    return result[1:]


def _ancestor(root, older, newer):
    result = subprocess.run(["git", "-C", str(root), "merge-base",
                             "--is-ancestor", older, newer],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def _id_projection(record, landed):
    return ["promise-to-proof/delivery-record/landed/v1",
            record["invocation_id"], record["contract"], record["comparison_base"],
            record["candidate_key"], record["candidate_changes_sha256"],
            landed["method"], landed["repository"],
            landed["destination"], landed["candidate_commit"],
            None if landed["pull_request"] is None else
            {key: landed["pull_request"][key] for key in ("url", "head")}]


def _receipt_id(record, landed):
    # Wall-clock observations and checkpoint transport do not change the event.
    return "sha256:" + fs.digest(fs.canonical(_id_projection(record, landed)))


def _event_id(record, landed):
    return fs.digest(fs.canonical(
        ["delivery-event/v1", record["invocation_id"], landed["repository"],
         landed["destination"]["ref"], landed["destination"]["after"]]))


def _verified_landing(root, record, landed, context, checkpoint):
    _keys(landed, ("status", "event_id", "receipt_id", "method", "repository",
                   "destination", "candidate_commit", "pull_request",
                   "checkpoint_sha256", "confirmed_at", "evidence_refs"), "landing")
    _need(landed["status"] == LANDED, "unrecognized delivery landing status")
    _need(landed["method"] in METHODS, "unsupported delivered-code relationship")
    _need(isinstance(landed["repository"], str) and
          re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", landed["repository"]),
          "invalid delivery destination repository")
    _timestamp(landed["confirmed_at"], "landing confirmation")
    _digest(landed["checkpoint_sha256"], "checkpoint identity")
    _need(fs.digest(checkpoint) == landed["checkpoint_sha256"],
          "landed claim does not reference this exact portable checkpoint")
    _keys(landed["destination"], ("ref", "before", "after", "tree"), "delivered destination")
    target = landed["destination"]
    route = record.get("routing")
    _need(isinstance(route, dict) and target["ref"] == route.get("target_ref"),
          "delivered branch differs from the approved destination")
    _need(isinstance(target["ref"], str) and
          target["ref"].startswith(("refs/heads/", "refs/remotes/")) and
          not any(ch.isspace() for ch in target["ref"]),
          "invalid destination reference")
    before = _commit(root, target["before"], "destination predecessor")
    after = _commit(root, target["after"], "delivered commit")
    _need(isinstance(target["tree"], str) and GIT_SHA.fullmatch(target["tree"]) and
          fs.git(root, "rev-parse", after + "^{tree}").decode().strip() == target["tree"],
          "delivered tree identity differs from the exact commit")
    try:
        current = fs.git(root, "rev-parse", "--verify", target["ref"] + "^{commit}").decode().strip()
    except ValueError:
        raise ValueError("approved destination ref cannot be read back") from None
    _need(GIT_SHA.fullmatch(current) and _ancestor(root, after, current),
          "delivered commit is not on the current approved destination history")
    base = _commit(root, record["comparison_base"], "frozen comparison base")
    _need(_ancestor(root, base, before),
          "destination predecessor is not based on the frozen comparison base")
    candidate_commit = _commit(root, landed["candidate_commit"], "retained approved candidate")
    cp = context["checkpoint"]
    _need(cp is not None and cp["candidate_commit"] == candidate_commit,
          "landed candidate is not the recoverable #82 checkpoint candidate")
    excludes = record["agreement_paths"]
    original = fs.snapshot(root, base, exclude=excludes)
    candidate = fs.snapshot(root, candidate_commit, exclude=excludes)
    predecessor = fs.snapshot(root, before, exclude=excludes)
    delivered = fs.snapshot(root, after, exclude=excludes)
    _need(fs.snapshot_key(candidate) == record["candidate_key"],
          "retained source candidate does not match reviewed product tree")
    changes = fs.tree_changes(original, candidate)
    _need(changes == context["candidate"]["changes"] and
          fs.digest(fs.canonical(changes)) == record["candidate_changes_sha256"],
          "accepted changed-path scope has changed")
    base_files = {e["path"]: e for e in fs.tree_identity(original)}
    candidate_files = {e["path"]: e for e in fs.tree_identity(candidate)}
    expected = {e["path"]: e for e in fs.tree_identity(predecessor)}
    for change in changes:
        name = change["path"]
        _need(expected.get(name) in (base_files.get(name), candidate_files.get(name)),
              "overlapping destination change needs new independent acceptance: " + name)
        if name in candidate_files:
            expected[name] = candidate_files[name]
        else:
            expected.pop(name, None)
    actual = {e["path"]: e for e in fs.tree_identity(delivered)}
    _need(actual == expected,
          "delivered product tree adds, loses, or changes unreviewed scope")
    parents = _parents(root, after)
    method = landed["method"]
    if method == "integrated":
        _need(before == after and landed["pull_request"] is None and
              fs.snapshot_key(delivered) == record["candidate_key"] and
              "## Children" in fs.document_lines(context["contract"]) and
              re.search(r"(?m)^## Children\r?$[\s\S]*?\[[^\]]+\]\([^)]+\)",
                        context["contract"]) is not None,
              "no-PR parent integration requires an actual linked child and whole assembled candidate proof")
    else:
        _need(before != after and changes,
              "delivery needs an actual changed candidate and a distinct landed commit")
        if method == "merge":
            _need(len(parents) == 2 and parents[0] == before,
                  "merge mapping must name the actual first-parent destination predecessor")
        elif method in ("squash", "direct"):
            _need(parents == [before], "single-commit delivery has a different parent")
        else:  # rebase is a linear sequence after the verified predecessor.
            _need(_ancestor(root, before, after), "rebase is not on destination history")
            commits = fs.git(root, "rev-list", "--first-parent", after, "^" + before).decode().splitlines()
            _need(commits and all(len(_parents(root, sha)) == 1 for sha in commits),
                  "rebase mapping contains a merge or uncertain ancestor")
    pr = landed["pull_request"]
    if pr is not None:
        _keys(pr, ("url", "head", "merged_at"), "pull request")
        url = pr["url"]
        match = PR_URL.fullmatch(url) if isinstance(url, str) else None
        _need(match is not None and match[1] == landed["repository"],
              "PR identity belongs to a different repository")
        _timestamp(pr["merged_at"], "pull request merge")
        head = _commit(root, pr["head"], "reviewed PR head")
        _need(fs.snapshot_key(fs.snapshot(root, head, exclude=excludes)) == record["candidate_key"],
              "published PR head differs from the accepted candidate")
        _need(method not in ("direct", "integrated"),
              "direct/assembled delivery does not use a dedicated PR")
        if method == "merge":
            _need(parents[1] == head, "merge commit does not include the reviewed PR head")
    if method == "integrated":
        _need(pr is None, "assembled parent without PR cannot name one")
    _digest(landed["event_id"], "delivery event identity")
    _need(landed["event_id"] == _event_id(record, landed) and
          landed["receipt_id"] == _receipt_id(record, landed),
          "delivery event/receipt identity differs from canonical facts")
    references = landed["evidence_refs"]
    _need(isinstance(references, list) and
          len(references) == len({(r.get("scope"), r.get("path")) for r in references
                                  if isinstance(r, dict)}),
          "duplicate or malformed normalized evidence references")
    for row in references:
        _keys(row, ("scope", "path", "sha256"), "evidence reference")
        _digest(row["sha256"], "evidence digest")
        content = context["indexed"].get((row["scope"], row["path"]))
        _need(content is not None and fs.digest(content) == row["sha256"],
              "normalized evidence reference lacks retrievable matching bytes")
        if row["path"].endswith(".json"):
            try:
                evidence = json.loads(content)
            except (ValueError, UnicodeError):
                raise ValueError("normalized evidence is malformed") from None
            _need(isinstance(evidence, dict) and
                  evidence.get("schema") == "promise-to-proof/evidence-record/v1",
                  "evidence reference does not contain a normalized Evidence Record v1")
            _need(evidence.get("candidate") == record["candidate_key"] and
                  evidence.get("contract") == record["contract"] and
                  isinstance(evidence.get("requirements"), list) and
                  evidence["requirements"] and
                  set(evidence["requirements"]) <= set(context["requirements"]),
                  "normalized evidence belongs to a different candidate or promise")
    return {"status": "LANDED_MAPPING_VERIFIED", "receipt_id": landed["receipt_id"],
            "event_id": landed["event_id"], "method": method,
            "destination_ref": target["ref"], "delivered_commit": after,
            "delivered_tree": target["tree"], "observed_destination_tip": current,
            "pull_request": pr["url"] if pr else None,
            "checkpoint_sha256": landed["checkpoint_sha256"],
            "receipt_published": False,
            "next_action": "Issue #47 must verify effect authority, publish/read back the receipt, and finalize; this validator performs no remote effect."}


def validate(root, record, *, checkpoint=None, artifact_directory=None):
    """Validate old local records unchanged; confirm landed code only with #82 facts."""
    root = Path(root).resolve()
    _need(isinstance(record, dict) and record.get("schema") == SCHEMA and
          record.get("status") == LOCAL, "invalid or unsupported Delivery Record v1")
    work = record.get("work_item")
    _need(isinstance(work, str) and fs.WORK.fullmatch(work),
          "invalid canonical work-item path")
    _need(isinstance(record.get("invocation_id"), str) and record["invocation_id"].strip(),
          "delivery has no stable invocation identity")
    _keys(record.get("contract"), ("source", "revision", "sha256"), "contract")
    _digest(record["contract"]["sha256"], "contract digest")
    _digest(record.get("candidate_record_sha256"), "candidate record digest")
    _digest(record.get("candidate_changes_sha256"), "candidate changes digest")
    _digest(record.get("review_sha256"), "review digest")
    _digest(record.get("proof_sha256"), "proof digest")
    _need(isinstance(record.get("candidate_key"), str) and
          re.fullmatch(r"snapshot:sha256:[a-f0-9]{64}", record["candidate_key"]),
          "invalid reviewed product candidate key")
    _timestamp(record.get("completed_at"), "local acceptance")
    _commit(root, record.get("comparison_base"), "frozen comparison base")
    context = _source_context(root, record, checkpoint, artifact_directory)
    if "landing" not in record:
        return {"status": "LOCAL_REVIEWED_PROVEN", "work_item": work,
                "candidate_key": record["candidate_key"],
                "receipt_published": False,
                "next_action": "Local review and proof do not establish code landing, publication or merge."}
    _need(checkpoint is not None,
          "landed-code validation needs the exact published #82 checkpoint bytes")
    _independent_coverage(context, record)
    return _verified_landing(root, record, record["landing"], context, checkpoint)


def preview(root, record, *, checkpoint, method, repository, destination_ref,
            before, after, confirmed_at, pull_request=None, pr_head=None,
            merged_at=None, evidence_refs=()):
    """Create a deterministic, *unpublished* landed-code record for #47."""
    root = Path(root).resolve()
    validate(root, {k: v for k, v in record.items() if k != "landing"},
             checkpoint=checkpoint)
    value, _ = fs.read_checkpoint(root, checkpoint)
    after = _commit(root, after, "delivered commit")
    landed = {
        "status": LANDED, "method": method, "repository": repository,
        "candidate_commit": value["candidate_commit"],
        "destination": {"ref": destination_ref, "before": before, "after": after,
                        "tree": fs.git(root, "rev-parse", after + "^{tree}").decode().strip()},
        "pull_request": ({"url": pull_request, "head": pr_head, "merged_at": merged_at}
                         if pull_request is not None else None),
        "checkpoint_sha256": fs.digest(checkpoint),
        "confirmed_at": confirmed_at,
        "evidence_refs": list(evidence_refs),
    }
    landed["event_id"] = _event_id(record, landed)
    landed["receipt_id"] = _receipt_id(record, landed)
    result = copy.deepcopy(record)
    if "landing" in result:
        if result["landing"]["receipt_id"] != landed["receipt_id"]:
            raise ValueError("conflicting completed-delivery event; do not replace an earlier receipt")
        validate(root, result, checkpoint=checkpoint)
        return result
    result["landing"] = landed
    validate(root, result, checkpoint=checkpoint)
    return result


def render(record, verified):
    """Plain-language presentation is derived from this exact machine record."""
    if verified["status"] == "LOCAL_REVIEWED_PROVEN":
        return ("The accepted candidate passed independent local review and proof. "
                "No delivered commit, publication, merge or durable final receipt "
                "has been confirmed.")
    return ("The accepted candidate's changed product tree matches commit " +
            verified["delivered_commit"] + " on " +
            verified["destination_ref"] + " (" + verified["method"] +
            "). The checkpoint and independent review/proof were checked against "
            "the same agreement and candidate. This verifies the landed-code "
            "mapping, not remote receipt publication. Next: #47 must reconcile "
            "authorization and publish/read back the durable completion receipt.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("validate", "preview"):
        command = commands.add_parser(name)
        command.add_argument("record", help="saved Delivery Record v1 JSON")
        command.add_argument("--checkpoint", help="exact existing #82 checkpoint JSON")
        if name == "validate":
            command.add_argument("--artifacts", help="local compact artifacts, for legacy local-only validation")
        else:
            for field in ("method", "repository", "destination-ref", "before", "after", "confirmed-at"):
                command.add_argument("--" + field, required=True)
            command.add_argument("--pull-request")
            command.add_argument("--pr-head")
            command.add_argument("--merged-at")
    args = parser.parse_args(argv)
    try:
        root = Path(fs.git(Path(args.repo), "rev-parse", "--show-toplevel").decode().strip())
        record = json.loads(Path(args.record).read_bytes())
        checkpoint = Path(args.checkpoint).read_bytes() if args.checkpoint else None
        if args.action == "preview":
            _need(checkpoint is not None, "landed-code preview requires a portable checkpoint")
            value = preview(root, record, checkpoint=checkpoint, method=args.method,
                            repository=args.repository, destination_ref=args.destination_ref,
                            before=args.before, after=args.after, confirmed_at=args.confirmed_at,
                            pull_request=args.pull_request, pr_head=args.pr_head, merged_at=args.merged_at)
            print(json.dumps({"record": value, "validation": validate(root, value, checkpoint=checkpoint),
                              "published": False}, indent=2, ensure_ascii=False))
        else:
            result = validate(root, record, checkpoint=checkpoint,
                              artifact_directory=args.artifacts)
            print(json.dumps({"validation": result, "explanation": render(record, result)},
                             indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as error:
        print("p2p delivery record: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
