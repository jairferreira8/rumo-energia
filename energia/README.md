# Energia em casa: contribuição de SERS ao assistente Rumo

**Matéria:** Soluções em Energias Renováveis e Sustentáveis (SERS), Global Solution 2026.2 "CitizenTech", FIAP, turma 1CCPY
**Responsável:** Jair Ferreira dos Santos Neto (RM 569682)
**Equipe:** Jair Ferreira dos Santos Neto (RM 569682), Arthur dos Santos Bezerra (RM 569721), Carlos Henrique Fratezi (RM 571792)

Tudo o que está nesta pasta `energia/` é a parte de SERS. O restante do repositório (assistente, base de moradia e transporte) é de outras matérias.

## 1. Contexto

| | |
|---|---|
| **Público** | Famílias de baixa renda em moradia popular de São Paulo (Minha Casa Minha Vida Faixa 1, conjuntos habitacionais, aluguel social), clientes da Enel SP. É o mesmo público que o Rumo já atende em Moradia. |
| **Necessidade energética** | Energia elétrica residencial: chuveiro, geladeira, iluminação, TV. O problema real é o **peso da conta de luz no orçamento**: a tarifa da Enel SP subiu em média 10,18% em jul/2026. |
| **Como o Rumo ajuda** | Explica a Tarifa Social (que muita família com direito não usa), mostra quais aparelhos pesam mais, simula quanto cada ação economiza em R$ e kWh e compara eficiência com energia solar, sempre com fonte, aviso de estimativa e sem pedir dados pessoais. |

## 2. Funcionalidades de energia

1. **Simulador no menu** (`menu_energia()`): o usuário digita só o consumo em kWh da conta e se já tem Tarifa Social; o Rumo mostra a conta estimada e as alternativas lado a lado.
2. **Respostas por palavra-chave** (`responder_energia(pergunta)`): reconhece perguntas como "vale a pena placa solar se gasto 250 kWh?" ou "como pego a tarifa social?" e devolve a resposta com fonte e aviso. Devolve `None` se a pergunta não for sobre energia.
3. **`simular(kwh, tarifa_social)`**: devolve os números da comparação (dicionário) e o texto pronto, para o assistente usar como quiser.
4. **Orientações "Energia em casa" na base principal** (`data/base_conhecimento.json`, ids ENE01 a ENE03): Tarifa Social (80 kWh grátis), Desconto Social e energia solar/assinatura solar (alternativa B). Os textos usam as mesmas premissas da calculadora. Versões mais longas e orientações extras (eficiência, preço do kWh) estão em `dados/base_conhecimento_energia.json`.

## 3. Como executar

Requisito: Python 3.10+ (só biblioteca padrão). A partir da raiz do repositório:

```bash
python -m energia.calculadora_energia               # simulador interativo
python -m energia.calculadora_energia --relatorio   # recalcula analise/resultados.md
python -m unittest discover -s energia/testes -t .  # 15 testes automáticos
```

Pelo assistente principal (`python main.py`): opção **"5 - Simular economia na conta de luz"** do menu (chama `energia.calculadora_energia.menu_energia()`).

## 4. Dados, origem e premissas

Todas as premissas estão em [`dados/premissas_energia.json`](dados/premissas_energia.json), cada uma com **valor, unidade, origem, data e tipo** (`oficial`, `secundaria` ou `estimativa`). Principais:

| Dado | Valor | Origem | Tipo |
|---|---|---|---|
| Tarifa B1 residencial Enel SP | TUSD R$ 0,47242 + TE R$ 0,31696 = **R$ 0,78938/kWh** sem tributos | ANEEL, REH 3.596/2026, vigência 04/07/2026 a 03/07/2027 (conferido no PDF da resolução em 18/11/2026) | oficial |
| ICMS SP residencial | 0% até 90 kWh; 12% de 91 a 200 kWh; 18% acima | Lei SP 12.185/2006; LC 194/2022 | oficial |
| PIS/COFINS | 5,33% (PIS 0,95% + COFINS 4,38%) | conta de luz real da Enel SP, conferida em 18/11/2026 (varia um pouco por mês) | conta real |
| Tarifa Social | 80 kWh/mês grátis | Lei 15.235/2025 (MP 1.300/2025), desde 05/07/2025 | oficial |
| Fator de emissão da rede (SIN) | **0,0461 kg CO₂/kWh** (média 2025) | MCTI/SIRENE, planilha de fatores de emissão, média anual 2025 (conferida em 18/11/2026) | oficial |
| Emissão de ciclo de vida da solar em telhado | 0,041 kg CO₂eq/kWh | IPCC AR5, Anexo III (2014) | oficial |
| Geração solar em SP | 100 kWh por kWp por mês | 4,5 kWh/m²·dia × 30 × PR 0,75 | **estimativa** |
| Preço do sistema solar | R$ 3,20/Wp | Greener 1º sem./2025 (R$ 2,84/Wp para 4 kWp) + 13% por ser sistema pequeno | **estimativa** |
| Fio B (Lei 14.300) | 60% em 2026, 75% em 2027, 90% de 2028 em diante; R$ 0,20/kWh | Lei 14.300/2022, art. 27; valor em R$ estimado | oficial / **estimativa** |
| Consumo dos aparelhos | ver perfil abaixo | potência × horas × dias; geladeira pela média IDEC | **estimativa** |

**Período de comparação:** 1 mês (conta), 1 ano (economia e CO₂) e 25 anos (vida útil da solar). Tarifa mantida constante em valores de 2026 (sem inflação nem reajustes futuros), o que é conservador para a solar.

### Família de referência (perfil ESTIMADO, não é uma família real)

4 pessoas, apartamento popular em SP, ligação monofásica:

| Aparelho | Conta | kWh/mês | % |
|---|---|---:|---:|
| Chuveiro 5.500 W | 5,5 kW × 0,533 h/dia (4 banhos de 8 min) × 30 | 87,9 | 47% |
| Geladeira 2 portas, +10 anos | estimado (IDEC: média 48 kWh/mês para 2 portas) | 55,0 | 29% |
| 6 lâmpadas fluorescentes de 20 W | 0,12 kW × 5 h × 30 | 18,0 | 10% |
| TV 100 W | 0,1 kW × 5 h × 30 | 15,0 | 8% |
| Máquina de lavar + ferro | estimado | 8,0 | 4% |
| Outros | estimado | 5,0 | 3% |
| **Total** | | **188,9** | |

## 5. Cálculos e comparação (mesma família, 189 kWh/mês)

Fórmula da conta: `conta = kWh faturados × 0,78938 ÷ (1 − PIS/COFINS − ICMS)`.
Exemplo: 189 kWh × 0,78938 = R$ 149,19; ÷ (1 − 0,0533 − 0,12) = **R$ 180,47/mês**.

| Critério | A) Eficiência (LED + geladeira A + banho 5 min) | B1) Solar no telhado (1,6 kWp) | B2) Assinatura solar |
|---|---:|---:|---:|
| Investimento | R$ 2.672 (R$ 72 sem a geladeira) | R$ 5.120 | R$ 0 |
| Conta depois (sem Tarifa Social) | R$ 115,65 | R$ 39,08 | R$ 157,69 |
| Economia/mês | **R$ 64,82** | **R$ 141,38** | **R$ 22,77** |
| Retorno | LED 8 meses; banho imediato; geladeira 9 anos (ou grátis pela Enel) | 4 anos à vista; financiado (60× de R$ 140) empata com a economia | imediato |
| CO₂ evitado | 38 kg/ano | 89 kg/ano (≈10 kg/ano líquido do ciclo de vida) | 88 kg/ano |
| Viabilidade para o público | Alta: barato, serve em apartamento | Baixa: precisa de casa com telhado e capital ou crédito | Média: sem obra, mas depende de contrato e de a empresa aceitar o cliente |

Com **Tarifa Social** a conta cai de R$ 180,47 para R$ 104,08 sem investimento nenhum. Depois disso, a eficiência ainda economiza R$ 64,82/mês (cada kWh acima de 80 é cobrado cheio), e a solar própria passa a se pagar em 6 anos.

Tabelas completas (faixas de consumo, fluxo de caixa de 25 anos, sensibilidade de 100 a 350 kWh): [`analise/resultados.md`](analise/resultados.md). Justificativas: [`analise/justificativas.md`](analise/justificativas.md).

## 6. Recomendação do Rumo

1. **Tarifa Social primeiro**: maior economia (≈R$ 76/mês na família de referência) e custo zero.
2. **Hábitos e LED**: banho de 5 min e lâmpadas LED, R$ 41/mês por R$ 72.
3. **Geladeira eficiente**: vale a pena se vier pelo programa de troca da Enel; comprada, demora ~9 anos para se pagar.
4. **Solar**: é a maior economia em R$, mas só para quem tem casa com telhado e dinheiro à vista. Em apartamento, a opção renovável é a assinatura solar.

## 7. Limitações (leia antes de usar os números)

- Tudo é **estimativa**: economia e geração **não são garantidas**. Dependem dos aparelhos reais, hábitos, clima, bandeira e reajustes.
- Não incluímos COSIP (iluminação pública), bandeiras amarela/vermelha, inflação, nem a cobrança de ICMS sobre a energia compensada na solar.
- A Tarifa Social foi modelada como 80 kWh grátis e o resto cobrado cheio; o "Desconto Social" da Lei 15.235/2025 (famílias de meio a 1 salário mínimo por pessoa) não foi calculado.
- O modelo da solar é simplificado (autoconsumo fixo de 30%, geração média sem variação mensal, Fio B estimado em R$).
- No Brasil a rede já é muito limpa (~46 g CO₂/kWh), por isso o CO₂ evitado é pequeno. A solar em telhado tem ~41 g CO₂eq/kWh no ciclo de vida: o ganho ambiental líquido é pequeno e não deve ser exagerado.
- O Rumo não é canal oficial da Enel, ANEEL ou Prefeitura.

## 8. Referências

- ANEEL. Resolução Homologatória nº 3.596, de 30/06/2026: reajuste tarifário anual da Enel Distribuição São Paulo. PDF da resolução publicado pela Enel SP (enel.com.br). Conferido em 18/11/2026.
- ANEEL. Resolução Normativa nº 1.000/2021 (custo de disponibilidade).
- BRASIL. Lei nº 14.300, de 06/01/2022 (marco legal da micro e minigeração distribuída), art. 27.
- BRASIL. Lei nº 15.235/2025 (conversão da MP 1.300/2025) e MME, *Gratuidade até 80 kWh mensais para beneficiários da TSEE começa em julho* (gov.br/mme), 2025.
- SÃO PAULO (Estado). Lei nº 12.185/2006 e Decreto nº 50.473/2006 (ICMS sobre energia residencial).
- MCTI/SIRENE. *Fatores de emissão de CO₂ da geração de energia elétrica no SIN*, planilha Ano Base 2025, e Nota Técnica de jun/2025 (gov.br/mcti). Conferido em 18/11/2026.
- IPCC. *AR5, WG III, Annex III: Technology-specific cost and performance parameters*, 2014.
- Greener. *Estudo Estratégico de Geração Distribuída*, 1º semestre de 2025 (via Canal Solar/eixos).
- IDEC. Dicas para economizar na conta de luz (consumo médio de refrigeradores).
- CRESESB/CEPEL. SunData; INPE. *Atlas Brasileiro de Energia Solar*, 2ª ed., 2017.
- Enel Brasil. Programa *Enel Compartilha Eficiência* (troca de geladeiras e lâmpadas), notícias de 2026.

## 9. Testes com usuários

Roteiro, situações testadas, comentários e ajustes: [`testes/testes_usuarios.md`](testes/testes_usuarios.md). Nenhum dado pessoal é registrado.
