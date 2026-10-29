"""Monta a versão estática do painel em site/ (para hospedar no Render).

Uso: python scripts/montar_site.py
Junta painel/index.html com o d3 e o dash-shim.js e copia as bases de dados/processados.
"""
import pathlib
import re
import shutil

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = RAIZ / "site"

HEAD = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manifestações de usuários · Arsesp</title>
<meta name="description" content="Planejamento, apuração e painel das reclamações e solicitações de usuários de água e esgoto, com dados abertos da Arsesp (2021–2024).">
<style>
  html, body { margin: 0; background: #ffffff; }
  @media (prefers-color-scheme: dark) { html, body { background: #101820; } }
  :root { --cds-dur-slow: 240ms; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="dash-shim.js"></script>
</head>
<body>
<div id="dash-root">
"""
FOOT = """
</div>
</body>
</html>
"""

pagina = (RAIZ / "painel" / "index.html").read_text(encoding="utf-8")
pagina = pagina.replace('<meta name="dash-one-writer">\n', "", 1)
# No painel do Claude cada <script> roda em escopo próprio; numa página comum, isola cada um num bloco
pagina = re.sub(r"<script>(.*?)</script>", lambda m: "<script>{" + m.group(1) + "}</script>", pagina, flags=re.S)
(SITE / "index.html").write_text(HEAD + pagina + FOOT, encoding="utf-8")

destino = SITE / "dados"
destino.mkdir(parents=True, exist_ok=True)
for arq in (RAIZ / "dados" / "processados").glob("*.json"):
    shutil.copy2(arq, destino / arq.name)
print("Site montado em", SITE)
