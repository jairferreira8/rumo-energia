"""
Calculadora de energia do assistente Rumo (matéria SERS - Global Solution 2026.2).

Compara, para a MESMA família e o MESMO período (1 mês e 1 ano / vida útil),
duas alternativas para baixar a conta de luz:

  A) Eficiência e direitos: Tarifa Social + LED + geladeira eficiente + banho mais curto
  B) Energia solar fotovoltaica (fonte renovável):
     B1) sistema próprio no telhado (casa)
     B2) assinatura de energia solar / geração compartilhada (apartamento)

Todas as premissas (tarifa, tributos, fator de CO2, custos) ficam em
dados/premissas_energia.json, com origem e data. Este arquivo só faz contas.

IMPORTANTE: os resultados são ESTIMATIVAS. Não são garantia de economia.

Uso:
    python -m energia.calculadora_energia            -> menu interativo
    python -m energia.calculadora_energia --relatorio -> gera analise/resultados.md
"""

import json
import os
import re
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ_PREMISSAS = os.path.join(PASTA, "dados", "premissas_energia.json")

AVISO = ("Estimativa feita pelo Rumo com dados públicos (ANEEL, MCTI, MME). "
         "Não é canal oficial e a economia não é garantida: depende dos seus "
         "aparelhos, hábitos, tarifa do mês e bandeira tarifária.")


# ----------------------------------------------------------------------------
# Premissas
# ----------------------------------------------------------------------------
def carregar_premissas(caminho=ARQ_PREMISSAS):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


P = carregar_premissas()


def brl(valor):
    """Formata número como dinheiro brasileiro: 1234.5 -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def tarifa_sem_tributos():
    """TUSD + TE em R$/kWh (bandeira verde)."""
    t = P["tarifa"]
    return t["tusd_r_kwh"] + t["te_r_kwh"]


def aliquota_icms(kwh_total):
    """ICMS de SP: a faixa é escolhida pelo consumo total do mês."""
    for faixa in P["tributos"]["icms_faixas_sp"]:
        if faixa["ate_kwh"] is None or kwh_total <= faixa["ate_kwh"]:
            return faixa["aliquota"]
    return 0.18


def com_tributos(valor_sem_tributos, kwh_total):
    """Aplica PIS/COFINS + ICMS 'por dentro', como na conta de luz."""
    icms = aliquota_icms(kwh_total)
    pis_cofins = P["tributos"]["pis_cofins"]
    return valor_sem_tributos / (1 - pis_cofins - icms)


# ----------------------------------------------------------------------------
# Conta de luz
# ----------------------------------------------------------------------------
def custo_conta(kwh, tarifa_social=False, ligacao="monofasico"):
    """
    Valor estimado da conta (R$/mês) para um consumo em kWh.
    - Sem Tarifa Social: paga pelo menos o custo de disponibilidade.
    - Com Tarifa Social: os primeiros 80 kWh são grátis; o excedente é cobrado.
    Não inclui COSIP (iluminação pública) nem bandeira amarela/vermelha.
    """
    if kwh < 0:
        raise ValueError("consumo não pode ser negativo")
    minimo = P["solar"]["custo_disponibilidade_kwh"][ligacao]
    if tarifa_social:
        faturado = max(kwh - P["tarifa_social"]["kwh_gratis"], 0)
    else:
        faturado = max(kwh, minimo)
    return com_tributos(faturado * tarifa_sem_tributos(), kwh)


def consumo_aparelho(ap):
    """kWh/mês de um aparelho = potência (kW) x horas/dia x dias/mês."""
    if "kwh_mes_fixo" in ap:
        return ap["kwh_mes_fixo"]
    return ap["potencia_w"] / 1000 * ap["horas_dia"] * ap["dias_mes"]


def perfil_referencia():
    """Lista (nome, kWh/mês) da família de referência (perfil ESTIMADO)."""
    return [(ap["nome"], consumo_aparelho(ap))
            for ap in P["familia_referencia"]["aparelhos"]]


def co2_kg(kwh):
    """kg de CO2 da rede (SIN) associados a um consumo em kWh."""
    return kwh * P["fator_emissao"]["valor_kgco2_kwh"]


# ----------------------------------------------------------------------------
# Alternativa A - eficiência + Tarifa Social
# ----------------------------------------------------------------------------
def acoes_eficiencia():
    """Economia de cada ação, em kWh/mês, e custo de implantação (R$)."""
    ef = P["eficiencia"]
    perfil = dict(perfil_referencia())
    # LED: 6 lâmpadas de 20 W -> 9 W, 5 h/dia
    kwh_led = (20 - 9) * 6 * 5 * 30 / 1000
    # Geladeira antiga -> classe A
    kwh_gel = ef["consumo_geladeira_antiga_kwh_mes"] - ef["consumo_geladeira_nova_kwh_mes"]
    # Banho: de 8 para 5 minutos por pessoa (mesma potência)
    chuveiro = perfil["Chuveiro elétrico"]
    kwh_banho = chuveiro * (1 - 5 / 8)
    return [
        {"acao": "Trocar 6 lâmpadas por LED 9 W", "kwh_mes": kwh_led,
         "custo": 6 * ef["preco_led_r"], "vida_anos": ef["vida_util_led_anos"]},
        {"acao": "Trocar geladeira antiga por classe A (Procel)", "kwh_mes": kwh_gel,
         "custo": ef["preco_geladeira_r"], "vida_anos": ef["vida_util_geladeira_anos"]},
        {"acao": "Banho de 8 para 5 min por pessoa", "kwh_mes": kwh_banho,
         "custo": 0.0, "vida_anos": None},
    ]


def alternativa_eficiencia(kwh_base, tarifa_social=False, ligacao="monofasico"):
    acoes = acoes_eficiencia()
    resultado = []
    consumo = kwh_base
    for a in acoes:
        antes = custo_conta(consumo, tarifa_social, ligacao)
        consumo_novo = max(consumo - a["kwh_mes"], 0)
        depois = custo_conta(consumo_novo, tarifa_social, ligacao)
        economia = antes - depois
        payback_meses = (a["custo"] / economia) if economia > 0 and a["custo"] > 0 else (0 if a["custo"] == 0 else None)
        resultado.append({**a, "economia_mes": economia, "payback_meses": payback_meses,
                          "co2_kg_ano": co2_kg(a["kwh_mes"] * 12)})
        consumo = consumo_novo
    total_kwh = kwh_base - consumo
    return {
        "consumo_antes": kwh_base,
        "consumo_depois": consumo,
        "conta_antes": custo_conta(kwh_base, tarifa_social, ligacao),
        "conta_depois": custo_conta(consumo, tarifa_social, ligacao),
        "investimento": sum(a["custo"] for a in acoes),
        "kwh_economizado_mes": total_kwh,
        "co2_kg_ano": co2_kg(total_kwh * 12),
        "acoes": resultado,
    }


# ----------------------------------------------------------------------------
# Alternativa B1 - solar própria no telhado
# ----------------------------------------------------------------------------
def percentual_fio_b(ano_operacao, ano_inicio=2026):
    """Lei 14.300: 60% em 2026, 75% em 2027, 90% de 2028 em diante (premissa)."""
    ano = ano_inicio + ano_operacao - 1
    if ano <= 2026:
        return 0.60
    if ano == 2027:
        return 0.75
    return 0.90


def conta_com_solar(kwh, geracao, ligacao="monofasico", pct_fio_b=0.60, tarifa_social=False):
    """Conta do mês com geração solar (modelo simplificado da Lei 14.300)."""
    s = P["solar"]
    minimo = s["custo_disponibilidade_kwh"][ligacao]
    autoconsumo = min(geracao * s["fracao_autoconsumo"], kwh)
    injetado = geracao - autoconsumo
    da_rede = kwh - autoconsumo
    compensado = min(injetado, max(da_rede - minimo, 0))
    liquido = da_rede - compensado
    base = custo_conta(liquido, tarifa_social, ligacao)
    fio_b = compensado * s["fio_b_r_kwh"] * pct_fio_b
    return base + com_tributos(fio_b, liquido)


def alternativa_solar_propria(kwh_base, ligacao="monofasico", tarifa_social=False):
    s = P["solar"]
    minimo = s["custo_disponibilidade_kwh"][ligacao]
    kwp = max(kwh_base - minimo, 0) / s["geracao_kwh_por_kwp_mes"]
    kwp = round(kwp * 10) / 10  # arredonda para 0,1 kWp
    investimento = kwp * 1000 * s["custo_r_por_wp"]
    conta_antes = custo_conta(kwh_base, tarifa_social, ligacao)

    fluxo = []
    acumulado = -investimento
    payback_ano = None
    economia_total = 0.0
    geracao_total = 0.0
    for ano in range(1, s["vida_util_anos"] + 1):
        geracao = kwp * s["geracao_kwh_por_kwp_mes"] * (1 - s["degradacao_ao_ano"]) ** (ano - 1)
        conta_depois = conta_com_solar(kwh_base, geracao, ligacao, percentual_fio_b(ano), tarifa_social)
        economia_ano = (conta_antes - conta_depois) * 12 - s["manutencao_r_ano"]
        if ano == s["inversor_troca_ano"]:
            economia_ano -= s["inversor_troca_r"]
        acumulado += economia_ano
        economia_total += economia_ano
        geracao_total += geracao * 12
        if payback_ano is None and acumulado >= 0:
            payback_ano = ano
        fluxo.append((ano, economia_ano, acumulado))

    juros = s["financiamento_juros_mes"]
    n = s["financiamento_meses"]
    parcela = investimento * juros / (1 - (1 + juros) ** -n) if investimento > 0 else 0.0

    g1 = kwp * s["geracao_kwh_por_kwp_mes"]
    conta_ano1 = conta_com_solar(kwh_base, g1, ligacao, percentual_fio_b(1), tarifa_social)
    co2_rede = co2_kg(g1 * 12)
    co2_ciclo = g1 * 12 * P["emissao_ciclo_vida_fv"]["valor_kgco2eq_kwh"]
    return {
        "kwp": kwp,
        "investimento": investimento,
        "geracao_mes": g1,
        "conta_antes": conta_antes,
        "conta_depois_ano1": conta_ano1,
        "economia_mes_ano1": conta_antes - conta_ano1,
        "payback_anos": payback_ano,
        "parcela_financiamento": parcela,
        "meses_financiamento": n,
        "saldo_vida_util": acumulado,
        "economia_total_vida": economia_total,
        "co2_kg_ano_rede_evitado": co2_rede,
        "co2_kg_ano_liquido": co2_rede - co2_ciclo,
        "fluxo": fluxo,
    }


# ----------------------------------------------------------------------------
# Alternativa B2 - assinatura de energia solar (geração compartilhada)
# ----------------------------------------------------------------------------
def alternativa_assinatura(kwh_base, ligacao="monofasico", tarifa_social=False):
    s = P["solar"]
    minimo = s["custo_disponibilidade_kwh"][ligacao]
    conta_antes = custo_conta(kwh_base, tarifa_social, ligacao)
    if tarifa_social:
        kwh_pago = max(kwh_base - P["tarifa_social"]["kwh_gratis"], 0)
    else:
        kwh_pago = max(kwh_base - minimo, 0)
    # desconto sobre o valor da energia que seria paga à distribuidora
    valor_energia = com_tributos(kwh_pago * tarifa_sem_tributos(), kwh_base)
    economia = valor_energia * s["assinatura_desconto"]
    return {
        "investimento": 0.0,
        "conta_antes": conta_antes,
        "gasto_depois": conta_antes - economia,
        "economia_mes": economia,
        "kwh_renovavel_mes": kwh_pago,
        "co2_kg_ano": co2_kg(kwh_pago * 12),
    }


# ----------------------------------------------------------------------------
# Comparação completa
# ----------------------------------------------------------------------------
def comparar(kwh_base, tarifa_social=False, ligacao="monofasico"):
    return {
        "kwh": kwh_base,
        "tarifa_social": tarifa_social,
        "A_eficiencia": alternativa_eficiencia(kwh_base, tarifa_social, ligacao),
        "B1_solar_propria": alternativa_solar_propria(kwh_base, ligacao, tarifa_social),
        "B2_assinatura": alternativa_assinatura(kwh_base, ligacao, tarifa_social),
    }


def simular(kwh_base, tarifa_social=False, ligacao="monofasico"):
    """API para o assistente: devolve o dicionário da comparação e o texto pronto."""
    return {"dados": comparar(kwh_base, tarifa_social, ligacao),
            "texto": texto_comparacao(kwh_base, tarifa_social, ligacao)}


def texto_comparacao(kwh_base, tarifa_social=False, ligacao="monofasico"):
    c = comparar(kwh_base, tarifa_social, ligacao)
    a, b1, b2 = c["A_eficiencia"], c["B1_solar_propria"], c["B2_assinatura"]
    ts = "com Tarifa Social" if tarifa_social else "sem Tarifa Social"
    linhas = [
        f"Consumo informado: {kwh_base:.0f} kWh/mês ({ts}). Conta estimada hoje: {brl(a['conta_antes'])}/mês.",
        "",
        "A) Eficiência (LED + geladeira classe A + banho de 5 min)",
        f"   Consumo cai para {a['consumo_depois']:.0f} kWh/mês. Conta: {brl(a['conta_depois'])}/mês "
        f"(economia de {brl(a['conta_antes'] - a['conta_depois'])}/mês).",
        f"   Investimento: {brl(a['investimento'])} (a geladeira é quase tudo; pode sair grátis no programa da Enel).",
        f"   CO2 evitado: {a['co2_kg_ano']:.0f} kg/ano.",
    ]
    for ac in a["acoes"]:
        pb = "imediato" if ac["payback_meses"] == 0 else (
            f"{ac['payback_meses']:.0f} meses" if ac["payback_meses"] else "não se paga")
        linhas.append(f"   - {ac['acao']}: -{ac['kwh_mes']:.1f} kWh, {brl(ac['economia_mes'])}/mês, retorno {pb}")
    pb1 = f"{b1['payback_anos']} anos" if b1["payback_anos"] else "não se paga em 25 anos"
    linhas += [
        "",
        f"B1) Solar no telhado ({b1['kwp']:.1f} kWp, gera ~{b1['geracao_mes']:.0f} kWh/mês)",
        f"   Investimento: {brl(b1['investimento'])}. Conta no 1º ano: {brl(b1['conta_depois_ano1'])}/mês "
        f"(economia de {brl(b1['economia_mes_ano1'])}/mês). Retorno: {pb1}.",
        f"   Se financiar em {b1['meses_financiamento']} meses: parcela de ~{brl(b1['parcela_financiamento'])}/mês "
        f"(a economia mal cobre a parcela até quitar).",
        f"   CO2 da rede evitado: {b1['co2_kg_ano_rede_evitado']:.0f} kg/ano "
        f"(descontando a fabricação dos painéis: {b1['co2_kg_ano_liquido']:.0f} kg/ano).",
        "",
        "B2) Assinatura de energia solar (sem obra, serve para apartamento)",
        f"   Investimento: R$ 0. Gasto estimado: {brl(b2['gasto_depois'])}/mês "
        f"(economia de {brl(b2['economia_mes'])}/mês).",
        f"   {b2['kwh_renovavel_mes']:.0f} kWh/mês vindos de usina solar; CO2 da rede evitado: {b2['co2_kg_ano']:.0f} kg/ano.",
        "",
        recomendacao(c),
        "",
        AVISO,
    ]
    return "\n".join(linhas)


def recomendacao(c):
    if not c["tarifa_social"]:
        dica = ("1º passo: veja se sua família tem direito à Tarifa Social (CadÚnico com renda "
                "de até meio salário mínimo por pessoa). Os primeiros 80 kWh ficam de graça. ")
    else:
        dica = "Você já tem Tarifa Social: cada kWh que passa de 80 é cobrado inteiro, então economizar ainda vale. "
    dica += ("2º passo: ações de custo zero ou baixo (banho curto, LED). "
             "3º passo: geladeira eficiente (procure a troca gratuita da Enel). "
             "Solar própria só compensa para quem tem casa com telhado e dinheiro para investir; "
             "em apartamento, a opção renovável é a assinatura de energia solar.")
    return "Recomendação do Rumo: " + dica


# ----------------------------------------------------------------------------
# Integração com o assistente (respostas curtas por palavra-chave)
# ----------------------------------------------------------------------------
def extrair_kwh(texto, padrao=170):
    """Procura um número seguido de 'kwh' na pergunta (ex.: 'gasto 150 kWh')."""
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*kwh", texto.lower())
    if m:
        valor = float(m.group(1).replace(",", "."))
        if 0 < valor <= 2000:
            return valor
    return padrao


def responder_energia(pergunta):
    """Recebe a pergunta do usuário e devolve um texto, ou None se não for sobre energia."""
    p = pergunta.lower()
    if any(k in p for k in ("tarifa social", "luz de graça", "luz de graca", "desconto na luz", "desconto na conta")):
        ts = P["tarifa_social"]
        return (f"{ts['nome']}: {ts['regra']}\nQuem tem direito: {ts['quem_tem_direito']}\n"
                f"Como pedir: {ts['como_pedir']}\nFonte: {ts['origem']}\n{AVISO}")
    chaves = ("solar", "painel", "placa", "geladeira", "lâmpada", "lampada", "led", "chuveiro",
              "economizar", "conta de luz", "energia", "kwh")
    if any(k in p for k in chaves):
        return texto_comparacao(extrair_kwh(p), "tenho tarifa social" in p or "já tenho tarifa" in p)
    return None


def ler_numero(msg, padrao):
    texto = input(msg).strip().replace(",", ".")
    if not texto:
        return padrao
    try:
        valor = float(texto)
        if valor < 0 or valor > 2000:
            print("Valor fora do esperado; usando", padrao)
            return padrao
        return valor
    except ValueError:
        print("Não entendi o número; usando", padrao)
        return padrao


def menu_energia():
    """Menu chamado pelo assistente principal. Não pede dados pessoais."""
    print("\n=== Rumo | Energia em casa: simular economia na conta de luz ===")
    print("Não precisa informar nome, CPF nem endereço. Só o consumo em kWh (está na conta de luz).")
    kwh = ler_numero("Quantos kWh sua casa gasta por mês? [Enter = 170, só um exemplo] ", 170)
    ts = input("Sua conta já tem Tarifa Social? (s/n) [n] ").strip().lower().startswith("s")
    print()
    print(texto_comparacao(kwh, ts))
    print()


# ----------------------------------------------------------------------------
# Relatório da análise (vai para analise/resultados.md)
# ----------------------------------------------------------------------------
def gerar_relatorio():
    perfil = perfil_referencia()
    total = sum(k for _, k in perfil)
    out = ["# Resultados da análise de energia (gerado por calculadora_energia.py)", "",
           "> Valores ESTIMADOS a partir de dados/premissas_energia.json. Não são garantia.", "",
           f"Tarifa Enel SP B1 sem tributos: R$ {tarifa_sem_tributos():.5f}/kWh "
           f"(TUSD {P['tarifa']['tusd_r_kwh']} + TE {P['tarifa']['te_r_kwh']}), vigência {P['tarifa']['vigencia']}.", "",
           "## 1. Consumo da família de referência (perfil estimado)", "",
           "| Aparelho | kWh/mês | % |", "|---|---:|---:|"]
    for nome, k in perfil:
        out.append(f"| {nome} | {k:.1f} | {100 * k / total:.0f}% |")
    out.append(f"| **Total** | **{total:.1f}** | 100% |")
    out += ["", "## 2. Conta estimada por faixa de consumo", "",
            "| kWh/mês | Sem Tarifa Social | Com Tarifa Social |", "|---:|---:|---:|"]
    for k in (60, 80, 100, 150, 189, 250):
        out.append(f"| {k} | {brl(custo_conta(k))} | {brl(custo_conta(k, True))} |")
    for ts in (False, True):
        out += ["", f"## 3{'b' if ts else 'a'}. Comparação para {total:.0f} kWh/mês "
                f"({'COM' if ts else 'SEM'} Tarifa Social)", "", "```",
                texto_comparacao(round(total), ts), "```"]
        c = comparar(round(total), ts)
        a, b1, b2 = c["A_eficiencia"], c["B1_solar_propria"], c["B2_assinatura"]
        out += ["", "| Critério | A) Eficiência | B1) Solar própria | B2) Assinatura solar |",
                "|---|---:|---:|---:|",
                f"| Investimento | {brl(a['investimento'])} | {brl(b1['investimento'])} | R$ 0,00 |",
                f"| Economia/mês (1º ano) | {brl(a['conta_antes'] - a['conta_depois'])} | {brl(b1['economia_mes_ano1'])} | {brl(b2['economia_mes'])} |",
                f"| Economia/ano | {brl(12 * (a['conta_antes'] - a['conta_depois']))} | {brl(12 * b1['economia_mes_ano1'])} | {brl(12 * b2['economia_mes'])} |",
                f"| Retorno | ver ações | {b1['payback_anos'] or '> 25'} anos | imediato |",
                f"| CO2 evitado (kg/ano) | {a['co2_kg_ano']:.0f} | {b1['co2_kg_ano_rede_evitado']:.0f} (líq. {b1['co2_kg_ano_liquido']:.0f}) | {b2['co2_kg_ano']:.0f} |",
                f"| Serve para apartamento? | Sim | Não (só casa/condomínio) | Sim |"]
    b1 = alternativa_solar_propria(round(total))
    out += ["", "## 4. Fluxo de caixa da solar própria (sem Tarifa Social)", "",
            "| Ano | Economia no ano | Saldo acumulado |", "|---:|---:|---:|"]
    for ano, eco, acc in b1["fluxo"]:
        out.append(f"| {ano} | {brl(eco)} | {brl(acc)} |")
    out += ["", "## 5. Sensibilidade (sem Tarifa Social)", "",
            "| kWh/mês | Economia A | Solar: kWp | Solar: investimento | Solar: retorno (anos) | Economia B2 |",
            "|---:|---:|---:|---:|---:|---:|"]
    for k in (100, 150, 189, 250, 350):
        c = comparar(k)
        a, s, b2 = c["A_eficiencia"], c["B1_solar_propria"], c["B2_assinatura"]
        out.append(f"| {k} | {brl(a['conta_antes'] - a['conta_depois'])} | {s['kwp']:.1f} | "
                   f"{brl(s['investimento'])} | {s['payback_anos'] or '> 25'} | {brl(b2['economia_mes'])} |")
    caminho = os.path.join(PASTA, "analise", "resultados.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return caminho


if __name__ == "__main__":
    if "--relatorio" in sys.argv:
        print("Relatório salvo em", gerar_relatorio())
    else:
        menu_energia()
