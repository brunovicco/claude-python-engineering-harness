# Como contribuir

*[English](CONTRIBUTING.md)*

Este repositório não tem código de aplicação próprio para compilar ou testar. O que você está
alterando é `template/` (renderizado em outros repositórios por `bootstrap.py`) e
`plugin/python-engineering-harness/` (carregado diretamente como plugin do Claude Code). Valide as
mudanças exercitando essas saídas, não rodando uma suíte de testes na raiz - ela não existe.

## Antes de começar

Leia `CLAUDE.md` primeiro. Ele explica por que os dois mecanismos de distribuição existem, que
precisam ser mantidos em sincronia deliberadamente, e quais arquivos são a fonte da verdade para
padrões de engenharia (`template/CLAUDE.md`) versus comportamento específico do Claude Code
(`template/AGENTS.md`).

## Alterando `template/`

1. Edite os arquivos em `template/`. Lembre-se que `{{PROJECT_NAME}}`, `{{PACKAGE_NAME}}`,
   `{{PYTHON_VERSION}}` e `{{RUFF_TARGET_VERSION}}` são substituídos tanto no conteúdo quanto nos
   caminhos dos arquivos; qualquer arquivo novo precisa ficar livre de tokens fora de
   `src/{{PACKAGE_NAME}}/`.
2. Renderize o template e rode o próprio quality gate dele:

   ```bash
   python3 bootstrap.py --name smoke-test --package smoke_test --target /tmp/smoke-test \
     --git-init --lock
   cd /tmp/smoke-test
   uv run ruff check .
   uv run ruff format --check .
   uv run python scripts/validate_architecture.py
   uv run python scripts/validate_mcp_config.py
   uv run mypy src tests
   uv run pytest
   uv run bandit -c pyproject.toml -r src
   uv run pip-audit
   ```

3. Se você mudou um nome de camada ou a direção de dependência permitida em
   `template/docs/ARCHITECTURE.md` ou `template/CLAUDE.md`, atualize
   `LAYERS`/`FORBIDDEN_LOCAL`/`FORBIDDEN_EXTERNAL` em `template/scripts/validate_architecture.py`
   para acompanhar - o validador é o que de fato impõe a regra, não a prosa.
4. Se você mudou padrões de engenharia em `template/CLAUDE.md`, verifique se algum arquivo
   condicional por caminho em `template/.claude/rules/` elabora a mesma seção e precisa da mesma
   atualização.

## Alterando `plugin/python-engineering-harness/`

1. Agentes e skills são copiados quase como estão a partir de `template/.claude/`; os scripts de
   hook ficam em `plugin/python-engineering-harness/scripts/` e referenciam `${CLAUDE_PLUGIN_ROOT}`
   em vez de `${CLAUDE_PROJECT_DIR}`. Ao mudar o comportamento de um hook em uma árvore, replique a
   mudança equivalente na outra.
2. Valide:

   ```bash
   python3 -m py_compile plugin/python-engineering-harness/scripts/*.py
   claude plugin validate ./plugin/python-engineering-harness
   claude --plugin-dir ./plugin/python-engineering-harness
   ```

   `claude plugin validate` exige a CLI do Claude Code; se ela não estiver disponível no seu
   ambiente, diga isso explicitamente em vez de reportar o plugin como validado.

## Mantendo as duas árvores em sincronia

Uma mudança em padrões de engenharia ou comportamento de hook geralmente precisa acontecer tanto em
`template/` quanto em `plugin/python-engineering-harness/`. Antes de abrir um PR, compare os
diretórios de agentes/skills equivalentes para os arquivos que você tocou e confirme que a
divergência é só a esperada (substituição de token de caminho, `${CLAUDE_PLUGIN_ROOT}` vs.
`${CLAUDE_PROJECT_DIR}`).

## Versionamento e changelog

- Adicione uma entrada em `CHANGELOG.md` em `Added`/`Changed`/`Security` conforme apropriado.
  Explique *por que* a mudança foi feita, não só o que mudou - futuros contribuidores e as revisões
  de `SOURCES.md` dependem desse raciocínio.
- Se a mudança afeta o plugin, incremente `version` em
  `plugin/python-engineering-harness/.claude-plugin/plugin.json` e em `.claude-plugin/marketplace.json`
  juntos, e mantenha os dois iguais ao título que você adicionou em `CHANGELOG.md`.
- Se uma mudança em `template/` ou no comportamento do projeto gerado exige que um repositório já
  bootstrapado faça algo para adotá-la (não apenas re-renderizar), adicione uma nota de migração -
  veja `docs/UPGRADING.md`.
- Atualize `VALIDATION.md` quando você de fato exercitar algo novo (um caminho de renderização, um
  caso de hook, uma etapa do quality gate) ou quando uma cobertura antes dependente de ambiente
  passar a ser exercitável. Não afirme que uma verificação passou se você não a rodou nesta
  passagem.
- Se uma decisão de design tem base em um trecho específico da documentação oficial do Claude Code,
  uv ou Ruff, adicione o endereço da fonte e a data de revisão em `SOURCES.md`.

## Idioma da documentação

Inglês é canônico para toda a documentação e código. Docs na raiz do repositório (`README.md`,
`SOURCES.md`, `VALIDATION.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/ENTERPRISE_ROLLOUT.md`,
`docs/UPGRADING.md`) adicionalmente têm um irmão `<nome>.pt-BR.md`, com link cruzado no topo dos dois
arquivos. `CHANGELOG.md` e tudo sob `template/`/`plugin/` (código, regras, agentes, skills)
permanecem só em inglês. Ao editar um arquivo que tem um irmão `.pt-BR.md`, atualize os dois no mesmo
PR, a tradução não deve divergir do original em inglês.

## Checklist de pull request

- [ ] Alterou `template/` e `plugin/` juntos onde a mudança deveria valer para os dois.
- [ ] Renderizou `template/` (ou rodou `claude plugin validate`) e reportou o resultado real, não um
      resultado assumido.
- [ ] Atualizou `CHANGELOG.md`, e `VALIDATION.md` se a cobertura de validação mudou.
- [ ] Incrementou os campos `version` de plugin/marketplace juntos, se o plugin mudou.
- [ ] Atualizou o irmão `.pt-BR.md` correspondente para qualquer doc de raiz que você tocou.
- [ ] Adicionou uma nota de migração em `docs/UPGRADING.md` se repositórios já bootstrapados
      precisam fazer algo além de re-renderizar para adotar a mudança.
