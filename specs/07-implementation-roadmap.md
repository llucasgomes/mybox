# 07. Roadmap de Implementação

Este roadmap prioriza consolidar o supervisório existente. Itens são propostas de trabalho,
não promessas de comportamento já disponível.

## Marco 1 — Contratos e feedback confiáveis

- [ ] Confirmar com firmware payloads, unidades, limites e respostas das três rotas.
- [ ] Documentar esquemas de erro e política de timeout/retry aprovada.
- [ ] Validar respostas de `/status` em runtime e definir fallback para campos ausentes.
- [ ] Confirmar ambiente de produção e evitar endereço de desenvolvimento embutido nele.

## Marco 2 — Cobertura automatizada funcional

- [ ] Criar testes unitários de `DeviceApiService`.
- [ ] Testar leitura de status, cálculo de litros, polling e comando da bomba.
- [ ] Testar seleção/salvamento de capacidade, parâmetros e credenciais Wi-Fi sem expor senha.
- [ ] Substituir a asserção E2E do scaffold por um fluxo Mybox com API interceptada.

## Marco 3 — Experiência de operação

- [ ] Revisar telas em navegador e Android em estados de carregamento, erro e rede lenta.
- [ ] Revisar contraste, acessibilidade por teclado/leitor e nomes de controles.
- [ ] Confirmar com produto se histórico, multi-dispositivo ou operação offline são necessários.

## Critérios de conclusão de cada marco

- Critérios de aceite específicos atendidos.
- Contratos e decisões atualizados nas especificações correspondentes.
- Build e validações aplicáveis executados.
- Limitações e itens não realizados reportados explicitamente.
