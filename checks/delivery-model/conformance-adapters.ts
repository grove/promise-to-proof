import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { ControllerRole, ConformanceModel } from './conformance_interfaces.js';

const scenario = process.env.P2P_MBT_CASE!;
const faults = ['stale-identity', 'mistyped-identity', 'candidate-mutated-during-verification',
  'incomplete-archive', 'late-stage-result', 'duplicate-report-write'];

function operation(name: string): string {
  const result = spawnSync(process.env.PYTHON!,
    [resolve(process.env.P2P_REPO!, 'checks/delivery-model/conformance_bridge.py'), name],
    {encoding: 'utf8', env: process.env});
  if (result.error) throw result.error;
  // Do not let MBT interpret an execution error as a disabled operation.
  if (result.status !== 0) {
    process.stderr.write(result.stderr + result.stdout);
    process.exit(2);
  }
  return result.stdout.trim();
}
export class ControllerRoleAdapter implements ControllerRole {
  // Scheduling metadata for the fixture's pause points. No expected controller
  // values live here: every enabled result comes from its output and saved files.
  private phase = 'new';
  private corrupted = false;
  private repaired = false;
  private inspected = false;
  private repeats = 0;
  async actionStart() {
    if (this.phase !== 'new') return 'DISABLED';
    const value = operation('Start');
    this.phase = ['unauthorized-before-dispatch', 'contested-dirty-file'].includes(scenario) ? 'terminal' :
      scenario === 'uncertain-launch-restart' ? 'uncertain' : 'review';
    return value;
  }
  async actionReview() {
    if (this.phase !== 'review' || scenario === 'concurrent-resume') return 'DISABLED';
    const value = operation('Review'); this.phase = 'proof'; return value;
  }
  async actionProof() {
    if (this.phase !== 'proof') return 'DISABLED';
    const value = operation('Proof'); this.phase = 'pending'; return value;
  }
  async actionCorrupt() {
    if (this.phase !== 'pending' || this.corrupted || !faults.includes(scenario)) return 'DISABLED';
    const value = operation('Corrupt'); this.corrupted = true; return value;
  }
  async actionRestart() {
    if (!['pending', 'uncertain', 'storage'].includes(this.phase) ||
        (faults.includes(scenario) && !this.corrupted)) return 'DISABLED';
    const value = operation('Restart');
    if (scenario === 'interrupted-report-storage' && this.phase !== 'storage') this.phase = 'storage';
    else if (['repair-restart-exhaustion', 'successful-repair', 'blocked-failure'].includes(scenario) && !this.repaired) {
      this.repaired = true; this.phase = 'review';
    } else this.phase = 'terminal';
    return value;
  }
  async actionInspect() {
    if (!['review', 'proof'].includes(this.phase) || this.inspected) return 'DISABLED';
    const value = operation('Inspect'); this.inspected = true; return value;
  }
  async actionResume() {
    if (this.phase !== 'terminal' || this.repeats >= 2) return 'DISABLED';
    const value = operation('Resume'); this.repeats++; return value;
  }
  async actionOverlap() {
    if (this.phase !== 'review' || scenario !== 'concurrent-resume' || this.corrupted) return 'DISABLED';
    const value = operation('Overlap'); this.corrupted = true; this.phase = 'proof'; return value;
  }
}
export class ConformanceModelAdapter implements ConformanceModel {
  private role = new ControllerRoleAdapter();
  async init() { operation('Init'); }
  async getRoles() { return new Map([['Controller#0', this.role]]); }
  async cleanup() {}
  async cleanupAll() {}
}
export function newConformanceModel(): ConformanceModel { return new ConformanceModelAdapter(); }
export function getTestOptions(): Record<string, number> {
  return {'max-seq-runs': 1, 'max-parallel-runs': 0, 'max-actions': 256};
}
