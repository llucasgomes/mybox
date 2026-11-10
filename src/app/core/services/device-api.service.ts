import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { tap, type Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import type { DeviceConfiguration, DeviceStatus, LigarBomba } from '../models/device-config.models';

@Injectable({ providedIn: 'root' })
export class DeviceApiService {
  private readonly http = inject(HttpClient);
  private readonly storageUrlKey = 'mybox.deviceApiUrl';
  private readonly storageTokenKey = 'mybox.deviceApiToken';
  readonly statusRefreshVersion = signal(0);

  get apiBaseUrl(): string {
    return localStorage.getItem(this.storageUrlKey) ?? environment.apiBaseUrl;
  }

  get apiToken(): string {
    return localStorage.getItem(this.storageTokenKey) ?? '';
  }

  normalizeApiBaseUrl(value: string): string {
    const url = new URL(value.trim());
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
      throw new Error('Informe um endereço HTTP ou HTTPS válido, sem credenciais, parâmetros ou fragmento.');
    }

    const path = url.pathname.replace(/\/+$/, '') || '/api';
    if (path !== '/api') {
      throw new Error('O endereço deve apontar para a raiz da API, terminando em /api.');
    }
    return `${url.origin}${path}`;
  }

  saveConnection(apiBaseUrl: string, apiToken: string): void {
    localStorage.setItem(this.storageUrlKey, this.normalizeApiBaseUrl(apiBaseUrl));
    localStorage.setItem(this.storageTokenKey, apiToken.trim());
  }

  getStatus(): Observable<DeviceStatus> {
    return this.getStatusAt(this.apiBaseUrl, this.apiToken);
  }

  getStatusAt(apiBaseUrl: string, apiToken: string): Observable<DeviceStatus> {
    const baseUrl = this.normalizeApiBaseUrl(apiBaseUrl);
    return this.http.get<DeviceStatus>(`${baseUrl}/status`, { headers: this.createHeaders(apiToken) });
  }

  updateConfiguration(configuration: Partial<DeviceConfiguration>): Observable<unknown> {
    return this.http
      .post<unknown>(`${this.apiBaseUrl}/config`, configuration, {
        headers: this.createHeaders(this.apiToken),
      })
      .pipe(tap(() => this.statusRefreshVersion.update((version) => version + 1)));
  }

  updateWifi(credentials: { ssid: string; senha: string }): Observable<unknown> {
    return this.updateConfiguration({
      SSID_ROTEADOR: credentials.ssid,
      SENHA_ROTEADOR: credentials.senha,
    });
  }

  updateBomba(credentials: LigarBomba): Observable<unknown> {
    return this.http.post<unknown>(`${this.apiBaseUrl}/bomba`, credentials, {
      headers: this.createHeaders(this.apiToken),
    });
  }

  confirmarRede(): Observable<unknown> {
    return this.http.post<unknown>(
      `${this.apiBaseUrl}/rede/confirmar`,
      { confirmar: true },
      { headers: this.createHeaders(this.apiToken) },
    );
  }

  private createHeaders(apiToken: string): HttpHeaders {
    return apiToken ? new HttpHeaders({ 'X-API-Key': apiToken }) : new HttpHeaders();
  }
}
