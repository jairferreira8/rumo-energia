"""Testes automáticos da calculadora (rodar: python -m unittest discover -s energia/testes -t .)"""
import unittest

from energia import calculadora_energia as c


class TestConta(unittest.TestCase):
    def test_tarifa_soma_tusd_te(self):
        self.assertAlmostEqual(c.tarifa_sem_tributos(), 0.78938, places=5)

    def test_icms_faixas(self):
        self.assertEqual(c.aliquota_icms(90), 0.0)
        self.assertEqual(c.aliquota_icms(91), 0.12)
        self.assertEqual(c.aliquota_icms(200), 0.12)
        self.assertEqual(c.aliquota_icms(201), 0.18)

    def test_conta_100_kwh_calculo_manual(self):
        # 100 kWh x 0,78938 = 78,938 ; / (1 - 0,0533 - 0,12) = 95,49
        self.assertAlmostEqual(c.custo_conta(100), 95.49, places=2)

    def test_tarifa_social_ate_80_gratis(self):
        self.assertEqual(c.custo_conta(80, tarifa_social=True), 0)
        self.assertGreater(c.custo_conta(81, tarifa_social=True), 0)

    def test_custo_disponibilidade(self):
        # monofásico paga no mínimo 30 kWh
        self.assertAlmostEqual(c.custo_conta(10), c.custo_conta(30) * 1.0, places=6)

    def test_consumo_negativo(self):
        with self.assertRaises(ValueError):
            c.custo_conta(-1)


class TestAlternativas(unittest.TestCase):
    def test_eficiencia_reduz_conta(self):
        a = c.alternativa_eficiencia(189)
        self.assertLess(a["conta_depois"], a["conta_antes"])
        self.assertAlmostEqual(a["kwh_economizado_mes"], 9.9 + 25 + 87.9 * 3 / 8, delta=0.2)

    def test_solar_dimensiona_acima_do_minimo(self):
        s = c.alternativa_solar_propria(189)
        self.assertAlmostEqual(s["kwp"], 1.6)
        self.assertGreaterEqual(s["conta_depois_ano1"], c.custo_conta(30) - 0.01)

    def test_solar_sem_consumo_nao_dimensiona(self):
        self.assertEqual(c.alternativa_solar_propria(20)["kwp"], 0)

    def test_assinatura_sem_investimento(self):
        b2 = c.alternativa_assinatura(189)
        self.assertEqual(b2["investimento"], 0)
        self.assertGreater(b2["economia_mes"], 0)

    def test_co2(self):
        self.assertAlmostEqual(c.co2_kg(1000), 46.1, places=1)


class TestAssistente(unittest.TestCase):
    def test_reconhece_tarifa_social(self):
        self.assertIn("80 kWh", c.responder_energia("como consigo a tarifa social?"))

    def test_extrai_kwh(self):
        self.assertIn("250 kWh", c.responder_energia("gasto 250 kWh, vale placa solar?"))

    def test_fora_do_tema(self):
        self.assertIsNone(c.responder_energia("qual ônibus vai para a Sé?"))

    def test_sempre_tem_aviso(self):
        self.assertIn("não é garantida", c.responder_energia("como economizar energia"))


if __name__ == "__main__":
    unittest.main()
