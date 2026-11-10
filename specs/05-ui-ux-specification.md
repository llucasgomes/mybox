# 05. Especificação de UI/UX

## Navegação

- `/home` é a tela inicial.
- `/config` contém configurações do dispositivo.
- O cabeçalho oferece navegação entre as telas.
- A rota raiz redireciona para `/home`.

## Tela inicial

- A visualização mostra reservatório, nível percentual, volume calculado e capacidade.
- O estado visual da bomba deriva de `bomba_ligada`.
- O controle de bomba envia uma solicitação e deve ficar desabilitado enquanto está
  carregando ou salvando.
- Alertas são derivados do nível recebido pela API.
- A atualização automática deve respeitar `delay_leitura_s`.
- Erro de leitura deve ser visível e não pode parecer um status válido.

## Tela de configuração

- Capacidade: seletor em litros e ação explícita para salvar.
- Parâmetros: controles numéricos com faixa/validação e salvamento por campo.
- Wi-Fi: campos SSID e senha enviados juntos.
- A senha remota existente não deve ser carregada para um campo ou exposta na interface.
- Exibir estados de carregamento, salvamento, validação e falha.

## Padrões visuais e acessibilidade

- Reutilizar Zard e classes Tailwind existentes.
- Botões devem ter nome acessível, foco visível e estado desabilitado coerente.
- Mensagens de erro devem ser anunciadas (`role="alert"`); estados de carregamento/status
  devem ser apresentados semanticamente.
- Usar unidades explícitas (L, %, cm, s) e formatação localizada em pt-BR.
- Não usar interação puramente visual para indicar que uma gravação ocorreu: mostrar
  confirmação ou erro real da API.

## Melhorias sujeitas a especificação

Não assumir suporte a tema escuro/claro, múltiplos reservatórios, offline, idiomas
adicionais ou personalização de limites sem requisitos e critérios de aceite.
