#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BBank 2026 — envio automático via Google Apps Script (HTTPS).
Configure GOOGLE_MAIL_URL e BBANK_MAIL_TOKEN no Render.
Veja CONFIGURAR_ENVIO.md para a configuração inicial.
"""

import csv
import html
import io
import json
import uuid
import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PORTA = int(os.getenv("PORT", os.getenv("PORTA", "8000")))
CACHE_SEGUNDOS = float(os.getenv("CACHE_SEGUNDOS", "3"))

ADMIN_EMAIL = "wanderson.silva@etapa.com.br"
GOOGLE_MAIL_URL = os.getenv("GOOGLE_MAIL_URL", "").strip()
BBANK_MAIL_TOKEN = os.getenv("BBANK_MAIL_TOKEN", "").strip()

SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID",
    "11jArIL27b7rhZSXWzfi4M7UPLaEGI8sraruHPQnfbSE"
).strip()

GOOGLE_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    + SHEET_ID
    + "/gviz/tq?sheet="
)

AQUISICOES = {
    "lugar_alternativo": {
        "nome": "Lugar alternativo",
        "descricao": "Mudar de lugar por uma aula",
        "custo": "B$ 50",
    },
    "cadeira_amigo": {
        "nome": "Cadeira ao lado de um amigo",
        "descricao": "Sentar ao lado de um amigo",
        "custo": "B$ 100",
    },
    "maker_coin": {
        "nome": "Maker Coin (MC$)",
        "descricao": "Comprar Maker Coin conforme a Taxa de Câmbio (TC) do mês",
        "custo": "TC*",
    },
}

USUARIOS_PODEM_COMPRAR = False

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#061225;--blue:#2463d4;--gold:#f5b83d;--ink:#0e1726;--muted:#65748a;--line:#e5eaf2;--success:#16845b}
html{scroll-behavior:smooth}
body{min-height:100vh;font-family:Inter,"Segoe UI",system-ui,sans-serif;color:var(--ink);background:radial-gradient(circle at 10% 5%,rgba(63,140,255,.25),transparent 28%),radial-gradient(circle at 90% 90%,rgba(245,184,61,.14),transparent 24%),linear-gradient(145deg,#061225,#0a1930 48%,#102a4b);padding:24px 14px;overflow-x:hidden}
body:before{content:"";position:fixed;width:380px;height:380px;border-radius:50%;background:#2463d4;filter:blur(100px);opacity:.16;left:-220px;top:10%;pointer-events:none}
.page{width:100%;max-width:1100px;margin:auto;position:relative;z-index:1;animation:enter .5s ease}
.shell{background:rgba(248,250,253,.97);border:1px solid rgba(255,255,255,.65);border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.3);overflow:hidden}
.header{background:linear-gradient(135deg,#071427,#102b4d);color:white;padding:24px 28px 18px;display:flex;align-items:center;gap:18px;position:relative}
.header:after{content:"";position:absolute;right:-70px;top:-100px;width:260px;height:260px;border-radius:50%;background:rgba(63,140,255,.13)}
.logo-img{width:58px;height:58px;object-fit:cover;border-radius:16px;box-shadow:0 12px 28px rgba(0,0,0,.25);background:#071427;position:relative;z-index:1}
.brand{position:relative;z-index:1}.brand h1{font-size:1.5rem;letter-spacing:-.04em}.brand p{margin-top:4px;color:#b7c5d8;font-size:.88rem}
.content{padding:28px}
.search{display:flex;gap:10px;margin-bottom:22px}
.search input{flex:1;min-width:0;border:1px solid var(--line);border-radius:13px;padding:13px 15px;font-size:.98rem;outline:0;background:#fff}
.search input:focus{border-color:#78a8ef;box-shadow:0 0 0 4px rgba(63,140,255,.1)}
button{border:0;border-radius:12px;background:linear-gradient(135deg,var(--blue),#347ee8);color:white;font-weight:800;padding:0 20px;cursor:pointer;box-shadow:0 8px 20px rgba(36,99,212,.22);transition:.2s}
button:hover{transform:translateY(-1px);filter:brightness(1.04)}
.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:20px}
.eyebrow{font-size:.75rem;text-transform:uppercase;letter-spacing:.13em;color:#6c7d92;font-weight:800}
.hero h2{font-size:1.75rem;letter-spacing:-.045em;margin-top:5px}
.meta{color:var(--muted);margin-top:5px;font-size:.9rem}
.status{padding:8px 12px;border-radius:999px;background:#edf8f3;color:var(--success);font-size:.8rem;font-weight:800;white-space:nowrap}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}
.stat{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px;min-height:118px;box-shadow:0 8px 24px rgba(22,38,64,.05)}
.stat .label{font-size:.78rem;color:#718096;font-weight:700}.stat .value{font-size:1.55rem;font-weight:900;letter-spacing:-.04em;margin-top:10px}.stat .small{font-size:.78rem;color:#8390a1;margin-top:4px}
.panel{background:#fff;border:1px solid var(--line);border-radius:20px;padding:20px;box-shadow:0 8px 24px rgba(22,38,64,.04)}
.panel h3{font-size:1rem;margin-bottom:15px}
.notes-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.note{border:1px solid var(--line);border-radius:14px;padding:14px;background:#fbfcfe}.note span{display:block;color:#78869a;font-size:.78rem}.note b{display:block;font-size:1.25rem;margin-top:5px}
.progress-wrap{margin-top:15px}.progress-top{display:flex;justify-content:space-between;font-size:.8rem;color:#68788e;margin-bottom:8px}
.progress{height:9px;background:#edf1f6;border-radius:999px;overflow:hidden}.progress i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--gold));border-radius:999px}
.aquisicoes{margin-top:16px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:20px}
.aquisicoes-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;margin-bottom:15px}
.aquisicoes-head p{font-size:.82rem;color:var(--muted);margin-top:4px}
.aquisicao-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.aquisicao{border:1px solid var(--line);border-radius:16px;padding:15px;background:#fbfcfe;display:flex;flex-direction:column;justify-content:space-between;gap:15px}
.aquisicao strong{display:block}.aquisicao span{display:block;color:var(--muted);font-size:.82rem;margin-top:6px}.preco{color:#1d5fc6!important;font-weight:900}
.aquisicao form{margin:0}.aquisicao button{height:40px;width:100%}
.notice{margin-top:13px;padding:12px 14px;border-radius:13px;background:#f4f7fb;color:#617087;font-size:.8rem}.notice.lock{background:#fff5f5;color:#9c4650}
.info,.erro{padding:15px;border-radius:14px;background:#f3f7fc;color:#5c6d82}.erro{background:#fff2f3;color:#9d3f4b}
.normas-atalho{margin-top:16px}.normas-button{display:flex;align-items:center;justify-content:center;width:100%;min-height:48px;padding:13px 18px;border-radius:13px;background:linear-gradient(135deg,var(--blue),#347ee8);color:#fff;text-decoration:none;font-weight:800;box-shadow:0 8px 20px rgba(36,99,212,.22);transition:.2s}.normas-button:hover{transform:translateY(-1px);filter:brightness(1.04)}
.back{display:inline-block;margin-top:18px;color:#3569b6;text-decoration:none;font-weight:800;font-size:.88rem}
footer{text-align:center;color:#9eb0c7;font-size:.75rem;padding:16px}
.loading{position:fixed;inset:0;background:rgba(5,15,30,.5);backdrop-filter:blur(5px);z-index:10;display:grid;place-items:center}.loading.hide{display:none}
.loading-box{background:white;border-radius:16px;padding:18px 22px;display:flex;gap:12px;align-items:center;box-shadow:0 20px 50px rgba(0,0,0,.25);font-weight:700}
.spinner{width:19px;height:19px;border:3px solid #dce5f2;border-top-color:#2463d4;border-radius:50%;animation:spin .7s linear infinite}
@keyframes enter{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,1fr)}.aquisicao-grid{grid-template-columns:1fr}}
@media(max-width:560px){body{padding:0}.shell{border-radius:0;min-height:100vh}.header{padding:18px}.content{padding:18px}.hero{align-items:flex-start;flex-direction:column}.hero h2{font-size:1.45rem}.search{gap:7px}.search button{padding:0 14px}.grid{gap:9px}.stat{padding:14px;min-height:105px}.stat .value{font-size:1.25rem}.panel,.aquisicoes{padding:16px}}
"""


def esc(value):
    return html.escape(str(value or "").strip())


def normalizar_matricula(value):
    texto = str(value or "").strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto


def baixar_aba(nome_aba):
    # A exportação CSV preserva os títulos que o endpoint gviz pode omitir
    # quando há linhas de agrupamento acima do cabeçalho.
    gids = {
        "B$": os.getenv("GOOGLE_SHEET_BALANCE_GID", "939288011"),
        "notas": os.getenv("GOOGLE_SHEET_GRADES_GID", "0"),
    }
    if nome_aba not in gids:
        raise ValueError("Aba da planilha não configurada.")
    url = (
        "https://docs.google.com/spreadsheets/d/" + SHEET_ID
        + "/export?format=csv&gid=" + quote(gids[nome_aba], safe="")
    )
    req = Request(url, headers={"User-Agent": "BBank-Consulta/2.0"})
    with urlopen(req, timeout=25) as resposta:
        bruto = resposta.read()
    texto = bruto.decode("utf-8-sig", errors="replace")
    dados = list(csv.reader(io.StringIO(texto)))
    for i, row in enumerate(dados):
        cabecalho = [str(x).strip() for x in row]
        if "Matrícula" in cabecalho and "Nome" in cabecalho:
            return [cabecalho] + dados[i + 1:]
    raise ValueError("Não foi encontrado o cabeçalho da aba " + nome_aba + ".")


class PlanilhaDB:
    def __init__(self):
        self.alunos = {}
        self.notas = {}
        self.atualizado_em = 0.0
        self.lock = threading.Lock()

    def atualizar(self):
        agora = time.monotonic()
        if agora - self.atualizado_em < CACHE_SEGUNDOS:
            return

        with self.lock:
            agora = time.monotonic()
            if agora - self.atualizado_em < CACHE_SEGUNDOS:
                return

            dados_b = baixar_aba("B$")
            dados_n = baixar_aba("notas")

            alunos = {}
            if dados_b:
                cabecalho = [str(x).strip() for x in dados_b[0]]
                idx = {nome: i for i, nome in enumerate(cabecalho)}

                def get_b(row, nome):
                    i = idx.get(nome)
                    if i is None or i >= len(row):
                        return ""
                    return str(row[i]).strip()

                mat_i = idx.get("Matrícula")
                if mat_i is not None:
                    for row in dados_b[1:]:
                        if mat_i >= len(row):
                            continue
                        mat = normalizar_matricula(row[mat_i])
                        if not mat:
                            continue

                        alunos[mat] = {
                            "matricula": mat,
                            "nome": get_b(row, "Nome"),
                            "ano": get_b(row, "Ano"),
                            "turma": get_b(row, "Turma"),
                            "saldo_1s": get_b(row, "Saldo 1°S"),
                            "s04": get_b(row, "04/08"),
                            "s11": get_b(row, "11/08"),
                            "s18": get_b(row, "18/08"),
                            "s25": get_b(row, "25/08"),
                            "mc": get_b(row, "MC$"),
                            "saldo": get_b(row, "Saldo"),
                            "status": get_b(row, "status"),
                        }

            notas = {}
            if dados_n:
                cabecalho = [str(x).strip() for x in dados_n[0]]
                idx = {nome: i for i, nome in enumerate(cabecalho)}

                def get_n(row, nome):
                    i = idx.get(nome)
                    if i is None or i >= len(row):
                        return ""
                    return str(row[i]).strip()

                mat_i = idx.get("Matrícula")
                if mat_i is not None:
                    for row in dados_n[1:]:
                        if mat_i >= len(row):
                            continue
                        mat = normalizar_matricula(row[mat_i])
                        if not mat:
                            continue

                        notas[mat] = {
                            "matricula": mat,
                            "nome": get_n(row, "Nome"),
                            "ano": get_n(row, "Ano"),
                            "turma": get_n(row, "Turma"),
                            "P1": get_n(row, "P1"),
                            "P2": get_n(row, "P2"),
                            "P3": get_n(row, "P3"),
                            "P4": get_n(row, "P4"),
                        }

            self.alunos = alunos
            self.notas = notas
            self.atualizado_em = time.monotonic()

    def aluno(self, matricula):
        self.atualizar()
        return self.alunos.get(matricula)

    def nota(self, matricula):
        self.atualizar()
        return self.notas.get(matricula)


DB = PlanilhaDB()


def numero_nota(valor):
    bruto = str(valor or "").strip().replace(",", ".")
    if not bruto:
        return None
    try:
        return float(bruto)
    except ValueError:
        return None


def usuario_blindado(aluno):
    status = str(aluno.get("status", "") or "").strip().casefold()
    return (
        "blindado" in status
        and "não blindado" not in status
        and "nao blindado" not in status
    )


def dashboard_notas(nota):
    valores = [numero_nota(nota.get(p, "")) for p in ("P1", "P2", "P3", "P4")]
    valores = [v for v in valores if v is not None]
    qtd = len(valores)
    return {
        "qtd": qtd,
        "media": sum(valores) / qtd if qtd else None,
        "maior": max(valores) if valores else None,
        "menor": min(valores) if valores else None,
        "percentual": int(qtd / 4 * 100),
    }


def formatar_numero(valor):
    return "—" if valor is None else f"{valor:.2f}".replace(".", ",")


def linha_nota(prova, valor):
    mostrado = esc(valor) if str(valor or "").strip() else "—"
    return (
        f'<div class="note"><span>{esc(prova)}</span>'
        f"<b>{mostrado}</b></div>"
    )


def notas_resumo_html(nota):
    if not nota:
        return '<div class="info">Nenhuma nota encontrada para esta matrícula.</div>'

    d = dashboard_notas(nota)
    cards = "".join(
        linha_nota(p, nota.get(p, ""))
        for p in ("P1", "P2", "P3", "P4")
    )

    return f"""
<section class="panel">
<h3>Desempenho acadêmico</h3>
<div class="grid" style="margin-bottom:14px">
<div class="stat"><span class="label">Média</span><div class="value">{formatar_numero(d["media"])}</div></div>
<div class="stat"><span class="label">Avaliações</span><div class="value">{d["qtd"]}/4</div></div>
<div class="stat"><span class="label">Maior nota</span><div class="value">{formatar_numero(d["maior"])}</div></div>
<div class="stat"><span class="label">Menor nota</span><div class="value">{formatar_numero(d["menor"])}</div></div>
</div>
<div class="notes-grid">{cards}</div>
<div class="progress-wrap">
<div class="progress-top"><span>Notas lançadas</span><b>{d["percentual"]}%</b></div>
<div class="progress"><i style="width:{d["percentual"]}%"></i></div>
</div>
</section>
"""


def render_aquisicoes(aluno):
    if not aluno:
        return ""

    if not USUARIOS_PODEM_COMPRAR and not usuario_blindado(aluno):
        return """
<section class="aquisicoes">
<div class="aquisicoes-head">
<div><h3>Aquisições</h3><p>Benefícios disponíveis para alunos Blindados.</p></div>
</div>
<div class="notice lock">
Aquisições bloqueadas para este status.
</div>
</section>
"""

    botoes = []
    for chave, item in AQUISICOES.items():
        botoes.append(
            f"""
<article class="aquisicao">
<div>
<strong>{esc(item["nome"])}</strong>
<span>{esc(item["descricao"])}</span>
<span class="preco">{esc(item["custo"])}</span>
</div>
<form method="post" action="/comprar">
<input type="hidden" name="matricula" value="{esc(aluno["matricula"])}">
<input type="hidden" name="produto" value="{esc(chave)}">
<button type="submit">Solicitar</button>
</form>
</article>
"""
        )

    aviso = (
        "Modo de teste: todos os status podem solicitar aquisições."
        if USUARIOS_PODEM_COMPRAR
        else "A solicitação é enviada automaticamente por e-mail. O saldo não é alterado automaticamente."
    )

    return f"""
<section class="aquisicoes">
<div class="aquisicoes-head">
<div><h3>Aquisições</h3><p>Solicite um benefício e aguarde a confirmação do administrador.</p></div>
</div>
<div class="aquisicao-grid">{"".join(botoes)}</div>
<div class="notice">{esc(aviso)}</div>
</section>
"""


def render_dashboard(aluno, nota=None):
    d = dashboard_notas(nota or {}) if nota else {
        "qtd": 0,
        "media": None,
        "maior": None,
        "menor": None,
        "percentual": 0,
    }

    return f"""
<div class="hero">
<div>
<div class="eyebrow">Painel do aluno</div>
<h2>{esc(aluno["nome"])}</h2>
<p class="meta">{esc(aluno["ano"])}º ano · Turma {esc(aluno["turma"])} · Matrícula {esc(aluno["matricula"])}</p>
</div>
<span class="status">{esc(aluno["status"]) or "Status não informado"}</span>
</div>

<div class="grid">
<div class="stat"><span class="label">Saldo atual</span><div class="value">{esc(aluno["saldo"]) or "—"}</div><div class="small">Saldo informado pela planilha</div></div>
<div class="stat"><span class="label">Saldo 1º semestre</span><div class="value">{esc(aluno["saldo_1s"]) or "—"}</div><div class="small">Referência inicial</div></div>
<div class="stat"><span class="label">MC$</span><div class="value">{esc(aluno["mc"]) or "—"}</div><div class="small">Maker Coin</div></div>
<div class="stat"><span class="label">Média das notas</span><div class="value">{formatar_numero(d["media"])}</div><div class="small">{d["qtd"]}/4 avaliações lançadas</div></div>
</div>

<div style="margin-top:16px">{notas_resumo_html(nota)}</div>
<div id="aquisicoes">{render_aquisicoes(aluno)}</div>

<div class="normas-atalho">
<a class="normas-button" href="https://etapa.link/bbank/normas" target="_blank" rel="noopener noreferrer">
Abrir normas do BBank
</a>
</div>

<a class="back" href="/">Nova consulta</a>
"""


def pagina(conteudo="", valor_digitado="", titulo="BBank 2026"):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<style>{CSS}</style>
</head>
<body>
<div id="loading" class="loading hide" aria-hidden="true">
<div class="loading-box"><span class="spinner"></span><span>Consultando dados...</span></div>
</div>

<div class="page">
<main class="shell">
<header class="header">
<img class="logo-img" src="/assets/bbank_logo.png" alt="Logo BBank">
<div class="brand">
<h1>BBank 2026</h1>
<p>Consulta de saldo, notas e informações</p>
</div>
</header>

<div class="content">
<form class="search" method="get" action="/">
<input name="matricula" inputmode="numeric" pattern="[0-9]*"
placeholder="Digite sua matrícula" value="{esc(valor_digitado)}"
autocomplete="off" required>
<button type="submit">Consultar</button>
</form>
{conteudo}
</div>
</main>
<footer>BBank 2026 · Dados sincronizados com Google Planilhas</footer>
</div>

<script>
(() => {{
    const loading = document.getElementById("loading");
    document.querySelectorAll("form.search").forEach(form => {{
        form.addEventListener("submit", () => loading.classList.remove("hide"));
    }});
    window.addEventListener("pageshow", () => loading.classList.add("hide"));
}})();
</script>
</body>
</html>""".encode("utf-8")


def enviar_email_compra(aluno, produto):
    """Solicita envio automático; só retorna com confirmação do Google."""
    item = AQUISICOES[produto]
    assunto = f"BBank — Solicitação de aquisição — {item['nome']}"
    corpo = (
        "Nova solicitação de aquisição no BBank 2026.\r\n\r\n"
        f"Aluno: {aluno.get('nome', '')}\r\n"
        f"Matrícula: {aluno.get('matricula', '')}\r\n"
        f"Ano: {aluno.get('ano', '')}\r\n"
        f"Turma: {aluno.get('turma', '')}\r\n"
        f"Status: {aluno.get('status', '')}\r\n"
        f"Produto: {item['nome']}\r\n"
        f"Descrição: {item['descricao']}\r\n"
        f"Custo: {item['custo']}\r\n"
    )
    endpoint = urlparse(GOOGLE_MAIL_URL)
    if (endpoint.scheme != "https" or endpoint.hostname != "script.google.com"
            or not endpoint.path.startswith("/macros/s/")
            or not endpoint.path.endswith("/exec") or endpoint.query):
        raise RuntimeError("Configure GOOGLE_MAIL_URL com a URL /exec do Apps Script no Render.")
    if len(BBANK_MAIL_TOKEN) < 32:
        raise RuntimeError("Configure BBANK_MAIL_TOKEN no Render com pelo menos 32 caracteres.")
    request = Request(GOOGLE_MAIL_URL, method="POST",
        data=json.dumps({"token": BBANK_MAIL_TOKEN, "requestId": uuid.uuid4().hex,
                         "subject": assunto, "body": corpo}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError):
        raise RuntimeError("Não foi possível confirmar o envio pelo Google. Consulte o administrador antes de repetir o pedido.") from None
    except (ValueError, UnicodeError):
        raise RuntimeError("O Google não retornou a confirmação. Confira a implantação /exec e o acesso para Qualquer pessoa.") from None
    if not isinstance(result, dict) or result.get("ok") is not True:
        code = result.get("code") if isinstance(result, dict) else None
        errors = {
            "auth": "O token do Render deve ser igual ao token nas propriedades do Apps Script.",
            "quota": "O limite diário de e-mails do Google foi atingido.",
            "config": "Configure BBANK_MAIL_TOKEN nas propriedades do Apps Script.",
        }
        errors.update({
            "send": "O Apps Script recebeu o pedido, mas falhou ao enviar o e-mail. Confira a permissão do MailApp e o erro em Execuções no Apps Script antes de repetir o pedido.",
            "invalid": "O Apps Script rejeitou o formato do pedido. Publique uma nova versão usando o Google_Email.gs do repositório BBank.",
            "busy": "O serviço de envio está ocupado. Aguarde alguns segundos antes de tentar novamente.",
        })
        # Registre apenas códigos conhecidos; nunca tokens, corpos ou respostas brutas.
        safe_code = code if isinstance(code, str) and code in errors else "unexpected_response"
        print("BBANK_MAIL_ERROR code=" + safe_code, flush=True)
        raise RuntimeError(errors.get(safe_code,
            "O Apps Script retornou uma resposta incompatível (unexpected_response). "
            "Confira se a URL /exec aponta para uma implantação atualizada do Google_Email.gs."))


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/comprar":
            self.send_error(404, "Página não encontrada")
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = self.rfile.read(tamanho).decode("utf-8")
            params = parse_qs(corpo)

            mat = (params.get("matricula", [""])[0] or "").strip()
            produto = (params.get("produto", [""])[0] or "").strip()

            if produto not in AQUISICOES:
                self.send_error(400, "Aquisição inválida")
                return

            aluno = DB.aluno(mat)
            if not aluno:
                dados = pagina(
                    '<div class="erro">Aluno não encontrado.</div>',
                    mat,
                    "Aquisição — BBank 2026",
                )
                self._responder_html(dados, 404)
                return

            # PRODUÇÃO: somente Blindados.
            # TESTE: esta verificação é desativada.
            if not USUARIOS_PODEM_COMPRAR and not usuario_blindado(aluno):
                dados = pagina(
                    '<div class="erro"><b>Aquisições disponíveis somente para Blindados.</b></div>',
                    mat,
                    "Aquisição — BBank 2026",
                )
                self._responder_html(dados, 403)
                return

            enviar_email_compra(aluno, produto)

            item = AQUISICOES[produto]
            corpo_html = f"""
<div class="panel">
<h3>Solicitação enviada</h3>
<p class="meta">Sua solicitação de <b>{esc(item["nome"])}</b> foi enviada automaticamente para o administrador.</p>
<p class="meta">Aguarde a confirmação do administrador. O saldo não é alterado automaticamente.</p>
</div>
<a class="back" href="/?matricula={quote(mat)}">← Voltar para o saldo</a>
"""
            dados = pagina(corpo_html, mat, "Solicitação enviada — BBank 2026")
            self._responder_html(dados, 200)

        except Exception as exc:
            mensagem = (
                '<div class="erro"><b>Não foi possível enviar a solicitação.</b><br><br>'
                f'{esc(str(exc))}</div>'
            )
            dados = pagina(mensagem, "", "Erro — BBank 2026")
            self._responder_html(dados, 500)

    def _responder_html(self, dados, status):
        if not isinstance(dados, bytes):
            dados = dados.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        mat = ""

        try:
            parsed = urlparse(self.path)
            caminho = parsed.path
            params = parse_qs(parsed.query)
            mat = (params.get("matricula", [""])[0] or "").strip()

            if caminho == "/assets/bbank_logo.png":
                try:
                    caminho_logo = os.path.join(
                        os.path.dirname(__file__),
                        "bbank_logo.png"
                    )
                    with open(caminho_logo, "rb") as arquivo:
                        dados = arquivo.read()
                except FileNotFoundError:
                    self.send_error(404, "Logo não encontrada")
                    return

                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.send_header("Content-Length", str(len(dados)))
                self.end_headers()
                self.wfile.write(dados)
                return

            if caminho not in ("/", "/index.html"):
                self.send_error(404, "Página não encontrada")
                return

            if not mat:
                corpo = """
<div class="hero">
<div>
<div class="eyebrow">BBank 2026</div>
<h2>Seu painel começa aqui</h2>
<p class="meta">Digite sua matrícula para carregar saldo, notas e informações.</p>
</div>
</div>
<div class="info">Use o campo acima para consultar seus dados.</div>
"""
            else:
                aluno = DB.aluno(mat)
                corpo = (
                    render_dashboard(aluno, DB.nota(mat))
                    if aluno
                    else f'<div class="erro">Matrícula <b>{esc(mat)}</b> não encontrada. Confira o número e tente novamente.</div>'
                )

            dados = pagina(corpo, mat, "Dashboard — BBank 2026")
            self._responder_html(dados, 200)

        except Exception as exc:
            mensagem = (
                '<div class="erro"><b>Não foi possível acessar a planilha Google agora.</b>'
                f'<br><br>{esc(str(exc))}</div>'
            )
            self._responder_html(
                pagina(mensagem, mat, "Erro — BBank 2026"),
                502,
            )

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    url = f"http://localhost:{PORTA}"

    print("=" * 60)
    print("  BBank 2026")
    print(f"  Abra: {url}")
    print("  Fonte: Google Planilhas / B$ e notas")
    print("  Pedidos: envio automático pelo Google Apps Script")
    print(f"  Cache: {CACHE_SEGUNDOS} segundo(s)")
    print("  Para encerrar: Ctrl+C")
    print("=" * 60)

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("0.0.0.0", PORTA), Handler).serve_forever()
