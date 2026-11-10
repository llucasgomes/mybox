import { Component, computed, input, output } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucidePause, lucidePlay } from '@ng-icons/lucide';

import type { PumpMode, TankSpec } from '@/core/models/tank.models';
import { ZardButtonComponent } from '@/shared/components/button';

@Component({
  selector: 'app-tank-visualization',
  templateUrl: './tank-visualization.component.html',
  styleUrl: './tank-visualization.component.css',
  imports: [NgIcon, ZardButtonComponent],
  viewProviders: [provideIcons({ lucidePause, lucidePlay })],
})
export class TankVisualizationComponent {
  readonly model = input.required<TankSpec>();
  readonly capacity = input.required<number>();
  readonly level = input.required<number>();
  readonly pumpMode = input.required<PumpMode>();
  readonly manualControl = input.required<boolean>();
  readonly canControl = input.required<boolean>();
  readonly pumpBusy = input.required<boolean>();
  readonly showAnnotations = input.required<boolean>();
  readonly annotationsToggle = output<void>();
  readonly pumpAction = output<'PUMPING' | 'STANDBY'>();

  readonly liters = computed(() => Math.round((this.level() / 100) * this.capacity()));
  readonly height = computed(() => this.formatNumber((this.level() / 100) * this.model().b, 2));
  readonly waterTranslateY = computed(() => 278 - 186 * (this.level() / 100));

  formatNumber(value: number, decimals = 0): string {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }
}
