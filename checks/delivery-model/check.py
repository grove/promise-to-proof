#!/usr/bin/env python3
"""Run finite FizzBee safety, reachability and mutation checks; stdlib only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
VERSION = "v0.5.3"
REPOSITORY_REVISION = "41bebc726a8cc71c1d2f22d822ade006f4e78121"
# Official macOS arm64 release. Refuse an unrecognized binary, including latest.
PIN = {
    "fizz": "8e8f905864b1781a3960f44fb654fc4455ef633e45556adf3fae586b652480a6",
    "fizzbee": "f0746cd47d13f268835fc0d8c1e85ec28a8ad0034e080cff6ec49a26304c1bf3",
    "parser/parser_bin": "54eb014c1cc7cb874faccfe22e4f93e78dbb3d633a9f496d71e21f5997a8f3fd",
}
SCENARIOS = ["initial", "repair", "exhausted", "identity", "text", "candidate", "base",
             "report-lost", "report-access", "evidence-lost", "evidence-access"]
WITNESSES = {name: name for name in SCENARIOS}
WITNESSES.update({"restart": "repair", "missing-stage": "initial",
                  "report-save": "initial", "report-read": "initial",
                  "evidence-absent": "initial", "evidence-save": "initial", "evidence-read": "initial"})
MUTATIONS = {"identity": "SameReports", "text": "CurrentText", "candidate": "CurrentCandidate",
             "base": "ComparisonBase", "repair-reset": "RepairBound"}
MUTATIONS.update({name: "DurableReports" for name in ["report-save", "report-read", "report-lost", "report-access"]})
MUTATIONS.update({name: "DurableEvidence" for name in ["evidence-absent", "evidence-save", "evidence-read", "evidence-lost", "evidence-access"]})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nodes(path):
    """v0.5.3 node files: protobuf repeated field 1, length-delimited JSON."""
    data = path.read_bytes()
    offset = 0
    while offset < len(data):
        if data[offset] != 10:
            raise ValueError("unexpected FizzBee node encoding")
        offset += 1
        length = shift = 0
        while True:
            byte = data[offset]
            offset += 1
            length |= (byte & 127) << shift
            if byte < 128:
                break
            shift += 7
        end = offset + length
        yield json.loads(data[offset:end])
        offset = end


def check_trace(trace, kind, name, property_name):
    """Check observed terminal facts, independently of the completion guard."""
    state = trace[-1]["Node"]["state"]
    if kind == "witness":
        expected = {"initial": "complete", "repair": "complete", "restart": "complete", "exhausted": "repair-exhausted"}.get(name, name)
        assert state["outcome"] == expected, (name, state)
        if name in ["repair", "restart", "exhausted"]:
            assert state["repairs_actual"] == 1
            assert any(step["Name"] == "Repair" for step in trace)
        if name in ["restart", "exhausted"]:
            assert state["restarted"]
        if name == "text":
            assert state["revision"] == "v1" and state["contract"] == 1
        if expected == "complete":
            assert state["reports"] == state["evidence"] == [3, 3]
            assert all(b[:2] == [state["contract"], state["candidate"]] for b in state["bindings"])
            assert state["bindings"][0][2] == state["base"]
    else:
        if property_name == "RepairBound":
            assert state["repairs_actual"] == 2 and state["restarted"]
        else:
            assert state["outcome"] == "complete"
            if property_name == "SameReports":
                assert state["bindings"][0][:2] != state["bindings"][1][:2]
            elif property_name == "CurrentText":
                assert any(b[0] != state["contract"] for b in state["bindings"])
                assert state["revision"] == "v1"
            elif property_name == "CurrentCandidate":
                assert any(b[1] != state["candidate"] for b in state["bindings"])
            elif property_name == "ComparisonBase":
                assert state["bindings"][0][2] != state["base"]
            else:
                artifact = "reports" if property_name == "DurableReports" else "evidence"
                missing = {"absent": 0, "save": 1, "read": 2, "lost": 4, "access": 5}[name.split("-")[1]]
                assert missing in state[artifact], (name, state)


def run(fizz, output, scratch, kind, name, scenario, mutation="none", witness="none"):
    target = output / (kind + "-" + name)
    target.mkdir()
    source = (HERE / "delivery.fizz").read_text()
    for key, value in [("SCENARIO", scenario), ("MUTATION", mutation), ("WITNESS", witness)]:
        source, count = re.subn(r'^' + key + r' = "[^"]*"$', key + " = " + json.dumps(value), source, flags=re.M)
        assert count == 1
    model = scratch / (target.name + ".fizz")
    model.write_text(source)
    (target / "model.fizz").write_text(source)
    graph = scratch / target.name
    command = [str(fizz), "--output-dir", str(graph), str(model)]
    started = time.monotonic()
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    elapsed = time.monotonic() - started
    (target / "output.txt").write_text(result.stdout)
    observation = {"kind": kind, "name": name, "scenario": scenario, "mutation": mutation,
                   "command": command, "returncode": result.returncode, "seconds": round(elapsed, 3),
                   "model_sha256": digest(target / "model.fizz")}
    # fizz's shell wrapper returns 0 even on invariant failure. Read the verdict.
    assert result.returncode == 0, result.stdout
    if kind == "baseline":
        assert "PASSED: Model checker completed successfully" in result.stdout and "FAILED:" not in result.stdout, result.stdout
        files = list(graph.glob("nodes_*.pb"))
        assert files, "missing exploration graph"
        maximum = count = 0
        outcomes = set()
        actions = set()
        for file in files:
            for node in nodes(file):
                count += 1
                maximum = max(maximum, node["stats"]["totalActions"])
                outcomes.add(node["state"]["outcome"])
                actions.update(node["stats"]["counts"])
        assert maximum < 64, "action cutoff reached; exploration incomplete"
        observation.update(nodes=count, max_actions_observed=maximum, outcomes=sorted(outcomes), actions=sorted(actions),
                           result="complete finite safety exploration")
    else:
        expected = "Witness" if kind == "witness" else MUTATIONS[name]
        assert "FAILED: Model checker failed. Invariant:  " + expected in result.stdout, result.stdout
        trace = json.loads((graph / "error-graph.json").read_text())
        check_trace(trace, kind, name, expected)
        (target / "trace.json").write_text(json.dumps(trace, indent=2) + "\n")
        (target / "trace.txt").write_text("\n".join(step["Name"] + " " + json.dumps(step["Node"]["state"], sort_keys=True) for step in trace) + "\n")
        observation.update(property=expected, steps=len(trace) - 1, result="expected counterexample" if kind == "mutation" else "reachable witness")
    (target / "observation.json").write_text(json.dumps(observation, indent=2) + "\n")
    print(f'{target.name}: {observation["result"]} ({elapsed:.2f}s)', flush=True)
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fizz", default=os.environ.get("FIZZBEE", "fizz"), help="path to pinned fizz executable")
    parser.add_argument("--output-dir", type=Path, help="new evidence directory; default OS temporary directory")
    args = parser.parse_args()
    fizz = Path(shutil.which(args.fizz) or args.fizz).resolve()
    for relative, expected in PIN.items():
        actual = digest(fizz.parent / relative)
        if actual != expected:
            parser.error(f"unrecognized {relative}: expected FizzBee {VERSION} macOS arm64 SHA-256 {expected}, got {actual}")
    output = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="p2p-delivery-model-evidence-"))
    if args.output_dir:
        output.mkdir(parents=True, exist_ok=False) # Never overwrite prior evidence.
    print(f"Evidence: {output}", flush=True)
    summary = {"fizzbee": VERSION, "binary_sha256": PIN, "repository_revision": REPOSITORY_REVISION,
               "environment": platform.platform(), "python": platform.python_version(), "bounds": "single fault family; 64 actions; one restart; one repair",
               "model_sha256": digest(HERE / "delivery.fizz"), "runs": []}
    try:
        with tempfile.TemporaryDirectory(prefix="p2p-delivery-model-run-") as temp:
            scratch = Path(temp)
            for name in SCENARIOS:
                summary["runs"].append(run(fizz, output, scratch, "baseline", name, name))
            for name, scenario in WITNESSES.items():
                summary["runs"].append(run(fizz, output, scratch, "witness", name, scenario, witness=name))
            for name in MUTATIONS:
                scenario = "exhausted" if name == "repair-reset" else name if name in SCENARIOS else "initial"
                summary["runs"].append(run(fizz, output, scratch, "mutation", name, scenario, mutation=name))
        summary["result"] = "PASS"
    except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        summary["result"] = "FAIL"
        summary["error"] = str(error)
        raise
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f'PASS: {len(summary["runs"])} checks. Model evidence only; no live-agent conformance claim.')


if __name__ == "__main__":
    main()
