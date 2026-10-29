# Apuração de qualidade

Verificações feitas nos CSV originais da Arsesp e o tratamento aplicado. Gerado a partir de `dados/processados/apuracao.json`.

| Etapa | Verificação | Resultado | Tratamento |
|---|---|---:|---|
| Ingestão | Linhas lidas (cada arquivo) | 18.180 | Arquivos CSV em Latin-1, separador ";". |
| Limpeza | Linhas sem município, data ou valores | 138 | Removidas (soma dos dois arquivos). |
| Limpeza | Linhas idênticas repetidas | 0 | Mantida uma cópia. |
| Limpeza | Linhas válidas de reclamações | 18.111 | Base para todas as análises de reclamações. |
| Padronização | Municípios distintos (código IBGE) | 394 | Código IBGE usado como chave; nome mais frequente em maiúsculas. |
| Padronização | Municípios com mais de uma grafia | 163 | Ex.: "Aspásia" e "ASPASIA" unificados pelo código IBGE. |
| Padronização | Grafias distintas da unidade de negócio | 84 | Reduzidas a 15 unidades regionais da Sabesp + outras concessionárias. |
| Padronização | Meses com data escrita por extenso | 48 | "sábado, 1 de maio de 2021" convertido para 2021-05. |
| Agregação | Meses em que um município aparece em várias linhas | 58 | São Paulo e Guarujá vêm divididos por unidade; valores somados por município e mês. |
| Cobertura | Combinações mês × categoria com menos de 50% de preenchimento | 150 | Marcadas como lacuna; ex.: reposição de pavimento jul–dez/2022, qualidade da água a partir de jul/2023. |
| Cobertura | Combinações mês × categoria acima de 5× a mediana | 35 | Marcadas como atípicas; concentradas em solicitações de jul–dez/2021. |
| Consistência | Correlação municipal 1º × 2º semestre de 2023 (×1000) | 987 | Referência: municípios mantêm o mesmo patamar entre semestres. |
| Consistência | Correlação municipal 1º × 2º semestre de 2024 (×1000) | 125 | Valores de jul–dez/2024 não correspondem aos municípios. Usados só no total estadual. |

## Observação sobre 2024

Comparando o 1º com o 2º semestre de cada município, a correlação é 0,99 em 2023 e cai para 0,12 em 2024. No 2º semestre de 2024, municípios pequenos aparecem com dezenas de milhares de reclamações e a capital quase some, enquanto o total estadual segue no mesmo patamar. Isso indica linhas trocadas. Esse período só deve ser usado no total estadual até a Arsesp confirmar.
