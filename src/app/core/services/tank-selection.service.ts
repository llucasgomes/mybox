import { Injectable, signal } from '@angular/core';

import { TANK_SPECS } from '@/core/consts/tank.const';
import type { TankSpec } from '@/core/models/tank.models';

@Injectable({ providedIn: 'root' })
export class TankSelectionService {
  readonly selectedModel = signal<TankSpec>(TANK_SPECS[6]);
}
