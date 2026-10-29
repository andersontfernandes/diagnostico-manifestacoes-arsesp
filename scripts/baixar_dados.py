"""Baixa o conjunto "Manifestações de usuários" da Arsesp e extrai os CSV.

Uso: python scripts/baixar_dados.py [pasta_destino]   (padrão: dados/brutos)
"""
import pathlib
import sys
import urllib.request
import zipfile

URL = "https://www.arsesp.sp.gov.br/Documentosgerais/Dados-Abertos/REG_SAN_SGFCI-RECLAMACOES.zip"

destino = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dados/brutos")
destino.mkdir(parents=True, exist_ok=True)
arquivo_zip = destino / "REG_SAN_SGFCI-RECLAMACOES.zip"

print(f"Baixando {URL}")
urllib.request.urlretrieve(URL, arquivo_zip)
with zipfile.ZipFile(arquivo_zip) as z:
    z.extractall(destino)
    print("Extraídos:", ", ".join(z.namelist()))
