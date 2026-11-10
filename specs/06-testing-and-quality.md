# 06. Testes e Qualidade

## Ferramentas e comandos existentes

| Objetivo | Comando |
|---|---|
| Build de produção | `npm run build` |
| ESLint | `npm run eslint` |
| Typecheck E2E | `npm run typecheck:e2e` |
| Formatação | `npm run prettier -- --check` |
| Testes unitários | `npm run test:unit` |
| Testes E2E | `npm run test:e2e` |
| Conjunto de lint configurado | `npm run lint` |

O `npm run test` executa unitários e E2E. Escolha primeiro o menor comando que verifica a
alteração; execute a suíte ampla quando o escopo ou o resultado exigir.

## Cobertura esperada por camada

- **Serviços:** método HTTP, rota, payload e propagação de erro.
- **Componentes/formulários:** validação, estados desabilitados, ações e mensagens.
- **Supervisão:** mapeamento do status, cálculo de volume, polling e comando da bomba.
- **Firmware:** autenticação da API, validação de payload/configuração, modo manual/automático
  e transição de rede AP/STA.
- **E2E:** navegação e fluxos observáveis do operador, com respostas HTTP simuladas e sem
  depender de dispositivo físico.

## Estado atual dos testes

O builder Vitest está configurado, mas não foram encontrados arquivos `*.spec.ts` em
`src/` durante a criação deste guia. O E2E existente contém uma asserção de scaffold Ionic
(“Ready to create an app?”) e deve ser atualizado para validar a aplicação Mybox antes de
ser considerado cobertura funcional.

Não declarar uma área testada apenas porque o comando de teste existe. Registrar testes
adicionados, testes executados e limitações concretas.

## Checklist de qualidade

- Dados HTTP são tratados como entrada externa e validados onde necessário.
- Falhas de conexão e respostas HTTP não são ocultadas.
- Controles de hardware não são simulados como se tivessem acionado o dispositivo.
- Testes não contêm credenciais reais.
- Formatação, ESLint, typecheck e build são executados conforme o escopo.
- Alterações de UI incluem verificação de acessibilidade e estados de carregamento/erro.
