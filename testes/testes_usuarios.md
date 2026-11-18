# Testes com usuários: parte de energia

> **Regras:** não anotar nome, idade exata, endereço, CPF, NIS nem foto da conta. Identificar só como "Participante 1, 2, 3..." e o perfil geral (ex.: "mora em apartamento, já tem Tarifa Social").
> **Preencha só com o que aconteceu de verdade.** As colunas de resultado estão vazias de propósito.

## Como aplicar (10 a 15 min por pessoa)
1. Explique: "é um assistente de estudo, não é canal oficial; não precisa dar dados pessoais".
2. Rode `python main.py` e entregue o teclado.
3. Peça para a pessoa resolver as situações abaixo **sem ajuda**. Anote onde travou.
4. No fim, faça as 3 perguntas de opinião.

## Situações testadas
| # | Situação dada ao participante | O que se espera |
|---|---|---|
| S1 | "Sua conta veio 150 kWh. Descubra quanto dá para economizar." | Achar a opção 5 do menu, digitar 150 e entender a recomendação |
| S2 | "Pergunte ao Rumo se você tem direito a desconto na luz." | Receber a resposta da Tarifa Social com fonte e onde pedir |
| S3 | "Você mora em apartamento. Vale a pena energia solar?" | Entender que a opção é a assinatura solar, não o telhado |
| S4 | "Digite um valor errado (ex.: 'cem')." | O programa não quebra e explica |
| S5 | "Qual é o aparelho que mais gasta na sua casa, segundo o Rumo?" | Citar o chuveiro |

## Registro
| Participante (perfil geral) | Situação | Conseguiu? (sim/parcial/não) | Comentário (palavras da pessoa) | Ajuste feito |
|---|---|---|---|---|
| P1 – | S1 | | | |
| P1 – | S2 | | | |
| P1 – | S3 | | | |
| P2 – | S1 | | | |
| P2 – | S4 | | | |
| P3 – | S3 | | | |
| P3 – | S5 | | | |

## Perguntas de opinião (no fim)
1. O que ficou difícil de entender?
2. Você confiaria nesses números para tomar uma decisão? Por quê?
3. O que você mudaria?

## Ajustes feitos depois dos testes
Liste aqui cada mudança no código ou no texto e qual comentário a motivou. Exemplo de formato (não é resultado real): *"Trocamos 'payback' por 'tempo para se pagar' porque o participante não conhecia a palavra."*

- 

## Testes automáticos (complementam, não substituem os testes com pessoas)
`python -m unittest discover -s energia/testes -t .` → 15 testes (tarifa, faixas de ICMS, Tarifa Social, custo de disponibilidade, alternativas, CO₂, reconhecimento de perguntas, aviso sempre presente).
