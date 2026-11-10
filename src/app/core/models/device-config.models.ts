export interface DeviceConfiguration {
  capacidade_litros: number;
  gatilho_desligar_pct: number;
  dist_sensor_vazio_cm: number;
  delay_leitura_s: number;
  dist_sensor_cheio_cm: number;
  gatilho_ligar_pct: number;
  controle_manual: boolean;
  SSID_ROTEADOR: string;
  SENHA_ROTEADOR: string;
  IP_FIXO?: string;
  MASCARA?: string;
  GATEWAY?: string;
  DNS?: string;
  NOME_AP?: string;
}

export interface DeviceNetworkStatus {
  ip_ap: string | null;
  ip_sta: string | null;
  ap_ativo: boolean;
}

export interface DeviceStatus {
  bomba_ligada: boolean;
  configuracoes: DeviceConfiguration;
  nivel_atual_pct: number;
  rede?: DeviceNetworkStatus;
}

export interface LigarBomba {
  ligar: boolean;
}
