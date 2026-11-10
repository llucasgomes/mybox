# 02. Arquitetura Técnica e Stack

## Stack observada

| Camada | Tecnologia/padrão |
|---|---|
| Aplicação | Angular 22, TypeScript estrito e componentes standalone |
| Web/mobile | Ionic Angular 9 e Capacitor 8 |
| Rotas | Angular Router, carregamento lazy das páginas |
| Estado de UI | Angular Signals (`signal`, `computed`) |
| API | `HttpClient` Angular e RxJS |
| Interface | Tailwind CSS v4, componentes compartilhados Zard e `@ng-icons/lucide` |
| Testes | Vitest pelo builder Angular; Playwright para E2E |
| Qualidade | ESLint, Prettier e TypeScript |

Confirme versões em `package.json`; não atualize versões neste documento sem atualizar
também o manifesto do projeto.

## Organização existente

- `src/app/core/models/`: tipos centrais do dispositivo e reservatório.
- `src/app/core/services/`: integração HTTP e seleção compartilhada da caixa.
- `src/app/core/consts/`: catálogo local de capacidades/modelos.
- `src/app/feature/home/`: supervisão e visualização.
- `src/app/feature/config/`: formulários de configuração.
- `src/app/shared/components/`: componentes reutilizáveis, incluindo componentes Zard.
- `src/app/shared/core/` e `src/app/shared/utils/`: internacionalização, infraestrutura de UI
  e utilitários.
- `src/environments/`: configuração por ambiente.

## Diretrizes de implementação

- Manter telas e componentes standalone e carregar páginas sob demanda pelo router.
- Injetar dependências com `inject()` e usar tipos explícitos nos contratos.
- Usar Signals para estado síncrono da interface; não copiar estado da API sem uma razão.
- Centralizar comunicação com o dispositivo em `DeviceApiService`.
- Tratar falhas de rede e respostas HTTP sem substituir erros por sucesso silencioso.
- Evitar que dados locais simulados sejam apresentados como telemetria real.
- Respeitar os componentes e estilos compartilhados em vez de reimplementar controles.
- Manter valores de ambiente configuráveis por build; desenvolvimento e produção não devem
  depender acidentalmente do endereço local de teste.

## Limites e decisões a confirmar

- A API atualmente é configurada por `src/environments`; a estratégia de configuração
  segura para produção ainda deve ser definida.
- Não há contrato de autenticação ou autorização documentado no repositório.
- Não se deve inferir suporte do firmware a atualizações parciais, persistência imediata
  ou respostas específicas sem confirmar com o backend.
