import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import type { Observable } from 'rxjs';

import { environment } from '../../../environments/environment.prod';
import type { DeviceConfiguration, DeviceStatus, LigarBomba } from '../models/device-config.models';

@Injectable({ providedIn: 'root' })
export class DeviceApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiBaseUrl}/`;

  getStatus(): Observable<DeviceStatus> {
    return this.http.get<DeviceStatus>(`${this.apiUrl}status`);
  }

  updateConfiguration(configuration: Partial<DeviceConfiguration>): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}config`, configuration);
  }

  updateWifi(credentials: { ssid: string; senha: string }): Observable<void> {
    return this.updateConfiguration({
      SSID_ROTEADOR: credentials.ssid,
      SENHA_ROTEADOR: credentials.senha,
    });
  }

  updateBomba(credentials: LigarBomba): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}bomba`, credentials);
  }
}
