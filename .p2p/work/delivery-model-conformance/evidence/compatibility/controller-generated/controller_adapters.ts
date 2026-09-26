import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { ControllerRole, ControllerModel } from './controller_interfaces.js';
export class ControllerRoleAdapter implements ControllerRole {
  async actionStatus(): Promise<string> {
    const command = ['../../../../skills/productivity/deliver-issue/scripts/p2p_delivery.py', '--repo', resolve('controller-fixture'), 'status', 'work/tiny.md'];
    const result = spawnSync('python3', command, {encoding: 'utf8'});
    if (result.error) throw result.error;
    const state = JSON.parse(result.stdout);
    console.log(JSON.stringify({command: ['python3', ...command], exit: result.status, observed: state}));
    if (result.status !== 1 || state.blocker !== 'no delivery invocation exists') throw new Error('Unexpected fixture observation');
    return process.env.BAD_OBSERVATION === '1' ? 'STATUS_WRONG' : state.status;
  }
}
export class ControllerModelAdapter implements ControllerModel {
  private role = new ControllerRoleAdapter();
  async init(): Promise<void> {}
  async getRoles(): Promise<Map<string, ControllerRole>> { return new Map([['Controller#0', this.role]]); }
  async cleanup(): Promise<void> {}
  async cleanupAll(): Promise<void> {}
}
export function newControllerModel(): ControllerModel { return new ControllerModelAdapter(); }
export function getTestOptions(): Record<string, number> {
  return {'max-seq-runs': 1, 'max-parallel-runs': 0, 'max-actions': 3};
}
