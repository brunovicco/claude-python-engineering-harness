# Política de segurança

*[English](SECURITY.md)*

Este repositório distribui as partes sensíveis à segurança de uma configuração do Claude Code: hooks
que bloqueiam comandos destrutivos e acesso a arquivos sensíveis, varredura de conteúdo com formato
de segredo, guarda-corpos de governança MCP, e um quality gate apoiado em Bandit/pip-audit para
projetos gerados. Trate vulnerabilidades neste repositório - não só nas aplicações que ele gera -
como problemas de segurança que valem um reporte responsável.

## O que está no escopo

- Contornos dos hooks `PreToolUse`/`PostToolUse` em `template/.claude/hooks/` e
  `plugin/python-engineering-harness/scripts/` (`protect_sensitive_files.py`, `validate_bash.py`,
  `guard_mcp.py`, `scan_secrets.py`) - por exemplo, um padrão de comando destrutivo, um caminho
  sensível ou um formato de segredo que deveria ser bloqueado e não é.
- Erros de lógica em `template/scripts/validate_architecture.py` ou
  `template/scripts/validate_mcp_config.py` que deixem passar uma configuração ou dependência que
  viola a regra do gate.
- Comportamento do `bootstrap.py` que possa escrever fora do diretório de destino pretendido,
  sobrescrever arquivos em `--merge` de um jeito não descrito pelo fluxo documentado de conflito
  `.harness-new`, ou de alguma forma anular a garantia de "nunca sobrescrever arquivos existentes".
- Lacunas na governança MCP: qualquer coisa que permita a um servidor configurado exfiltrar
  segredos passando pelo `guard_mcp.py`, ou que permita a uma chamada de ferramenta que muta estado
  pular o requisito de confirmação documentado em `template/docs/MCP.md`.
- Qualquer controle documentado em `docs/ENTERPRISE_ROLLOUT.md` (aplicação de allowlist/denylist,
  exemplos de managed settings) que não se comporte como descrito.

## O que está fora do escopo

- Vulnerabilidades em dependências de terceiros trazidas para um projeto *já bootstrapado*
  (`fastapi`, `sqlalchemy`, etc.) - reporte essas rio acima; o `pip-audit` no quality gate do
  projeto gerado é o mecanismo de detecção pretendido, não esta política.
- Achados que exigem que o operador já tenha desativado um controle de segurança documentado (por
  exemplo, um modo `bypassPermissions` explicitamente aprovado, ou um hook editado à mão que remove
  uma checagem) - o modelo de ameaça do harness assume que seus controles nativos permanecem em
  vigor.
- Problemas no próprio Claude Code, em contraste com a configuração que este harness faz dele -
  reporte esses pelos canais oficiais do Claude Code à Anthropic.

## Como reportar uma vulnerabilidade

Este projeto ainda não publica um endereço de contato de segurança dedicado. Até que um seja
adicionado aqui:

- Se este repositório estiver hospedado no GitHub, use o relatório privado de vulnerabilidades do
  GitHub (aba **Security** -> **Report a vulnerability**), para que o relato não fique visível
  publicamente antes de uma correção sair.
- Caso contrário, contate o dono do repositório listado em "Recommended ownership" em
  `docs/ENTERPRISE_ROLLOUT.md` (engenharia de plataforma para hooks e baseline de CI, segurança para
  caminhos bloqueados e padrões de segredo) pelo canal interno da sua organização.

Por favor, não abra uma issue pública para uma suspeita de vulnerabilidade antes que os
mantenedores tenham tido a chance de avaliar e, quando cabível, lançar uma correção.

## O que incluir

- O hook, script ou flag do bootstrap específico envolvido, e a entrada ou comando exato que
  deveria ter sido bloqueado e não foi (ou que produziu um comportamento de escrita inesperado).
- Se o problema se reproduz em `template/`, `plugin/python-engineering-harness/`, ou em ambos.
- Sua versão do Claude Code e sistema operacional, já que a correspondência de hooks e o
  comportamento do shell podem diferir entre plataformas (o `template/README.md` e o `README.md`
  deste repositório citam macOS/Linux/WSL como o conjunto suportado para a configuração padrão de
  hooks).

## Divulgação

Como isto é uma distribuição de template/plugin em vez de um serviço hospedado, não há dados de
usuário a proteger diretamente, mas um bypass de hook não detectado ou uma falha de gate poderia se
propagar para todo projeto que fizer bootstrap a partir de uma versão afetada. Por favor, dê tempo
para uma correção e uma entrada em `CHANGELOG.md` (veja a convenção de seção `Security` já usada lá)
antes de uma divulgação pública.
