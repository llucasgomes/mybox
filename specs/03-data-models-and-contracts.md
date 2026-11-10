# 03. Modelos de Dados e Contratos TypeScript

Os modelos da aplicação estão definidos em `src/app/core/models/`. Os campos abaixo
reproduzem os tipos atuais; os tipos TypeScript não validam automaticamente o JSON recebido
em runtime.

## Configuração do dispositivo

| Campo | Tipo | Significado |
|---|---|---|
| `capacidade_litros` | `number` | Capacidade nominal da caixa em litros |
| `gatilho_ligar_pct` | `number` | Percentual de acionamento da bomba |
| `gatilho_desligar_pct` | `number` | Percentual de desligamento da bomba |
| `dist_sensor_cheio_cm` | `number` | Leitura/distância associada ao reservatório cheio |
| `dist_sensor_vazio_cm` | `number` | Leitura/distância associada ao reservatório vazio |
| `delay_leitura_s` | `number` | Intervalo de leitura em segundos |
| `SSID_ROTEADOR` | `string` | SSID configurado no dispositivo |
| `SENHA_ROTEADOR` | `string` | Senha configurada no dispositivo |

## Status

```ts
interface DeviceStatus {
  bomba_ligada: boolean;
  configuracoes: DeviceConfiguration;
  nivel_atual_pct: number;
}
```

O cliente usa `nivel_atual_pct` para calcular litros e `configuracoes` para capacidade,
gatilhos e período de atualização.

## Comando da bomba

```ts
interface LigarBomba {
  ligar: boolean;
}
```

Valores `true` e `false` representam pedido de ligar e desligar. O formato efetivo aceito
deve permanecer alinhado com o firmware.

## Caixa catalogada

`TankSpec` contém capacidade (`cap`), código e dimensões (`a` a `e`, `lidCode`) usados pela
visualização técnica. O catálogo está em `TANK_SPECS`. A escolha persistida na API é
`capacidade_litros`; a seleção visual deve corresponder a essa capacidade quando houver
correspondência no catálogo.

## Validação de fronteira

Ao alterar ou expandir o contrato:

1. Confirme nomes, nulabilidade, unidade e limites no backend/firmware.
2. Atualize modelos e documentação juntos.
3. Considere validação em runtime para respostas HTTP; uma interface TypeScript não valida
   dados externos.
4. Nunca registre ou exiba `SENHA_ROTEADOR` em logs ou na UI.
