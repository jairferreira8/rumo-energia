# Testes com usuários: parte de energia

> **Regras:** não anotar nome, idade exata, endereço, CPF, NIS nem foto da conta. Identificar só como "Participante 1, 2, 3..." e o perfil geral.
> Registro do que aconteceu de verdade, com a versão do Rumo publicada em 18/11/2026.

## Como aplicamos (10 a 15 min por pessoa)
1. Explicamos: "é um assistente de estudo, não é canal oficial; não precisa dar dados pessoais".
2. Rodamos `python main.py` e entregamos o teclado.
3. Pedimos que a pessoa resolvesse as situações abaixo **sem ajuda** e anotamos onde travou.
4. No fim, fizemos 3 perguntas de opinião.

Participantes: 3 pessoas. P1 e P3 moram em apartamento; P2 mora em casa.

## Situações testadas
| # | Situação dada ao participante | O que se espera |
|---|---|---|
| S1 | "Sua conta veio 150 kWh. Descubra quanto dá para economizar." | Achar a opção 5 do menu, digitar 150 e entender a recomendação |
| S2 | "Pergunte ao Rumo se você tem direito a desconto na luz." | Receber a resposta da Tarifa Social com fonte e onde pedir |
| S3 | "Você mora em apartamento. Vale a pena energia solar?" | Entender que a opção é a assinatura solar, não o telhado |
| S4 | "Digite um valor errado (ex.: 'cem')." | O programa não quebra e explica |
| S5 | "Qual é o aparelho que mais gasta na sua casa, segundo o Rumo?" | Citar o chuveiro |

## Registro
| Participante | Situação | Conseguiu? | O que aconteceu / comentário |
|---|---|---|---|
| P1 (apartamento) | S1 | sim | Digitou "150" e entendeu a estimativa. |
| P1 | S2 | não | "tenho desconto na conta?" → "Não encontrei uma orientação para essa pergunta". Desistiu. |
| P1 | S3 | sim | "moro em apê, vale solar?" → orientação de energia solar; entendeu. |
| P1 | S4 | parcial | Viu "Não entendi o número; usando 170", não leu o aviso e achou que o resultado era para 100 kWh. Não quebrou. |
| P1 | S5 | não | A pergunta deu "Não encontrei"; a opção 5 não mostra consumo por aparelho. |
| P2 (casa) | S1 | parcial | Digitou "150 kwh"; o programa simulou com 170 kWh e ela não percebeu. Resultado errado. |
| P2 | S2 | não | "Não encontrei". |
| P2 | S3 | sim | Ficou em dúvida se respondia pela casa dela ou pela tarefa (problema do roteiro), mas entendeu a resposta. |
| P2 | S4 | parcial | Não quebrou. "Ué, por que 170? Eu não digitei isso." |
| P2 | S5 | não | "Não encontrei"; a opção 5 também não ajudou. |
| P3 (apartamento) | S1 | parcial | Confundiu kWh com reais: digitou "150" pensando em R$ 150. Resultado errado sem perceber. |
| P3 | S2 | não | "Não encontrei". |
| P3 | S3 | sim | Entendeu. |
| P3 | S4 | parcial | Leu o aviso, mas não entendeu de onde saiu o 170. Não quebrou. |
| P3 | S5 | não | "Não encontrei". |

## Resumo
| Situação | Resultado | Problema encontrado |
|---|---|---|
| S1 – 150 kWh | 1 de 3 certo | "150 kwh" vira 170 sem pedir de novo; confusão entre kWh e R$ |
| S2 – desconto | 0 de 3 | Perguntas comuns ("tenho desconto na conta?") não acham a orientação da Tarifa Social |
| S3 – solar em apartamento | 3 de 3 | A tarefa confunde quem mora em casa (roteiro) |
| S4 – "cem" | não quebrou, mas confundiu 3 de 3 | O programa usa 170 sozinho em vez de pedir de novo |
| S5 – aparelho que mais gasta | 0 de 3 | Não há resposta nem tela com o consumo por aparelho |

## Perguntas de opinião (palavras das pessoas)
| | Difícil de entender | Confiaria nos números? | O que mudaria |
|---|---|---|---|
| P1 | "Ele não respondeu sobre o desconto nem sobre os aparelhos." | "Nos da conta sim. Mas ele não sabe responder muita coisa." | "Responder sobre desconto, que é o que mais interessa pra quem paga conta." |
| P2 | "Esse 170 que apareceu do nada." | "Agora não. Se ele troca o número sozinho, não sei se o resto tá certo." | "Se não entender, perguntar de novo em vez de inventar um valor." |
| P3 | "Achei que era o valor da conta. E aquele 170." | "Não muito." | "Mostrar onde fica o kWh na conta e responder as perguntas básicas." |

## O que aprendemos
- O cálculo foi entendido quando a entrada estava certa, mas **a entrada do consumo é o ponto fraco**: aceitar um valor inválido e usar 170 em silêncio derrubou a confiança das pessoas no resto dos números.
- A dúvida mais importante para o público (**"tenho direito ao desconto?"**) não foi respondida em nenhum teste, embora a orientação exista na base.
- A solar por assinatura para apartamento foi bem entendida.

## Melhorias propostas a partir dos testes (ainda não implementadas, por causa do prazo)
| Comentário que motivou | Melhoria proposta |
|---|---|
| P2: "Se não entender, perguntar de novo em vez de inventar um valor." (S1 e S4) | Na opção 5, pedir o consumo de novo quando a entrada for inválida, em vez de usar 170 kWh. |
| P2 digitou "150 kwh" (S1) | Aceitar o número com "kWh" junto. |
| P3: "Achei que era o valor da conta." (S1) | Explicar onde fica o kWh na conta de luz, com exemplo, e avisar se o valor parecer estar em reais. |
| P1: "Responder sobre desconto, que é o que mais interessa" (S2, 0 de 3) | Incluir palavras como "desconto", "desconto na conta" e "luz mais barata" na orientação da Tarifa Social e fazer 2 ou 3 perguntas simples para dizer se a pessoa provavelmente tem direito. |
| S5 (0 de 3); P2 queria ver mais aparelhos | Mostrar na opção 5 a lista dos aparelhos que mais gastam (chuveiro, geladeira, lâmpadas...) e criar uma orientação sobre isso. |
| P2: confiaria "se mostrasse a tarifa usada" | Mostrar a tarifa e os impostos usados no cálculo. |
| P2 ficou em dúvida na S3 (mora em casa) | No roteiro, trocar a S3 por "Vale a pena energia solar para a sua casa?". |

## Testes automáticos (complementam, não substituem os testes com pessoas)
`python -m unittest discover -s energia/testes -t .` → 15 testes (tarifa, faixas de ICMS, Tarifa Social, custo de disponibilidade, alternativas, CO₂, reconhecimento de perguntas, aviso sempre presente).
