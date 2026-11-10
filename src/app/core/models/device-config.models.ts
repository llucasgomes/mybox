export interface DeviceConfiguration {
  capacidade_litros: number;
  gatilho_desligar_pct: number;
  dist_sensor_vazio_cm: number;
  delay_leitura_s: number;
  dist_sensor_cheio_cm: number;
  gatilho_ligar_pct: number;
  SSID_ROTEADOR: string;
  SENHA_ROTEADOR: string;
}

export interface DeviceStatus {
  bomba_ligada: boolean;
  configuracoes: DeviceConfiguration;
  nivel_atual_pct: number;
}

export interface LigarBomba {
  ligar: boolean;
}
