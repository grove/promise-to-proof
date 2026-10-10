#!/usr/bin/env python3
"""Deterministic, recoverable human-first issue acceptance proposal (stdlib only)."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from p2p_filesystem import bindings, safe, work_slug

COLUMNS = ("ID", "Source", "Requirement", "Boundaries / counterexamples",
           "Seam", "Oracle", "Planned evidence", "Plan state")
MARKER = "p2p-acceptance-proposal:v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    text = data.decode("utf-8")
    if not text.endswith("\n") or "\r" in text:
        raise ValueError("contract must have canonical LF with final newline")
    def one(pattern, label):
        found = re.findall(pattern, text, re.M)
        if len(found) != 1 or not found[0].strip():
            raise ValueError("missing or ambiguous " + label)
        return found[0].strip()
    revision = one(r"^Contract revision: (.+)$", "revision")
    if not re.fullmatch(r"v[1-9][0-9]*", revision):
        raise ValueError("invalid revision")
    outcome = one(r"^Intended outcome: (.+)$", "outcome")
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            if current in sections:
                raise ValueError("duplicate section " + current)
            sections[current] = []
        elif current:
            sections[current].append(line)
    def cells(line):
        if not line.startswith("|") or not line.endswith("|"):
            raise ValueError("invalid matrix row")
        return [part.strip().replace(r"\|", "|") for part in re.split(r"(?<!\\)\|", line)[1:-1]]
    table = [x.strip() for x in sections.get("Acceptance matrix", []) if x.strip()]
    if len(table) < 3 or tuple(cells(table[0])) != COLUMNS:
        raise ValueError("invalid acceptance matrix")
    if not all(re.fullmatch(r":?-{3,}:?", x) for x in cells(table[1])):
        raise ValueError("missing table separator")
    rows, ids = [], set()
    for line in table[2:]:
        values = cells(line)
        if len(values) != len(COLUMNS) or not all(values):
            raise ValueError("incomplete requirement row")
        row = dict(zip(COLUMNS, values))
        rid = row["ID"]
        if not re.fullmatch(r"[A-Za-z][\w.-]*", rid) or rid in ids:
            raise ValueError("duplicate/invalid requirement ID")
        if row["Plan state"] not in ("planned", "gap"):
            raise ValueError("invalid requirement plan state")
        ids.add(rid)
        rows.append(row)
    lists = {}
    for name in ("Unresolved gaps", "Open questions", "Out of scope"):
        if name not in sections:
            raise ValueError("missing " + name)
        entries = []
        for line in sections[name]:
            if not line.strip():
                continue
            if re.match(r"^[-*] ", line):
                entries.append(line[2:].strip())
            elif line.startswith((" ", "\t")) and entries:
                entries[-1] += " " + line.strip()
            else:
                raise ValueError("unrenderable " + name)
        if not entries or not all(entries):
            raise ValueError("missing " + name)
        lists[name] = [] if len(entries) == 1 and entries[0].lower() == "none" else entries
    metadata = {}
    for label in ("Source", "Source attribution", "Parent", "Parent snapshot", "Contribution", "Prerequisites"):
        match = re.findall(r"^" + re.escape(label) + r": (.+)$", text, re.M)
        if len(match) > 1:
            raise ValueError("ambiguous " + label)
        metadata[label] = match[0].strip() if match else None
    return revision, outcome, rows, lists, metadata


def recovery(body):
    marker = re.search(r"^<!-- " + MARKER + r":([a-z0-9-]+):(v[1-9][0-9]*):([0-9a-f]{64}) -->$", body, re.M)
    if not marker or body.count("<!-- " + MARKER + ":") != 1:
        raise ValueError("missing/ambiguous proposal identity")
    def block(name, language):
        hit = re.search(r"<!-- " + name + r" -->\n(?P<fence>`{3,})" + language +
                        r"\n(?P<data>.*?)(?P=fence)(?=\n)", body, re.S)
        if not hit or body.count("<!-- " + name + " -->") != 1:
            raise ValueError("missing/ambiguous " + name)
        return hit.group("data")
    raw = block("p2p-exact-contract", "markdown").encode()
    if digest(raw) != marker[3] or parse(raw)[0] != marker[2]:
        raise ValueError("exact agreement hash or revision mismatch")
    snapshot = json.loads(block("p2p-binding-snapshot", "json"))
    if set(snapshot) != {"schema", "files"} or snapshot["schema"] != "p2p-binding-snapshot/v1":
        raise ValueError("invalid source snapshot")
    work = ".p2p/work/" + marker[1] + "/contract.md"
    restored = {work: raw}
    for item in snapshot["files"]:
        if set(item) != {"path", "sha256", "base64"}:
            raise ValueError("invalid binding record")
        path = item["path"]
        if (not isinstance(path, str) or path.startswith("/") or
                any(x in ("", "..", ".git") for x in path.split("/")) or path in restored):
            raise ValueError("unsafe/duplicate binding")
        value = base64.b64decode(item["base64"], validate=True)
        if digest(value) != item["sha256"]:
            raise ValueError("binding hash mismatch")
        restored[path] = value
    if render(work, raw, snapshot["files"], check=False) != body:
        raise ValueError("visible promises differ from canonical agreement")
    return restored


def render(work, raw, sources, check=True):
    revision, outcome, rows, lists, metadata = parse(raw)
    sha = digest(raw)
    lines = [f"<!-- {MARKER}:{work_slug(work)}:{revision}:{sha} -->", "",
             "## Proposed agreement", "", outcome, "",
             "This is a proposal; publication is not approval.", "",
             "## What will change and how we will check it", ""]
    for row in rows:
        lines += [f"**{row['ID']}. {row['Requirement']}**", "",
                  f"- Source promise: {row['Source']}",
                  f"- What stays unchanged / important limits: {row['Boundaries / counterexamples']}",
                  f"- Check: {row['Planned evidence']} — expected: {row['Oracle']}",
                  f"- Testable through: {row['Seam']}",
                  f"- Plan state: {row['Plan state']}", ""]
    present = [(k, v) for k, v in metadata.items() if v and v.lower() != "none"]
    if present:
        lines += ["## Source, parent and prerequisites", ""]
        lines += [f"- {k}: {v}" for k, v in present]
        lines += [""]
    lines += ["## Not part of this change", ""]
    lines += [f"- {x}" for x in lists["Out of scope"]] or ["- No explicit exclusions."]
    lines += ["", "## Open decisions or verification gaps", ""]
    for name in ("Open questions", "Unresolved gaps"):
        if lists[name]:
            lines += [f"**{name}**", ""]
            lines += [f"- {x}" for x in lists[name]]
            lines += [""]
    if not lists["Open questions"] and not lists["Unresolved gaps"]:
        lines += ["No unresolved items are listed.", ""]
    lines += ["## Your decision", ""]
    if (any(row["Plan state"] == "gap" for row in rows)
            or lists["Open questions"] or lists["Unresolved gaps"]):
        lines += ["**Not ready for approval.** Resolve the missing checks or open decisions and publish a revised exact proposal.", ""]
    else:
        lines += [f"To approve this exact proposal, reply: **I approve contract {revision}, SHA-256 `{sha}`.**",
                  "Approval binds to the exact canonical contract, not the readable presentation.", ""]
    snapshot = json.dumps({"schema": "p2p-binding-snapshot/v1", "files": sources},
                          ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    exact = raw.decode()
    fence = "`" * max(3, max((len(x) for x in re.findall(r"`+", exact)), default=0) + 1)
    other = "`" * max(3, max((len(x) for x in re.findall(r"`+", snapshot)), default=0) + 1)
    body = ("\n".join(lines) + "\n<details>\n<summary>Technical details: exact agreement and recovery</summary>\n\n" +
            f"Contract: `{work}`; revision: `{revision}`; SHA-256: `{sha}`\n\n" +
            "<!-- p2p-exact-contract -->\n" + fence + "markdown\n" + exact + fence + "\n\n" +
            "<!-- p2p-binding-snapshot -->\n" + other + "json\n" + snapshot + other + "\n\n</details>\n")
    if len(body) > 60000:
        raise ValueError("proposal exceeds recoverable GitHub comment limit")
    if check:
        expected = {work: raw, **{x["path"]: base64.b64decode(x["base64"]) for x in sources}}
        if recovery(body) != expected:
            raise ValueError("proposal recovery/readback differs")
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output")
    parser.add_argument("--verify-comment")
    args = parser.parse_args()
    try:
        root = Path(args.repo).resolve()
        work = args.contract
        raw = safe(root, work).read_bytes()
        sources = []
        for entry in bindings(root, work, require_trackable=False):
            value = safe(root, entry["path"]).read_bytes()
            if digest(value) != entry["sha256"]:
                raise ValueError("binding source changed")
            sources.append({"path": entry["path"], "sha256": entry["sha256"],
                            "base64": base64.b64encode(value).decode()})
        body = render(work, raw, sources)
        if args.verify_comment:
            if Path(args.verify_comment).read_text(encoding="utf-8") != body:
                raise ValueError("published comment readback is not the exact proposal")
            print("VERIFIED", file=sys.stderr)
        elif args.output:
            Path(args.output).write_text(body, encoding="utf-8")
        else:
            print(body, end="")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"BLOCKED: {exc}\n")


if __name__ == "__main__":
    main()
