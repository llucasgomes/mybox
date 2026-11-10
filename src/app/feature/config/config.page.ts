import { HttpErrorResponse } from '@angular/common/http';
import type { OnInit } from '@angular/core';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { IonContent } from '@ionic/angular';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideLoaderCircle, lucideSave, lucideWifi } from '@ng-icons/lucide';
import { firstValueFrom } from 'rxjs';

import { TANK_SPECS } from '@/core/consts/tank.const';
import type { DeviceConfiguration, DeviceStatus } from '@/core/models/device-config.models';
import { DeviceApiService } from '@/core/services/device-api.service';
import { TankSelectionService } from '@/core/services/tank-selection.service';
import { ZardButtonComponent } from '@/shared/components/button';
import { ZardCardImports } from '@/shared/components/card';
import { ZardInputComponent } from '@/shared/components/input';
import { ZardSonnerService } from '@/shared/components/sonner';

interface ConfigurationField {
  key: ConfigurationFieldKey;
  label: string;
  description: string;
  min: number;
  max?: number;
  unit: string;
}

type ConfigurationFieldKey = Exclude<
  keyof DeviceConfiguration,
  | 'capacidade_litros'
  | 'controle_manual'
  | 'SSID_ROTEADOR'
  | 'SENHA_ROTEADOR'
  | 'IP_FIXO'
  | 'MASCARA'
  | 'GATEWAY'
  | 'DNS'
  | 'NOME_AP'
>;

@Component({
  selector: 'app-config',
  templateUrl: './config.page.html',
  imports: [
    IonContent,
    ReactiveFormsModule,
    RouterLink,
    NgIcon,
    ZardButtonComponent,
    ZardInputComponent,
    ...ZardCardImports,
  ],
  viewProviders: [
    provideIcons({
      lucideLoaderCircle,
      lucideSave,
      lucideWifi,
    }),
  ],
})
export class ConfigPage implements OnInit {
  private readonly formBuilder = inject(FormBuilder).nonNullable;
  private readonly api = inject(DeviceApiService);
  private readonly sonner = inject(ZardSonnerService);
  private readonly tankSelection = inject(TankSelectionService);

  readonly tankSpecs = TANK_SPECS;
  readonly selectedTank = this.tankSelection.selectedModel;
  readonly apiBaseUrlInput = signal(this.api.apiBaseUrl);
  readonly apiTokenInput = signal(this.api.apiToken);
  readonly deviceStatus = signal<DeviceStatus | null>(null);
  readonly testedConnection = signal<DeviceStatus | null>(null);
  readonly testingConnection = signal(false);
  readonly savingControlMode = signal(false);
  readonly manualControl = signal(false);
  readonly canConfirmNetwork = computed(() => {
    const status = this.testedConnection();
    if (!status?.rede?.ip_sta || !status.rede.ap_ativo) return false;
    try {
      return new URL(this.apiBaseUrlInput()).hostname === status.rede.ip_sta;
    } catch {
      return false;
    }
  });
  readonly pendingTankCapacity = signal<number | null>(null);
  readonly configurationFields: ConfigurationField[] = [
    {
      key: 'gatilho_ligar_pct',
      label: 'Ligar a bomba',
      description: 'Nível percentual que aciona a bomba.',
      min: 0,
      max: 100,
      unit: '%',
    },
    {
      key: 'gatilho_desligar_pct',
      label: 'Desligar a bomba',
      description: 'Nível percentual que desliga a bomba.',
      min: 0,
      max: 100,
      unit: '%',
    },
    {
      key: 'dist_sensor_cheio_cm',
      label: 'Distância do sensor com reservatório cheio',
      description: 'Distância medida pelo sensor quando o reservatório está cheio.',
      min: 1,
      unit: 'cm',
    },
    {
      key: 'dist_sensor_vazio_cm',
      label: 'Distância do sensor com reservatório vazio',
      description: 'Distância medida pelo sensor quando o reservatório está vazio.',
      min: 1,
      unit: 'cm',
    },
    {
      key: 'delay_leitura_s',
      label: 'Intervalo entre leituras',
      description: 'Tempo entre leituras consecutivas do sensor.',
      min: 1,
      unit: 's',
    },
  ];

  readonly configurationForm = this.formBuilder.group({
    gatilho_desligar_pct: [100, [Validators.required, Validators.min(0), Validators.max(100)]],
    dist_sensor_vazio_cm: [120, [Validators.required, Validators.min(1)]],
    delay_leitura_s: [1, [Validators.required, Validators.min(1)]],
    dist_sensor_cheio_cm: [20, [Validators.required, Validators.min(1)]],
    gatilho_ligar_pct: [30, [Validators.required, Validators.min(0), Validators.max(100)]],
  });

  readonly wifiForm = this.formBuilder.group({
    ssid: ['', [Validators.required]],
    senha: ['', [Validators.required]],
  });

  readonly loadingStatus = signal(false);
  readonly savingFields = signal(new Set<ConfigurationFieldKey>());
  readonly savingTank = signal(false);
  readonly savingWifi = signal(false);
  readonly statusError = signal<string | null>(null);

  ngOnInit(): void {
    void this.loadCurrentConfiguration();
  }

  isSavingField(field: ConfigurationFieldKey): boolean {
    return this.savingFields().has(field);
  }

  selectTank(event: Event): void {
    const target = event.target;
    if (!(target instanceof HTMLSelectElement)) return;

    const capacity = Number(target.value);
    if (this.tankSpecs.some((tank) => tank.cap === capacity)) {
      this.pendingTankCapacity.set(capacity === this.selectedTank().cap ? null : capacity);
    }
  }

  async saveTankCapacity(): Promise<void> {
    const capacity = this.pendingTankCapacity();
    const selected = this.tankSpecs.find((spec) => spec.cap === capacity);
    if (!selected || this.savingTank()) return;

    this.savingTank.set(true);
    try {
      await firstValueFrom(this.api.updateConfiguration({ capacidade_litros: selected.cap }));
      this.tankSelection.selectedModel.set(selected);
      this.pendingTankCapacity.set(null);
      this.sonner.success('Tamanho da caixa d’água atualizado.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível atualizar o tamanho da caixa d’água.', {
        description: this.getErrorMessage(error, 'salvar o tamanho da caixa d’água'),
      });
    } finally {
      this.savingTank.set(false);
    }
  }

  async loadCurrentConfiguration(): Promise<void> {
    this.loadingStatus.set(true);
    this.statusError.set(null);

    try {
      const status = await firstValueFrom(this.api.getStatus());
      this.applyStatus(status);
    } catch (error: unknown) {
      this.statusError.set(this.getErrorMessage(error, 'carregar as configurações'));
    } finally {
      this.loadingStatus.set(false);
    }
  }

  async saveConfigurationField(field: ConfigurationFieldKey): Promise<void> {
    const control = this.configurationForm.controls[field];
    control.markAsTouched();
    if (control.invalid || this.isSavingField(field)) return;

    this.savingFields.update((current) => new Set(current).add(field));
    try {
      const update: Partial<DeviceConfiguration> = { [field]: control.value };
      await firstValueFrom(this.api.updateConfiguration(update));
      this.sonner.success('Configuração salva.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível salvar a configuração.', {
        description: this.getErrorMessage(error, 'salvar a configuração'),
      });
    } finally {
      this.savingFields.update((current) => {
        const next = new Set(current);
        next.delete(field);
        return next;
      });
    }
  }

  async saveWifi(): Promise<void> {
    this.wifiForm.markAllAsTouched();
    if (this.wifiForm.invalid || this.savingWifi()) return;

    this.savingWifi.set(true);
    try {
      await firstValueFrom(this.api.updateWifi(this.wifiForm.getRawValue()));
      this.sonner.success('Wi-Fi enviado. O ponto de acesso ficará ativo até você confirmar o novo IP.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível atualizar o Wi-Fi.', {
        description: this.getErrorMessage(error, 'salvar os dados do Wi-Fi'),
      });
    } finally {
      this.savingWifi.set(false);
    }
  }

  updateApiBaseUrl(event: Event): void {
    const target = event.target;
    if (target instanceof HTMLInputElement) {
      this.apiBaseUrlInput.set(target.value);
      this.testedConnection.set(null);
    }
  }

  updateApiToken(event: Event): void {
    const target = event.target;
    if (target instanceof HTMLInputElement) {
      this.apiTokenInput.set(target.value);
      this.testedConnection.set(null);
    }
  }

  async testAndSaveConnection(): Promise<void> {
    if (this.testingConnection()) return;

    this.testingConnection.set(true);
    this.statusError.set(null);
    try {
      const baseUrl = this.api.normalizeApiBaseUrl(this.apiBaseUrlInput());
      const token = this.apiTokenInput().trim();
      const status = await firstValueFrom(this.api.getStatusAt(baseUrl, token));
      this.api.saveConnection(baseUrl, token);
      this.apiBaseUrlInput.set(baseUrl);
      this.apiTokenInput.set(token);
      this.applyStatus(status);
      this.testedConnection.set(status);
      this.sonner.success('Conexão validada e salva neste dispositivo.');
    } catch (error: unknown) {
      this.testedConnection.set(null);
      this.sonner.error('Não foi possível validar a conexão com a API.', {
        description: this.getErrorMessage(error, 'validar o endereço e a chave da API'),
      });
    } finally {
      this.testingConnection.set(false);
    }
  }

  async confirmNetworkTransition(): Promise<void> {
    if (!this.canConfirmNetwork() || this.testingConnection()) return;

    this.testingConnection.set(true);
    try {
      await firstValueFrom(this.api.confirmarRede());
      this.testedConnection.update((status) =>
        status?.rede ? { ...status, rede: { ...status.rede, ap_ativo: false, ip_ap: null } } : status,
      );
      this.sonner.success('Troca confirmada. O ponto de acesso foi desativado.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível confirmar a nova conexão.', {
        description: this.getErrorMessage(error, 'confirmar a conexão pelo Wi-Fi do roteador'),
      });
    } finally {
      this.testingConnection.set(false);
    }
  }

  async setManualControl(event: Event): Promise<void> {
    const target = event.target;
    if (!(target instanceof HTMLInputElement) || this.savingControlMode()) return;

    const previousValue = this.manualControl();
    const nextValue = target.checked;
    this.manualControl.set(nextValue);
    this.savingControlMode.set(true);
    try {
      await firstValueFrom(this.api.updateConfiguration({ controle_manual: nextValue }));
      this.sonner.success(
        nextValue
          ? 'Modo manual ativado. A bomba pode ser comandada pela tela inicial.'
          : 'Modo automático ativado. Os gatilhos controlam a bomba.',
      );
    } catch (error: unknown) {
      this.manualControl.set(previousValue);
      this.sonner.error('Não foi possível alterar o modo de controle.', {
        description: this.getErrorMessage(error, 'salvar o modo de controle'),
      });
    } finally {
      this.savingControlMode.set(false);
    }
  }

  private getErrorMessage(error: unknown, action: string): string {
    if (error instanceof HttpErrorResponse && error.status === 0) {
      return `Não foi possível ${action}. Verifique se o celular está conectado ao Wi-Fi do dispositivo.`;
    }
    if (error instanceof HttpErrorResponse) {
      return `A API respondeu com o erro ${error.status}.`;
    }
    if (error instanceof Error) return error.message;
    return `Ocorreu um erro inesperado ao tentar ${action}.`;
  }

  private applyStatus(status: DeviceStatus): void {
    this.deviceStatus.set(status);
    this.configurationForm.patchValue(status.configuracoes);
    this.manualControl.set(status.configuracoes.controle_manual);
    const selectedTank = this.tankSpecs.find((tank) => tank.cap === status.configuracoes.capacidade_litros);
    if (selectedTank) {
      this.tankSelection.selectedModel.set(selectedTank);
      this.pendingTankCapacity.set(null);
    }
  }
}
