# Atualizando um projeto já bootstrapado

*[English](UPGRADING.md)*

O `bootstrap.py` tem um modo bem documentado para um projeto novo (renderizar tudo) e um
para aplicar o harness a um repositório existente sem destruí-lo (`--merge`). Nenhum dos dois modos
hoje distingue "este repositório nunca viu o harness" de "este repositório foi bootstrapado a partir
de uma versão mais antiga do harness e precisa se atualizar." Este documento descreve como lidar com
o segundo caso com o que existe hoje, e destaca a lacuna explicitamente em vez de sugerir um caminho
mais suave do que a ferramenta de fato oferece.

## Não existe um registro de versão no projeto bootstrapado

O `bootstrap.py` não grava um arquivo marcador registrando de qual commit, tag ou versão do
`CHANGELOG.md` do harness um projeto foi renderizado. Se você ainda não rastreia isso por conta
própria, não há como perguntar à ferramenta "em que versão eu estou." Comece a fazer isso agora se
mantém mais de um projeto bootstrapado:

- Registre o hash de commit ou a tag do harness no próprio `README.md` do projeto bootstrapado, ou
  em um comentário onde você invoca o `bootstrap.py` (por exemplo, seu script de provisionamento), e
  atualize isso toda vez que reaplicar o harness.
- Se você mantém muitos repositórios bootstrapados, rastreie "versão do harness por repositório" como
  faria com qualquer outra versão de dependência compartilhada - da mesma forma que a seção
  "Metrics" de `docs/ENTERPRISE_ROLLOUT.md` recomenda rastrear "repositórios e desenvolvedores em
  cada versão do harness."

Sem isso, o melhor que você pode fazer é comparar com a versão do harness que você *acredita* ter
usado como ponto de partida, ou tratar toda atualização como "comparar com o harness mais recente e
aceitar tudo que parecer intencional."

## Procedimento de atualização

1. **Leia o `CHANGELOG.md`** desde a versão registrada como ponto de partida (ou desde a entrada mais
   antiga, se não rastreada) até a versão para a qual você está atualizando. Cada entrada explica
   *por que* a mudança foi feita - use isso para julgar se ela se aplica ao seu projeto (por
   exemplo, uma mudança restrita à governança MCP não importa se você nunca habilitou `.mcp.json`).
2. **Rode o bootstrap novamente em modo `--merge`** contra o seu repositório existente:

   ```bash
   python3 bootstrap.py --name <projeto-existente> --package <pacote_existente> \
     --target /caminho/para/repo-existente --merge
   ```

   O `--merge` nunca sobrescreve um arquivo que já existe no destino. Todo arquivo do harness que
   difere do que já está no seu repositório é escrito ao lado do original com o sufixo
   `.harness-new`.
3. **Revise cada arquivo `.harness-new` individualmente.** Para cada um, decida se a diferença é:
   - uma melhoria do lado do harness que você deveria adotar (substitua seu arquivo, ou faça o merge
     manual das partes que se aplicam) - a maioria das mudanças em
     `template/.claude/hooks/*.py`, `template/.claude/rules/*.md` e `template/scripts/*.py` cai
     aqui, já que carregam a lógica de aplicação de fato;
   - uma customização específica do projeto que você fez deliberadamente (mantenha sua versão,
     apague o arquivo `.harness-new`) - isso é esperado para comandos de execução em `AGENTS.md`,
     layout do pacote em `src/`, nomes de camada em `.claude/rules/architecture.md`, e qualquer
     outra coisa que a lista "Customizações recomendadas" do `README.md` cita como algo que você
     deve ajustar por projeto;
   - uma mesclagem que precisa de reconciliação manual porque os dois lados mudaram (arquivos de
     regra que você estendeu localmente, ou listas de permissão em `.claude/settings.json` que você
     ampliou) - faça isso à mão, não há merge de três vias aqui.
4. **Apague os arquivos `.harness-new`** depois de resolvidos; não os deixe versionados.
5. **Rode novamente o próprio quality gate do projeto** (`/quality-gate`, ou a sequência de comandos
   em `template/docs/DEVELOPMENT.md`) antes de mesclar a atualização - uma mudança de hook ou
   validador pode revelar uma violação que seu projeto vinha passando silenciosamente (por exemplo,
   um import agora proibido em `validate_architecture.py`, ou um campo de configuração MCP agora
   exigido).
6. **Atualize seu registro de versão** (veja acima) para a versão do harness que você acabou de
   mesclar.

## O que costuma exigir mais atenção

Com base no formato de entradas passadas do `CHANGELOG.md`, estas categorias são as mais propensas a
exigir ação além de uma simples substituição de arquivo:

- **Scripts de hook** (`.claude/hooks/*.py` / `scripts/*.py` do plugin): quase sempre seguro adotar
  por completo, já que usam só a standard library e não são feitos para customização por projeto -
  exceto a lista de caminhos bloqueados do `protect_sensitive_files.py` e os padrões de
  allow/deny do `validate_bash.py`, se você adicionou entradas específicas do projeto.
- **`scripts/validate_architecture.py`**: se você adicionou suas próprias camadas ou entradas de
  dependência proibida, faça merge manual em vez de substituir.
- **Permissões de `.claude/settings.json`**: quase sempre específicas do projeto; trate a versão do
  harness como uma sugestão para reconciliar, não como uma substituição.
- **Campos de frontmatter de agente/skill** (`effort`, `memory`, `isolation`, `model`): campos novos
  introduzidos em uma atualização do harness (veja `CHANGELOG.md` 0.3.0 para `memory: project` e
  `isolation: worktree` como exemplos) são opt-in e não se aplicam retroativamente às cópias do seu
  projeto a menos que você adote a versão `.harness-new`.
- **`CLAUDE.md` / `AGENTS.md`**: esses arquivos carregam tanto padrões gerais do harness quanto fatos
  específicos do projeto no mesmo arquivo, então uma substituição mecânica apagaria suas
  customizações - sempre faça merge manual.

## Se você mantém muitos projetos bootstrapados

Trate isso como qualquer atualização de dependência compartilhada: atualize primeiro um projeto
piloto de baixo risco, confirme que o quality gate e o comportamento dos hooks não foram afetados, e
só então aplique as mesmas decisões de resolução de `.harness-new` ao restante. A seção de
governança de mudanças de `docs/ENTERPRISE_ROLLOUT.md` descreve o que um release do harness deveria
carregar (versão semântica, notas de release e migração, evidência de teste, declaração de
compatibilidade, instruções de rollback) - use essa checklist para decidir se uma dada versão do
harness vale a atualização antes de começar.
