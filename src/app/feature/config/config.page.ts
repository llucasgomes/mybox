import { HttpErrorResponse } from '@angular/common/http';
import type { OnInit } from '@angular/core';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { IonContent } from '@ionic/angular';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideLoaderCircle, lucideSave, lucideWifi } from '@ng-icons/lucide';
import { firstValueFrom } from 'rxjs';

import { TANK_SPECS } from '@/core/consts/tank.const';
import type { DeviceConfiguration } from '@/core/models/device-config.models';
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
  'capacidade_litros' | 'SSID_ROTEADOR' | 'SENHA_ROTEADOR'
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

    const selected = this.tankSpecs.find((spec) => spec.cap === Number(target.value));
    if (selected) this.tankSelection.selectedModel.set(selected);
  }

  async loadCurrentConfiguration(): Promise<void> {
    this.loadingStatus.set(true);
    this.statusError.set(null);

    try {
      const status = await firstValueFrom(this.api.getStatus());
      this.configurationForm.patchValue(status.configuracoes);
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
      this.sonner.success('Dados do Wi-Fi enviados para o dispositivo.');
    } catch (error: unknown) {
      this.sonner.error('Não foi possível atualizar o Wi-Fi.', {
        description: this.getErrorMessage(error, 'salvar os dados do Wi-Fi'),
      });
    } finally {
      this.savingWifi.set(false);
    }
  }

  private getErrorMessage(error: unknown, action: string): string {
    if (error instanceof HttpErrorResponse && error.status === 0) {
      return `Não foi possível ${action}. Verifique se o celular está conectado ao Wi-Fi do dispositivo.`;
    }
    if (error instanceof HttpErrorResponse) {
      return `A API respondeu com o erro ${error.status}.`;
    }
    return `Ocorreu um erro inesperado ao tentar ${action}.`;
  }
}
