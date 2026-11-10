export interface TankSpec {
  cap: number;
  code: string;
  a: number;
  b: number;
  c: number;
  d: number;
  e: number;
  lidCode: string;
}

export type PumpMode = 'STANDBY' | 'PUMPING' | 'DRAINING';

