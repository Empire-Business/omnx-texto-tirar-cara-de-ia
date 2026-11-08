#!/usr/bin/env python3
"""Conta sinais de texto com cara de IA em português do Brasil e imprime JSON.

Uso:
  detectar_sinais.py <arquivo>                   analisa um texto ("-" lê da entrada padrão)
  detectar_sinais.py <antes> --depois <depois>   compara duas versões

Só lê. Não altera nenhum arquivo. Biblioteca padrão do Python 3.8 em diante.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FLAGS = re.IGNORECASE | re.UNICODE
L = r"[^\W\d_]"  # letra, com acento
CORRIGIR, CONFERIR = "corrigir", "conferir"


def termos(*lista):
    return r"\b(?:" + "|".join(lista) + r")\b"


VAZIOS = r"rápid[oa]s?|simples|eficaz(?:es)?|fáce(?:l|is)|prátic[oa]s?|segur[oa]s?|modern[oa]s?|inteligentes?|intuitiv[oa]s?|completa?o?s?|acessíve(?:l|is)|confiáve(?:l|is)|ágeis|ágil|poderos[oa]s?|estruturad[oa]s?|testad[oa]s?|escalad[oa]s?"

# (categoria, gravidade, padrão, dica)
PADROES = [
    ("contraste", CORRIGIR, r"\bn[ãa]o\s+(é|são|era|foi)\b(?!\s+nem\b)[^.!?\n]{0,90}?[,;:.]\s*\1\b", "afirme a segunda parte direto"),
    ("contraste", CORRIGIR, r"\bn[ãa]o\s+se\s+trata\b[^.!?\n]{0,90}?[,;:.]\s*(?:trata-se|é|mas\s+(?:de|sim|sobre|em)|e\s+sim)\b", "afirme a segunda parte direto"),
    ("contraste", CORRIGIR, r"\bn[ãa]o\s+(" + L + r"{3,})\b[^.!?\n]{1,70}?[.,;]\s*\1\b", "afirme a segunda parte direto"),
    ("contraste", CORRIGIR, r"\bmais\s+do\s+que\b[^.!?\n]{1,70},\s*(?:é|são)\b", "afirme a segunda parte direto"),
    ("contraste", CORRIGIR, r"\?\s+N[ãa]o\.\s", "afirme direto"),
    ("terceira_opcao", CORRIGIR, r"\bn[ãa]o\s+é\s+nem\b", "diga a terceira opção com um fato"),
    ("fecho_de_efeito", CORRIGIR, termos(r"e\s+isso\s+muda\s+tudo", r"simples\s+assim", r"é\s+sobre\s+isso", r"fim\s+de\s+papo", r"e\s+ponto\s+final", r"e\s+isso\s+faz\s+toda\s+a\s+diferen[çc]a"), "corte e termine na informação"),
    ("aforismo", CONFERIR, r"\b" + L + r"+\s+é\s+" + L + r"+\s+em\s+(?:forma\s+de|movimento|construção)\b", "troque por um caso ou corte"),
    ("aforismo", CONFERIR, r"(?:^|[.!?]\s+)" + L + r"+(?:\s+" + L + r"+)?\s+também\s+é\s+" + L + r"+(?:\s+" + L + r"+){0,2}[.!]", "troque por um caso ou corte"),
    ("fechamento_pronto", CORRIGIR, termos(r"em\s+conclusão", r"em\s+suma", r"para\s+concluir", r"em\s+resumo,\s+podemos", r"espero\s+que\s+este\s+conteúdo", r"conta\s+nos\s+comentários", r"o\s+futuro\s+pertence", r"no\s+fim\s+das\s+contas", r"agora\s+é\s+com\s+você", r"agora\s+é\s+a\s+sua\s+vez"), "entregue a última informação e pare"),
    ("pigarro", CORRIGIR, termos(r"a\s+questão\s+é\s+a\s+seguinte", r"vamos\s+ser\s+sinceros", r"a\s+verdade\s+é\s+que", r"vale\s+ressaltar", r"é\s+importante\s+(?:destacar|notar|ressaltar)", r"cabe\s+salientar", r"isso\s+tem\s+nome"), "comece no assunto"),
    ("pergunta_de_suspense", CORRIGIR, r"(?:^|[.!?\n]\s*)(?:o\s+segredo|o\s+motivo|a\s+resposta|resultado|curioso|e\s+agora|quer\s+saber\s+mais)\?", "afirme"),
    ("metafora_traduzida", CORRIGIR, termos(r"navegar\s+pel[oa]s?\s+complexidades?", r"desbloque\w+", r"destrav\w+", r"abra[çc]ar\s+a\s+mudança", r"alavanc\w+", r"pap[ée]l?\s+(?:fundamental|crucial)", r"mergulh\w+\s+fundo", r"divisor\s+de\s+águas", r"peça-chave", r"próximo\s+(?:nível|patamar)", r"elevar\s+o\s+nível", r"elev(?:e|ar|a)\s+(?:o\s+|a\s+)?(?:seu|sua|seus|suas)", r"impulsion\w+"), "reescreva sem a metáfora; veja references/sinais.md"),
    ("metafora_literal_a_conferir", CONFERIR, termos(r"jornada\w*", r"ecossistema\w*"), "fica só no sentido literal"),
    ("palavra_de_consultoria", CONFERIR, termos(r"otimiz\w+", r"viabiliz\w+", r"mitig\w+", r"abrangente\w*", r"robust[oa]s?", r"proativ\w+", r"potencializ\w+", r"holístic\w+", r"disruptiv\w+", r"escaláve(?:l|is)", r"assertiv\w+", r"engajamento", r"entreg\w+\s+valor", r"sinergia\w*", r"paradigma\w*"), "troque pela palavra comum, salvo sentido técnico"),
    ("dono_vago", CORRIGIR, termos(r"(?:especialistas|estudos|pesquisas)(?:\s+(?:do\s+setor|da\s+área|de\s+mercado|recentes))?\s+(?:apontam|afirmam|dizem|indicam|mostram|comprovam|revelam)", r"segundo\s+especialistas", r"o\s+mercado\s+entende"), "nomeie a fonte; sem fonte, marque e peça"),
    ("qualificador_universal", CORRIGIR, r"\bqualquer\s+" + L + r"+,\s*qualquer\b", "diga para quem serve"),
    ("analogia_batida", CONFERIR, r"\bé\s+como\s+ter\b[^.!?\n]{3,60}?\se\s+(?:não|só|pular|usar|morar)\b", "use caso real ou corte"),
    ("entusiasmo_de_sistema", CORRIGIR, termos(r"novidade\s+empolgante", r"estamos\s+muito\s+felizes\s+em", r"temos\s+o\s+prazer\s+de"), "dê a notícia"),
    ("verbo_inflado", CONFERIR, termos(r"serve\s+como", r"atua\s+como", r"figura\s+como", r"se\s+configura\s+como"), "quase sempre o verbo certo é 'é'"),
    ("cadeia_de_gerundios", CONFERIR, r"\b" + L + r"+ndo,\s+" + L + r"+ndo\b", "use um verbo só"),
    ("lista_como_frase", CORRIGIR, r"(?:\b" + L + r"+,\s+){3,}" + L + r"+\s+e\s+" + L + r"+\b", "escolha o que importa e conte"),
    ("portugues_de_portugal", CONFERIR, termos(r"facto", r"factos", r"perspetiva\w*", r"monitorizar", r"consciencializar", r"partilhad[oa]s?"), "use a forma brasileira"),
    ("fulano_entendeu", CONFERIR, r"\bentendeu\s+que\b", "conte o que a pessoa fez"),
    ("esquema_de_slide", CORRIGIR, r"\b(?:o\s+)?(?:problema|desafio)\s*:[^.\n]{1,120}\.\s+(?:o\s+|a\s+)?(?:conserto|solução|resposta|resultado)\s*:", "escreva em prosa"),
    ("trio_vazio", CORRIGIR, r"\b(?:" + VAZIOS + r"),\s+(?:" + VAZIOS + r")\s+e\s+(?:" + VAZIOS + r")\b", "diga o que cada coisa faz, ou corte"),
    ("travessao", CORRIGIR, r"(?:(?<!\d)(?<!\d\s)\s*[—–]\s*|\s*[—–]\s*(?!\s?\d))", "use vírgula, ponto, dois-pontos ou parênteses"),
]
PADROES = [(c, g, re.compile(p, FLAGS), d) for c, g, p, d in PADROES]

ABERTURAS = re.compile(
    r"^[ \t]*(?:no\s+mundo\s+(?:de\s+hoje|acelerado|atual)|num\s+mundo\s+cada\s+vez|em\s+um\s+mundo\s+cada\s+vez|na\s+era\s+digital|"
    r"vivemos\s+um\s+momento|desde\s+sempre,\s+o\s+ser\s+humano|você\s+já\s+se\s+perguntou|imagine\s+por\s+um\s+instante|"
    r"descubra\s+o\s+poder|desbloqueie\s+o\s+potencial|em\s+um\s+cenário\s+cada\s+vez|não\s+é\s+segredo\s+para\s+ninguém|seja\s+você\s+um)",
    FLAGS | re.MULTILINE,
)
CONECTIVOS = re.compile(
    termos(r"além\s+disso", r"no\s+entanto", r"consequentemente", r"nesse\s+sentido", r"dito\s+isso", r"por\s+outro\s+lado", r"contudo", r"portanto"), FLAGS
)
ENTUSIASMO = re.compile(termos(r"incríve(?:l|is)", r"poderos[oa]s?", r"essenciais", r"essencial", r"revolucionári[oa]s?", r"extraordinári[oa]s?", r"transformador[a]?"), FLAGS)
TRIO = re.compile(r"\b" + L + r"{3,},\s+" + L + r"{3,}\s+e\s+" + L + r"{3,}\b", FLAGS)
NEGRITO = re.compile(r"\*\*[^*\n]+\*\*")
PARAGRAFO = re.compile(r"[^\n]+(?:\n(?!\s*\n)[^\n]+)*")
FRASE = re.compile(r"[^.!?\n]+[.!?]*")
PALAVRA = re.compile(L + r"+(?:-" + L + r"+)*")
CERCA = re.compile(r"```.*?```|`[^`\n]+`", re.DOTALL)
MARCA = re.compile(r"\[(?:exemplo real|fonte)\b[^\]\n]*\]", re.IGNORECASE)
ABREVIACAO = re.compile(r"\b(?:Sr|Sra|Dr|Dra|Prof|Profa|Av|art|etc|ex|n)\.(?=\s)", re.IGNORECASE)
PONTO_INTERNO = re.compile(r"\.(?=[^\W_])")


def neutralizar_codigo(texto):
    """Troca blocos de código por espaços, mantendo os números de linha."""
    return CERCA.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), texto)


def linha_de(texto, pos):
    return texto.count("\n", 0, pos) + 1


def achado(texto, ini, fim, categoria, gravidade, dica):
    trecho = re.sub(r"\s+", " ", texto[ini:fim]).strip()
    return {"categoria": categoria, "gravidade": gravidade, "linha": linha_de(texto, ini), "trecho": trecho[:140], "dica": dica}


def frases_de(texto):
    """Divide em frases sem cortar em abreviação, decimal, endereço de site."""
    protegido = PONTO_INTERNO.sub("\u00b7", ABREVIACAO.sub(lambda m: m.group(0)[:-1] + "\u00b7", texto))
    saida = []
    for m in FRASE.finditer(protegido):
        bruto = m.group(0).strip()
        if PALAVRA.search(bruto):
            saida.append((m.start(), m.end(), len(PALAVRA.findall(bruto))))
    return saida


def analisar(bruto):
    texto = neutralizar_codigo(bruto)
    achados, ocupado = [], {}

    for categoria, gravidade, padrao, dica in PADROES:
        for m in padrao.finditer(texto):
            ini, fim = m.span()
            usados = ocupado.setdefault(categoria, [])
            if any(ini < f and fim > i for i, f in usados):
                continue
            usados.append((ini, fim))
            achados.append(achado(texto, ini, fim, categoria, gravidade, dica))

    for m in ABERTURAS.finditer(texto):
        achados.append(achado(texto, m.start(), m.end(), "abertura_pronta", CORRIGIR, "comece pelo caso ou pelo número"))
    for m in PARAGRAFO.finditer(texto):
        negritos = NEGRITO.findall(m.group(0))
        if len(negritos) > 1:
            achados.append(achado(texto, m.start(), m.start() + 60, "negrito_em_excesso", CONFERIR, "um destaque por parágrafo"))

    frases = frases_de(texto)
    corrida = []
    for item in frases + [(len(texto), len(texto), 99)]:
        if item[2] <= 4:
            corrida.append(item)
            continue
        if len(corrida) >= 3:
            achados.append(achado(texto, corrida[0][0], corrida[-1][1], "ritmo_picado", CORRIGIR, "junte as frases e varie o tamanho"))
        corrida = []

    palavras = len(PALAVRA.findall(texto))
    total_frases = len(frases)
    densidade = []

    def medir(nome, regex_ou_lista, teto, categoria, dica):
        ocorrencias = list(regex_ou_lista.finditer(texto))
        if categoria == "trio":
            spans = ocupado.get("lista_como_frase", []) + ocupado.get("trio_vazio", [])
            ocorrencias = [m for m in ocorrencias if not any(m.start() < f and m.end() > i for i, f in spans)]
        estourou = len(ocorrencias) > teto
        densidade.append({"item": nome, "encontrado": len(ocorrencias), "teto": teto, "estourou": estourou})
        if estourou:
            for m in ocorrencias:
                achados.append(achado(texto, m.start(), m.end(), categoria, CONFERIR, dica))

    medir("conectivos", CONECTIVOS, max(1, total_frases // 3), "conectivo_em_excesso", "use 'e', 'mas', 'por isso', ou corte")
    medir("adjetivos_de_entusiasmo", ENTUSIASMO, max(1, palavras // 500), "entusiasmo_em_excesso", "corte ou troque por um fato")
    medir("trios", TRIO, 1, "trio", "dois itens com concreto, ou quatro")

    achados.sort(key=lambda a: (a["linha"], a["categoria"]))
    por_categoria = {}
    for a in achados:
        por_categoria[a["categoria"]] = por_categoria.get(a["categoria"], 0) + 1
    return {
        "palavras": palavras,
        "frases": total_frases,
        "total_corrigir": sum(a["gravidade"] == CORRIGIR for a in achados),
        "total_conferir": sum(a["gravidade"] == CONFERIR for a in achados),
        "marcas_pendentes": MARCA.findall(texto),
        "densidade": densidade,
        "por_categoria": dict(sorted(por_categoria.items())),
        "achados": achados,
    }


def ler(caminho):
    if caminho == "-":
        return sys.stdin.read()
    return Path(caminho).read_text(encoding="utf-8-sig", errors="replace")


def imprimir(dados):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(dados, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="Conta sinais de texto com cara de IA (só lê).")
    p.add_argument("arquivo", help="arquivo de texto, ou - para a entrada padrão")
    p.add_argument("--depois", help="segunda versão, para comparar")
    a = p.parse_args()
    try:
        antes = ler(a.arquivo)
        depois = ler(a.depois) if a.depois else None
    except OSError as e:
        imprimir({"erro": "Não consegui ler o arquivo: %s" % e})
        return 2
    if not PALAVRA.search(antes):
        imprimir({"erro": "O texto está vazio."})
        return 2
    r = analisar(antes)
    if depois is None:
        imprimir(r)
        return 0
    if not PALAVRA.search(depois):
        imprimir({"erro": "A segunda versão está vazia."})
        return 2
    d = analisar(depois)
    imprimir({
        "antes": {k: r[k] for k in ("palavras", "total_corrigir", "total_conferir", "por_categoria")},
        "depois": d,
        "tamanho_mudou_pct": round((d["palavras"] - r["palavras"]) / max(1, r["palavras"]) * 100, 1),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
