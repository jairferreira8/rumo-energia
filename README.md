# Rumo: assistente cidadão com orientações de energia (SERS)

**Global Solution 2026.2 "CitizenTech", FIAP, turma 1CCPY. Case Citizen Assist AI.**
**Matéria deste repositório: Soluções em Energias Renováveis e Sustentáveis (SERS).** Responsável: Jair Ferreira dos Santos Neto (RM 569682).

| Integrante | RM |
|---|---|
| Jair Ferreira dos Santos Neto | 569682 |
| Arthur dos Santos Bezerra | 569721 |
| Carlos Henrique Fratezi | 571792 |

## A contribuição de SERS está na pasta [`energia/`](energia/)

O Rumo é um assistente de terminal, em Python, que orienta famílias de baixa renda de São Paulo sobre **moradia** (MCMV, aluguel social, regularização) e **transporte** (Bilhete Único, gratuidades). Ele responde com fonte oficial e grau de confiança, avisa que não é canal oficial e não pede dados pessoais.

Para SERS, acrescentamos orientações sobre **uso consciente de energia** para esse mesmo público, cuja necessidade é reduzir a conta de luz:

- **Análise de consumo e comparação de alternativas** para a mesma família e o mesmo período: (A) eficiência (LED, geladeira classe A, banho mais curto) + Tarifa Social; (B) energia solar fotovoltaica, em telhado próprio ou por assinatura/geração compartilhada.
- **Calculadora** com custos (tarifa Enel SP, ANEEL REH 3.596/2026), viabilidade (investimento, retorno, financiamento) e impacto ambiental (CO₂ com o fator do MCTI 2025).
- **Integração ao assistente**: opção 5 do menu ("Simular economia na conta de luz") e orientações da categoria "Energia em casa" (ENE01 a ENE03) na base `data/base_conhecimento.json`.

Tudo sobre a parte de energia (público, dados e premissas, cálculos, comparação, justificativas, referências, limitações e testes com usuários) está em **[`energia/README.md`](energia/README.md)**.

## Como executar

Requisito: Python 3.10+ (só biblioteca padrão). Na raiz do repositório:

```bash
python main.py                                       # assistente Rumo; escolha a opção 5 para energia
python -m energia.calculadora_energia                # só o simulador de energia
python -m unittest discover -s energia/testes -t .   # 15 testes da parte de energia
```

## Estrutura

| Caminho | O que é |
|---|---|
| `main.py`, `assistente.py`, `orientacao.py`, `base_conhecimento.py`, `data/` | Assistente Rumo (base comum da equipe) |
| **`energia/`** | **Contribuição de SERS**: calculadora, premissas com fonte, análise, testes |

> O Rumo é um projeto acadêmico. As estimativas de economia não são garantidas e o assistente não substitui os canais oficiais (Enel SP, ANEEL, Prefeitura de São Paulo).
