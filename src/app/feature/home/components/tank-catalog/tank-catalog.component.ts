import { Component, input, output } from '@angular/core';

import type { TankSpec } from '@/core/models/tank.models';

@Component({
  selector: 'app-tank-catalog',
  templateUrl: './tank-catalog.component.html',
  styleUrl: './tank-catalog.component.css',
})
export class TankCatalogComponent {
  readonly specs = input.required<TankSpec[]>();
  readonly selectedModel = input.required<TankSpec>();
  readonly searchQuery = input.required<string>();

  readonly modelSelected = output<TankSpec>();
  readonly searchChanged = output<string>();

  formatNumber(value: number, decimals = 0): string {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }

  onSearchChange(event: Event): void {
    const target = event.target;
    if (target instanceof HTMLInputElement) this.searchChanged.emit(target.value);
  }
}
