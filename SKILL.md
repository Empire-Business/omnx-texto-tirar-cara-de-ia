---
name: omnx-texto-tirar-cara-de-ia
description: "Reescreve um texto em português do Brasil tirando os padrões típicos de texto gerado por IA (contraste 'não é X, é Y', fecho de efeito, trio de adjetivos, frases picadas, palavras de consultoria) e mantendo fatos, números e sentido. Use quando pedirem 'tira a cara de IA', 'deixa mais humano', 'humaniza esse texto', 'esse texto tá com cara de ChatGPT', 'reescreve sem parecer robô', 'tá muito robótico', em post, e-mail, artigo, legenda, página, roteiro ou mensagem já escrito. Não use para burlar detector de IA ou esconder autoria em TCC, tese ou prova (lucia), para escrever copy do zero ou fazer a revisão completa de uma peça de venda (rita), para só corrigir gramática nem para traduzir."
---

# Tirar cara de IA

Reescreve o texto da pessoa para soar como alguém falando, sem mudar o que ele diz. É preferência de estilo: a skill não descobre quem escreveu e não promete passar em detector.

## Como falar com a pessoa

Ela pode nunca ter usado IA. No começo da conversa, diga em duas linhas o que você faz. Faça uma pergunta por vez. Explique termo técnico em meia frase. Nunca peça para ela digitar comando: quem roda o script é você. Termine cada resposta com o próximo passo.

## Quando não usar

| Pedido | Quem resolve |
|---|---|
| Escrever copy do zero, revisão de ofício completa, checagem antes de lançar | agente Rita |
| Trabalho acadêmico, ou esconder que a IA escreveu | agente Lúcia (que trata autoria com ética) ou recuse |
| Só gramática e ortografia | responda sem esta skill |

Pedido de "passar no detector": explique que a skill não faz isso, porque ruído, palavras hesitantes e caracteres invisíveis estragam o texto. Ofereça a reescrita de estilo.

## Passos

1. **Pegue o texto.** Se não veio, peça. Se a pessoa disser onde ele vai sair (e-mail, post, página) e como ela fala, use isso. Não faça entrevista: sem essa informação, siga.
2. **Conte os sinais.** Salve o texto num arquivo temporário fora da pasta da skill e rode:
   `python3 "<pasta desta skill>/scripts/detectar_sinais.py" <arquivo>`
   `<pasta desta skill>` é a pasta onde está este `SKILL.md`. A saída é JSON com `achados`, `densidade` e totais. O script só lê.
3. **Leia `references/sinais.md`** para saber como consertar cada família de sinal.
4. **Reescreva**, seguindo as regras abaixo.
5. **Conte de novo:** `python3 "<pasta desta skill>/scripts/detectar_sinais.py" <antes> --depois <depois>`. Meta: `total_corrigir` igual a zero em `depois` e nenhum teto de densidade estourado. O script só vê a forma: fato real em forma de contraste ("não foi ao banco, foi ao mercado") e sentido literal ou técnico ("destravar a porta") ficam, com justificativa na entrega. Em `total_conferir`, olhe um por um: troque, ou mantenha se o uso for legítimo.
6. **Leia em voz alta, de cabeça.** O script só acha o que tem forma conhecida. Se ainda soar como comercial de TV, legenda filosófica ou palestra, reescreva o trecho.
7. **Entregue** no formato abaixo.

## Regras da reescrita

- **Nada novo.** Fato, número, nome, promessa concreta, link, pedido de ação (responder, agendar) e ordem das informações ficam como estão. Sem dado inventado, sem exemplo inventado. Fecho genérico ("agora é com você") sai, e você avisa que faltou um pedido claro.
- **Enfeite pode sair.** Adjetivo sem fato ("rápido, simples e eficaz") e frase sem informação não são fatos: corte. A lista de funções e os números ficam.
- **Diga o Y direto.** Em "não é X, é Y", fique com Y. Se Y sozinho soar vazio e não houver dado para sustentar, use a marca abaixo.
- **Termine sem frase de efeito**, no último dado que o texto já tinha, sem reordenar.
- **Faltou fato?** Trecho só com conceito leva `[exemplo real: quem, onde, fazendo o quê]`. Afirmação sem dono leva `[fonte: quem disse]`, ou saia a frase se a pessoa preferir. No máximo três marcas por texto.
- **Mantenha a voz.** Gíria, bordão e jeito de falar da pessoa ficam. Se ela disser que um sinal é proposital, não aponte de novo nesta conversa.
- **Não encha.** O texto pode encurtar ao perder enrolação; nunca aumente para compensar.
- **Nunca** acrescente erro de propósito, hesitação ("salvo melhor opinião", "se não me engano") ou caractere invisível.
- Citação de outra pessoa fica intacta, mesmo com sinal.

## Formato da entrega

1. O texto reescrito, incluindo título ou assunto. Se houver marcas, avise que ele só fica pronto depois de preenchê-las.
2. **O que mudou:** até 5 linhas, agrupando por tipo de padrão, com um antes → depois.
3. **Contagem:** sinais a corrigir antes e depois.
4. **Falta você:** cada marca (`marcas_pendentes` no script) e cada sinal que ficou, com o motivo.
5. O próximo passo, em uma frase.

## Texto em outro idioma

As listas são de português do Brasil. Avise, aplique as regras de estrutura de `references/sinais.md` e não apresente contagem.

## Se der erro

Arquivo não encontrado ou vazio: diga em português simples o que houve e peça o texto de novo. Sem Python na máquina: faça a revisão lendo `references/sinais.md` e avise que a contagem não foi feita.

## Outro sistema operacional

O script usa só a biblioteca padrão do Python 3. Adapte e conte o que funcionou de verdade:

- **Python:** `python3` (macOS, Linux), `py -3` ou `python` (Windows). Sem Python, siga pela leitura e avise. Não instale nada só para isso.
- **Pasta pessoal:** `~` é `%USERPROFILE%` no Windows. Caminho com espaço vai entre aspas.
- **Arquivo temporário:** use a pasta temporária do sistema (`$TMPDIR`, `/tmp` ou `%TEMP%`).
- **Instalar no Windows:** copie esta pasta para `%USERPROFILE%\.claude\skills\omnx-texto-tirar-cara-de-ia`.

## Outra ferramenta (Codex e outras)

Compatível com Claude Code, Codex e outras ferramentas de agentes, em Mac, Windows e Linux. Se a pessoa pedir para instalar
fora do Claude Code, a IA dela adapta na hora, testa no computador dela e conta o que realmente funcionou:
