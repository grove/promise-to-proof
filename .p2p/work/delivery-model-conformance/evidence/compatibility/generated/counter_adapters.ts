import { execFileSync } from 'node:child_process';
import { CounterRole, CounterModel } from './counter_interfaces.js';

function invoke(action: string): number {
  const result = execFileSync('python3', ['operation.py', action], {encoding: 'utf8'});
  const state = JSON.parse(result);
  console.log(JSON.stringify({subprocess: action, observed: state}));
  return state.value;
}
export class CounterRoleAdapter implements CounterRole {
  async actionInc(): Promise<void> { invoke('Inc'); }
  async actionDec(): Promise<void> { invoke('Dec'); }
  async actionGet(): Promise<number> {
    const value = invoke('Get');
    return process.env.BAD_OBSERVATION === '1' ? value + 1 : value;
  }
}
export class CounterModelAdapter implements CounterModel {
  private role = new CounterRoleAdapter();
  async init(): Promise<void> { invoke('Init'); }
  async getRoles(): Promise<Map<string, CounterRole>> { return new Map([['Counter#0', this.role]]); }
  async cleanup(): Promise<void> {}
  async cleanupAll(): Promise<void> {}
}
export function newCounterModel(): CounterModel { return new CounterModelAdapter(); }
export function getTestOptions(): Record<string, number> {
  return {'max-seq-runs': 10, 'max-parallel-runs': 0, 'max-actions': 10};
}
