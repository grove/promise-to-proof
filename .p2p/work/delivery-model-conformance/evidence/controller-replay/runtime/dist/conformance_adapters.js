"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConformanceModelAdapter = exports.ControllerRoleAdapter = void 0;
exports.newConformanceModel = newConformanceModel;
exports.getTestOptions = getTestOptions;
const node_child_process_1 = require("node:child_process");
const node_path_1 = require("node:path");
const scenario = process.env.P2P_MBT_CASE;
const faults = ['stale-identity', 'mistyped-identity', 'candidate-mutated-during-verification',
    'incomplete-archive', 'late-stage-result', 'duplicate-report-write'];
function operation(name) {
    const result = (0, node_child_process_1.spawnSync)(process.env.PYTHON, [(0, node_path_1.resolve)(process.env.P2P_REPO, 'checks/delivery-model/conformance_bridge.py'), name], { encoding: 'utf8', env: process.env });
    if (result.error)
        throw result.error;
    // Do not let MBT interpret an execution error as a disabled operation.
    if (result.status !== 0) {
        process.stderr.write(result.stderr + result.stdout);
        process.exit(2);
    }
    return result.stdout.trim();
}
class ControllerRoleAdapter {
    // Scheduling metadata for the fixture's pause points. No expected controller
    // values live here: every enabled result comes from its output and saved files.
    phase = 'new';
    corrupted = false;
    repaired = false;
    inspected = false;
    repeats = 0;
    async actionStart() {
        if (this.phase !== 'new')
            return 'DISABLED';
        const value = operation('Start');
        this.phase = ['unauthorized-before-dispatch', 'contested-dirty-file'].includes(scenario) ? 'terminal' :
            scenario === 'uncertain-launch-restart' ? 'uncertain' : 'review';
        return value;
    }
    async actionReview() {
        if (this.phase !== 'review' || scenario === 'concurrent-resume')
            return 'DISABLED';
        const value = operation('Review');
        this.phase = 'proof';
        return value;
    }
    async actionProof() {
        if (this.phase !== 'proof')
            return 'DISABLED';
        const value = operation('Proof');
        this.phase = 'pending';
        return value;
    }
    async actionCorrupt() {
        if (this.phase !== 'pending' || this.corrupted || !faults.includes(scenario))
            return 'DISABLED';
        const value = operation('Corrupt');
        this.corrupted = true;
        return value;
    }
    async actionRestart() {
        if (!['pending', 'uncertain', 'storage'].includes(this.phase) ||
            (faults.includes(scenario) && !this.corrupted))
            return 'DISABLED';
        const value = operation('Restart');
        if (scenario === 'interrupted-report-storage' && this.phase !== 'storage')
            this.phase = 'storage';
        else if (['repair-restart-exhaustion', 'successful-repair', 'blocked-failure'].includes(scenario) && !this.repaired) {
            this.repaired = true;
            this.phase = 'review';
        }
        else
            this.phase = 'terminal';
        return value;
    }
    async actionInspect() {
        if (!['review', 'proof'].includes(this.phase) || this.inspected)
            return 'DISABLED';
        const value = operation('Inspect');
        this.inspected = true;
        return value;
    }
    async actionResume() {
        if (this.phase !== 'terminal' || this.repeats >= 2)
            return 'DISABLED';
        const value = operation('Resume');
        this.repeats++;
        return value;
    }
    async actionOverlap() {
        if (this.phase !== 'review' || scenario !== 'concurrent-resume' || this.corrupted)
            return 'DISABLED';
        const value = operation('Overlap');
        this.corrupted = true;
        this.phase = 'proof';
        return value;
    }
}
exports.ControllerRoleAdapter = ControllerRoleAdapter;
class ConformanceModelAdapter {
    role = new ControllerRoleAdapter();
    async init() { operation('Init'); }
    async getRoles() { return new Map([['Controller#0', this.role]]); }
    async cleanup() { }
    async cleanupAll() { }
}
exports.ConformanceModelAdapter = ConformanceModelAdapter;
function newConformanceModel() { return new ConformanceModelAdapter(); }
function getTestOptions() {
    return { 'max-seq-runs': 1, 'max-parallel-runs': 0, 'max-actions': 256 };
}
