import { HttpErrorResponse } from '@angular/common/http';
import type { OnDestroy, OnInit } from '@angular/core';
import { Component, computed, effect, inject, signal } from '@angular/core';
import { IonContent } from '@ionic/angular';
import { firstValueFrom } from 'rxjs';

import { HeaderComponent } from './components/header/header.component';
import { TankVisualizationComponent } from './components/tank-visualization/tank-visualization.component';

import { TANK_SPECS } from '@/core/consts/tank.const';
import type { DeviceStatus } from '@/core/models/device-config.models';
import type { PumpMode } from '@/core/models/tank.models';
import { DeviceApiService } from '@/core/services/device-api.service';
import { TankSelectionService } from '@/core/services/tank-selection.service';
import { ZardSonnerService } from '@/shared/components/sonner';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.css'],
  imports: [IonContent, TankVisualizationComponent, HeaderComponent],
})
export class HomePage implements OnInit, OnDestroy {
  private readonly api = inject(DeviceApiService);
  private readonly sonner = inject(ZardSonnerService);
  private readonly tankSelection = inject(TankSelectionService);
  private statusRefreshTimer: ReturnType<typeof setTimeout> | null = null;
  private initialized = false;
  private lastRefreshVersion = 0;
  private readonly refreshEffect = effect(() => {
    const version = this.api.statusRefreshVersion();
    if (this.initialized && version !== this.lastRefreshVersion) {
      this.lastRefreshVersion = version;
      void this.loadStatus();
    }
  });

  readonly selectedModel = this.tankSelection.selectedModel;
  readonly deviceStatus = signal<DeviceStatus | null>(null);
  readonly loadingStatus = signal(false);
  readonly statusError = signal<string | null>(null);
  readonly savingPump = signal(false);
  readonly showAnnotations = signal(true);
  readonly waterLevelPct = computed(() => this.deviceStatus()?.nivel_atual_pct ?? 0);
  readonly pumpMode = computed<PumpMode>(() => (this.deviceStatus()?.bomba_ligada ? 'PUMPING' : 'STANDBY'));
  readonly manualControl = computed(() => this.deviceStatus()?.configuracoes.controle_manual ?? false);
  readonly tankCapacity = computed(
    () => this.deviceStatus()?.configuracoes.capacidade_litros ?? this.selectedModel().cap,
  );

  readonly alarm = computed(() => {
    const status = this.deviceStatus();
    if (!status) return null;

    const level = status.nivel_atual_pct;
    if (level <= 20) {
      return {
        message: 'Reservatório em nível crítico baixo. Volume abaixo de 20%.',
        className: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
      };
    }
    if (level >= 92) {
      return {
        message: 'Nível máximo próximo. O reservatório atingiu 92% da coluna.',
        className: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
      };
    }
    return null;
  });

  ngOnInit(): void {
    this.initialized = true;
    this.lastRefreshVersion = this.api.statusRefreshVersion();
    void this.loadStatus();
  }

  ngOnDestroy(): void {
    this.clearStatusRefresh();
  }

  toggleAnnotations(): void {
    this.showAnnotations.update((visible) => !visible);
  }

  async loadStatus(): Promise<void> {
    if (this.loadingStatus()) return;

    this.clearStatusRefresh();
    this.loadingStatus.set(true);
    this.statusError.set(null);

    try {
      const status = await firstValueFrom(this.api.getStatus());
      this.deviceStatus.set(status);

      const matchingModel = TANK_SPECS.find((spec) => spec.cap === status.configuracoes.capacidade_litros);
      if (matchingModel) this.selectedModel.set(matchingModel);

      this.scheduleStatusRefresh(status.configuracoes.delay_leitura_s);
    } catch (error: unknown) {
      this.statusError.set(this.getErrorMessage(error));
      this.scheduleStatusRefresh(5);
    } finally {
      this.loadingStatus.set(false);
    }
  }

  async handlePumpAction(mode: PumpMode): Promise<void> {
    const currentStatus = this.deviceStatus();
    if (!currentStatus || this.savingPump()) return;

    const ligar = mode === 'PUMPING';
    if (currentStatus.bomba_ligada === ligar) return;

    this.savingPump.set(true);
    try {
      await firstValueFrom(this.api.updateBomba({ ligar }));
      await this.loadStatus();
      this.sonner.success(ligar ? 'Comando para ligar a bomba enviado.' : 'Comando para desligar a bomba enviado.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível acionar a bomba.', {
        description: this.getErrorMessage(error),
      });
    } finally {
      this.savingPump.set(false);
    }
  }

  private scheduleStatusRefresh(delaySeconds: number): void {
    const delay = Number.isFinite(delaySeconds) && delaySeconds > 0 ? delaySeconds : 5;
    this.statusRefreshTimer = setTimeout(() => void this.loadStatus(), delay * 1000);
  }

  private clearStatusRefresh(): void {
    if (this.statusRefreshTimer !== null) {
      clearTimeout(this.statusRefreshTimer);
      this.statusRefreshTimer = null;
    }
  }

  private getErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse && error.status === 0) {
      return 'Não foi possível conectar ao dispositivo. Verifique a conexão de rede.';
    }
    if (error instanceof HttpErrorResponse) {
      return `A API respondeu com o erro ${error.status}.`;
    }
    return 'Ocorreu um erro inesperado ao comunicar com o dispositivo.';
  }
}
