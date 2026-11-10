import type { TankSpec } from '@/core/models/tank.models';

/**
 * Calcula o volume restante em litros com base na distância lida pelo sensor.
 *
 * @param sensorDistCm Distância atual medida pelo sensor ultrassônico (em cm)
 * @param spec Especificações da caixa selecionada (do seu TANK_SPECS)
 * @param sensorMountOffsetCm Altura extra caso o sensor esteja em um suporte acima da borda (em cm).
 *                            Se estiver montado na tampa, a referência total é spec.a * 100.
 */
export function calculateVolumeLiters(sensorDistCm: number, spec: TankSpec, sensorMountOffsetCm: number = 0): number {
  // Altura total do sensor até o fundo da caixa (em metros)
  // Usa a cota 'a' (com tampa) somada a eventual suporte externo
  const totalSensorHeightM = spec.a + sensorMountOffsetCm / 100;
  const sensorDistM = sensorDistCm / 100;

  // Altura atual da água (h)
  let h = totalSensorHeightM - sensorDistM;

  // Travas de limite físico
  if (h <= 0) return 0;
  if (h > spec.b) h = spec.b; // Não ultrapassa a borda útil

  const r1 = spec.e / 2; // Raio da base
  const r2 = spec.d / 2; // Raio do topo (sem tampa)

  // Raio da superfície da água na altura atual h
  const rh = r1 + ((r2 - r1) / spec.b) * h;

  // Volume do tronco de cone em m³
  const volumeM3 = ((Math.PI * h) / 3) * (Math.pow(r1, 2) + r1 * rh + Math.pow(rh, 2));

  // Converte para litros e arredonda
  const volumeLiters = volumeM3 * 1000;

  // Limita ao teto da capacidade nominal
  return Math.min(Math.round(volumeLiters), spec.cap);
}
