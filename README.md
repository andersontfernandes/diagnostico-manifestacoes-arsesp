# Diagnóstico das manifestações de usuários · Arsesp

Análise das reclamações e solicitações de usuários dos serviços de água e esgoto regulados pela Arsesp (Agência Reguladora de Serviços Públicos do Estado de São Paulo), de jan/2021 a dez/2024, com planejamento de dados, apuração de qualidade e painel.

> Trabalho de análise feito com dados abertos. Não é publicação oficial da Arsesp.

## Fonte

- **Conjunto:** “Manifestações de usuários”, Gerência de Fiscalização Comercial e Indicadores da Arsesp
- **Portal:** [Dados Abertos SP](https://dadosabertos.sp.gov.br/dataset/manifestacoes-de-usuarios-prestadores)
- **Arquivo:** `REG_SAN_SGFCI-RECLAMACOES.zip` (dois CSV: reclamações e solicitações)
- **Granularidade:** município × mês × prestador
- **Licença:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Estrutura

```
scripts/
  baixar_dados.py   baixa o ZIP da Arsesp e extrai os CSV
  perfil.py         perfil rápido das colunas (vazios, categorias, somas)
  tratar.py         limpeza, padronização, agregação e regras de qualidade
dados/
  processados/      bases agregadas usadas pelo painel (JSON)
painel/
  index.html        página do painel
docs/
  planejamento.md   objetivo, perguntas, fluxo e dicionário de dados
  apuracao.md       problemas encontrados e tratamento aplicado
```

## Como reproduzir

Requer só Python 3.10+ (biblioteca padrão).

```bash
python scripts/baixar_dados.py dados/brutos
python scripts/tratar.py dados/brutos dados/processados
```

Os CSV brutos ficam em `dados/brutos/`, fora do controle de versão.

## Bases geradas

| Arquivo | Conteúdo |
|---|---|
| `mensal.json` | Total estadual por mês, tipo e categoria, com municípios informantes e situação de qualidade |
| `anual.json` | Total anual por tipo e categoria, com o número de meses regulares |
| `municipios_2023.json` | Reclamações de 2023 por município e categoria, com regional padronizada |
| `regional.json` | Reclamações por regional e ano, 2021 a 2023 |
| `apuracao.json` | Registro das verificações de qualidade |

## Principais achados da apuração

- **Lacunas:** reposição de pavimento está vazia de jul a dez/2022 e qualidade da água vem quase vazia desde jul/2023.
- **Mudança de patamar:** em 2024 as reclamações mais que dobram em todas as categorias a partir de janeiro, provavelmente por mudança de método.
- **Linhas desalinhadas:** de jul a dez/2024 os valores não correspondem aos municípios. A correlação entre semestres cai de 0,99 (2023) para 0,12 (2024). Esse período só deve ser usado no total estadual.
- **Padronização:** 557 grafias para 395 municípios e 84 grafias de unidade de negócio, reduzidas a 15 regionais da Sabesp.

Detalhes em [docs/apuracao.md](docs/apuracao.md).

## Painel

`painel/index.html` foi escrito para o tipo de painel “Dashboard” do Claude (usa o objeto `dash` para ler as bases). Ele não abre sozinho no navegador.
