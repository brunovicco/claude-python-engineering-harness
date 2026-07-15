# Atualizando um projeto já bootstrapado

*[English](UPGRADING.md)*

O harness 0.5.0 ou posterior registra versão, perfil, Python, estado da origem, hashes e modos dos
arquivos gerados em `.harness.json`. Projetos antigos não têm baseline; por isso, a primeira
atualização deles continua exigindo reconciliação manual.

## Procedimento

1. Leia o `CHANGELOG.md` desde a versão registrada no projeto até a versão desejada.
2. Aplique o template atual sem sobrescrever arquivos existentes:

   ```bash
   python3 bootstrap.py --name <projeto-existente> --package <pacote_existente> \
     --target /caminho/para/repo-existente --merge
   ```

3. O bootstrap atualiza automaticamente arquivos cujo hash atual corresponde ao manifesto anterior.
   Revise cada `.harness-new` gerado. Se esse nome já existir, o bootstrap usará um sufixo
   numerado, como `.harness-new.2`.
4. Adote correções do harness, preserve customizações intencionais do projeto e reconcilie
   manualmente arquivos alterados nos dois lados. Apague os conflitos já resolvidos.
5. Execute `python3 bootstrap.py --target /caminho/para/repo-existente --check` e depois o
   `scripts/quality_gate.py` do projeto. O bootstrap atualiza a versão registrada ao renderizar.

Se a versão de origem não foi registrada, compare com o harness atual e trate cada diferença como
uma decisão manual de migração.

## Arquivos que exigem mais atenção

- `.claude/hooks/` e scripts de hook do plugin carregam controles e normalmente devem ser
  atualizados.
- Raízes e boundaries específicos pertencem ao `pyproject.toml`; mantenha o validator genérico
  sincronizado com o harness.
- Permissões em `.claude/settings.json` são específicas do projeto e devem ser reconciliadas, não
  substituídas.
- `CLAUDE.md` e `AGENTS.md` combinam padrões compartilhados com dados do projeto e exigem merge
  manual.
- Novos campos de frontmatter de agentes e skills não são aplicados retroativamente sem adotar o
  novo arquivo.

Para vários repositórios, atualize primeiro um piloto de baixo risco, valide os hooks e o quality
gate e então reutilize as decisões de migração revisadas. Consulte `ENTERPRISE_ROLLOUT.pt-BR.md`
para orientações de rollout, ownership e rollback.
