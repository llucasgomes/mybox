import { Component, input, output } from '@angular/core';

import type { DeviceStatus } from '@/core/models/device-config.models';

@Component({
  selector: 'app-tank-controls',
  templateUrl: './tank-controls.component.html',
  styleUrl: './tank-controls.component.css',
})
export class TankControlsComponent {
  readonly deviceStatus = input.required<DeviceStatus | null>();
  readonly loading = input.required<boolean>();
  readonly error = input.required<string | null>();
  readonly refresh = output<void>();

  formatNumber(value: number, decimals = 0): string {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }
}
