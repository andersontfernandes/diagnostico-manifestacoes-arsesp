# Planejamento de dados

## Objetivo

Entender o volume, a composição e a distribuição territorial das reclamações e solicitações de usuários de água e esgoto regulados pela Arsesp, e saber até onde a base permite comparar períodos e municípios.

## Perguntas

1. Quantas manifestações houve por ano e por categoria?
2. Quais motivos predominam?
3. Em quais municípios e regionais elas se concentram?
4. Como evoluem mês a mês?
5. Os dados são consistentes para comparar períodos?

## Fluxo de tratamento

1. **Ingestão:** download do ZIP e leitura dos CSV em Latin-1 com separador `;`.
2. **Limpeza:** remoção de linhas vazias e de cópias idênticas.
3. **Padronização:** data por extenso convertida para ano-mês; código IBGE como chave do município; grafias da unidade de negócio reduzidas às regionais da Sabesp.
4. **Agregação:** soma por município e mês (São Paulo e Guarujá vêm divididos por unidade), por regional e por ano.
5. **Validação:** preenchimento por mês e categoria, valores fora do padrão e comparação entre semestres por município.
6. **Publicação:** bases agregadas em `dados/processados/` e painel.

## Regras de qualidade

| Situação | Regra |
|---|---|
| Lacuna de preenchimento | Menos de 50% das linhas do mês trazem valor na categoria |
| Valor atípico | Total do mês acima de 5× a mediana dos meses regulares da categoria |
| Mudança de patamar | Reclamações de 2024 |
| Consistência municipal | Correlação entre o 1º e o 2º semestre de cada município |

## Dicionário de dados

O portal não publica dicionário. As descrições abaixo foram deduzidas dos nomes das colunas e precisam ser confirmadas com a Arsesp.

| Coluna | Tipo | Descrição |
|---|---|---|
| `COD_IBGE` | Chave | Código IBGE do município |
| `MUNICIPIO` | Texto | Nome do município (grafia varia) |
| `DATA` | Data | Primeiro dia do mês de referência, por extenso |
| `CONCESSIONARIA` | Texto | Prestador do serviço |
| `UN` | Texto | Unidade de negócio |
| `ANO_RELATORIO` | Número | Ano do relatório |
| `ReclQualAgua` | Reclamação | Qualidade da água |
| `ReclVazAgua` | Reclamação | Vazamento de água |
| `ReclCav` | Reclamação | Cavalete / hidrômetro |
| `ReclFAPP` | Reclamação | Falta de água e pouca pressão |
| `ReclValorConta` | Reclamação | Valor da conta |
| `ReclServEsg` | Reclamação | Serviços de esgoto |
| `ReclRepos` | Reclamação | Reposição de pavimento |
| `SolicVistoria` | Solicitação | Vistoria |
| `SolicCarroTq` | Solicitação | Caminhão-tanque |
| `SolicServLig` | Solicitação | Serviços de ligação |
| `SolicServCom` | Solicitação | Serviços comerciais |
| `SolicServComConAgua` | Solicitação | Serviços comerciais relacionados à conta de água |
| `NumSolicEstProj` | Solicitação | Estudos de projeto (viabilidade) |
| `OUTROS` | Solicitação | Outras solicitações (preenchido só em 2021) |

## Próximos passos

- Calcular reclamações por mil ligações, cruzando com o número de ligações por município (Arsesp ou SNIS).
- Confirmar com a Arsesp a mudança de método em 2024 e corrigir as linhas de jul–dez/2024.
- Obter o dicionário oficial e os critérios de cada categoria.
- Acrescentar prazos de atendimento e reincidência, se disponíveis.
- Automatizar a atualização quando a Arsesp publicar novos meses.
