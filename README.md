# omnx-texto-tirar-cara-de-ia

Guia visual: abra o `COMO-FUNCIONA.html` desta pasta (dois cliques; funciona sem internet).

Reescreve um texto em português do Brasil tirando os padrões típicos de texto gerado por IA, sem mudar fatos, números e sentido. Um pequeno programa conta os sinais antes e depois da reescrita, e você recebe o texto pronto, o que mudou e o que ficou faltando.

## O que ela não faz

- Não promete passar em detector de IA e não adiciona ruído, erro ou caractere invisível.
- Não inventa exemplo, número ou caso: quando falta, deixa `[exemplo real]` para você preencher.
- Copy do zero e revisão completa de peça de venda ficam com o agente **Rita**. Trabalho acadêmico fica com a **Lúcia**.

## Como instalar

**Direto do GitHub:** no Claude Code, diga: "Instale a skill a partir de https://github.com/Empire-Business/omnx-texto-tirar-cara-de-ia". Para atualizar, diga: "Atualize a skill a partir de https://github.com/Empire-Business/omnx-texto-tirar-cara-de-ia". A IA baixa e copia os arquivos.

Se você já baixou esta pasta:

1. Abra o Claude Code (no aplicativo do Claude, aba **Code**, ambiente **Local**).
2. Escreva: **"Instale a skill que está nesta pasta: `<caminho desta pasta>`"**.
3. Você vai ver a IA copiando os arquivos. Não precisa digitar comando nenhum.
4. Abra uma conversa nova e faça um pedido, como nos exemplos abaixo.

### Instalar à mão

- **Mac ou Linux:** rode `bash install.sh` a partir desta pasta. A skill é copiada para `~/.claude/skills/omnx-texto-tirar-cara-de-ia`.
- **Windows:** copie esta pasta para `%USERPROFILE%\.claude\skills\omnx-texto-tirar-cara-de-ia`, ou peça para a IA fazer isso. O `install.sh` não é usado no Windows.
- Funciona em Mac, Windows e Linux, no Claude Code e no Codex. Na instalação, a própria IA faz as adaptações necessárias para o seu computador.

Funciona em Mac, Windows e Linux, no Claude Code e no Codex. Na instalação, a própria IA faz as adaptações necessárias para o seu computador.

## Como pedir

- "Tira a cara de IA deste texto: (cole o texto)"
- "Esse e-mail tá muito robótico, deixa mais humano."
- "Reescreve esse post sem parecer ChatGPT."

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `SKILL.md` | o passo a passo que a IA segue |
| `references/sinais.md` | a lista de padrões e como consertar cada um |
| `scripts/detectar_sinais.py` | conta os padrões num texto; só lê |
| `COMO-FUNCIONA.html` | guia visual |
| `install.sh` | instalação no Mac ou Linux |

## Versões

- 1.0 (08/11/2026): primeira versão.
