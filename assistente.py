"""Classe Assistente: conversa com o cidadão, registra o histórico e calcula indicadores.

Composição: o Assistente TEM uma BaseConhecimento (self.base), e a base TEM
vários objetos Orientacao (self.base.orientacoes).
"""

import csv
import json
import time
from datetime import datetime

from base_conhecimento import nivel_confianca

CAMINHO_HISTORICO = "data/historico.json"
CAMINHO_CSV = "data/atendimentos.csv"
CAMPOS_HISTORICO = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
                    "ajudou", "tentativas", "tempo", "facilidade"]


def ler(mensagem):
    """input() que nunca derruba o programa (Ctrl+C ou Ctrl+D viram "0")."""
    try:
        return input(mensagem).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "0"


def tem_dado_pessoal(texto):
    """Bloqueia textos com 8 ou mais dígitos (CPF, telefone, RG) ou com @ (e-mail)."""
    digitos = sum(1 for c in texto if c.isdigit())
    return digitos >= 8 or "@" in texto


class Assistente:
    def __init__(self, nome, base, caminho_historico=CAMINHO_HISTORICO):
        self.nome = nome
        self.base = base                     # composição
        self.caminho_historico = caminho_historico
        self.historico = self._carregar_historico()
        self.sessao = []                     # atendimentos feitos nesta execução

    # ------------------------------------------------------------------ histórico
    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            return dados if isinstance(dados, list) else []
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            print("Aviso: historico.json estava corrompido. Um novo histórico será iniciado.")
            return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Aviso: não foi possível salvar o histórico ({e}).")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, inicio):
        """Grava um atendimento no histórico (lista de dicionários) e no arquivo."""
        registro = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "origem": origem,                         # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,           # None se não encontrou
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": round(time.time() - inicio, 1),  # segundos
            "facilidade": None,                       # preenchida ao sair
        }
        self.historico.append(registro)
        self.sessao.append(registro)
        self._salvar_historico()

    # ------------------------------------------------------------------ menus
    def iniciar(self):
        print("=" * 60)
        print(f"Olá! Eu sou o {self.nome}: o caminho para a sua casa e pela sua cidade.")
        print("Tiro dúvidas sobre moradia, transporte e conta de luz em São Paulo.")
        print("Não digite nome, CPF, telefone ou e-mail. Eu não preciso deles.")
        print("=" * 60)
        if self.base.erro:
            print(f"Aviso: {self.base.erro}")
            print("Sem a base eu não consigo responder, mas o programa continua aberto.")

        while True:
            print("\nMENU PRINCIPAL")
            print("1 - Fazer uma pergunta")
            print("2 - Ver assuntos por categoria")
            print("3 - Ver indicadores dos atendimentos")
            print("4 - Exportar atendimentos para CSV")
            print("5 - Simular economia na conta de luz")
            print("0 - Sair")
            opcao = ler("Escolha: ")
            if opcao == "1":
                self.perguntar()
            elif opcao == "2":
                self.navegar()
            elif opcao == "3":
                self.mostrar_indicadores()
            elif opcao == "4":
                self.exportar_csv()
            elif opcao == "5":
                self.simular_energia()
            elif opcao == "0":
                self.sair()
                break
            else:
                print("Opção inválida. Digite um número de 0 a 5.")

    def simular_energia(self):
        """Chama a calculadora da matéria de Energias Renováveis (pasta energia/).

        O try/except garante que o Rumo continua funcionando mesmo se o módulo faltar
        ou der erro: a busca por pontuação é o núcleo do assistente.
        """
        try:
            from energia.calculadora_energia import menu_energia
        except ImportError:
            print("O simulador de energia não está instalado nesta versão.")
            return
        except Exception as erro:   # ex.: arquivo de premissas ausente ou corrompido
            print(f"O simulador de energia não pôde ser carregado ({erro}).")
            return
        try:
            menu_energia()
        except (Exception, KeyboardInterrupt) as erro:   # falha do módulo não derruba o Rumo
            print(f"\nO simulador de energia foi interrompido ({erro or 'cancelado'}). Voltando ao menu.")

    def perguntar(self):
        """Atendimento por texto livre. Pode ter várias tentativas até resolver."""
        if not self.base.orientacoes:
            print("A base de conhecimento não foi carregada. Tente a opção mais tarde.")
            return

        tentativas = 0
        inicio = None
        ultima = None   # (pergunta, id_orientacao, encontrou) da última tentativa

        while True:
            print("\nEscreva sua dúvida com suas palavras (ou 0 para voltar).")
            pergunta = ler("Sua pergunta: ")

            if pergunta == "0":
                if ultima:   # a pessoa desistiu sem resolver
                    self.registrar("pergunta", ultima[0], ultima[1], ultima[2], False, tentativas, inicio)
                return
            if not pergunta or len(pergunta.replace(" ", "")) < 2:
                print("Não entendi. Escreva sua dúvida com pelo menos uma palavra.")
                continue
            if tem_dado_pessoal(pergunta):
                print("Por segurança, não aceito CPF, telefone, documentos ou e-mail.")
                print("Escreva a dúvida sem dados pessoais. Esta pergunta NÃO foi registrada.")
                continue

            if inicio is None:
                inicio = time.time()
            tentativas += 1

            resultados = self.base.buscar(pergunta)
            pontos = resultados[0][0] if resultados else 0
            confianca = nivel_confianca(pontos)

            if not confianca:
                print("\nNão encontrei uma orientação para essa pergunta.")
                print("Tente outras palavras (ex.: 'idoso ônibus', 'aluguel social', 'conta de luz')")
                print("ou volte e use a opção 2 para ver os assuntos por categoria:")
                print("  " + ", ".join(self.base.categorias()))
                ultima = (pergunta, None, False)
                continue

            melhor = resultados[0][1]
            alternativas = [o for p, o in resultados[1:3] if nivel_confianca(p)]
            self._mostrar_resultado(pergunta, resultados[0][0], melhor, confianca)
            ultima = (pergunta, melhor.id, True)

            resposta = self._perguntar_se_ajudou(alternativas)
            if resposta == "s":
                self.registrar("pergunta", pergunta, ultima[1], True, True, tentativas, inicio)
                print("Que bom! Atendimento registrado.")
                return
            if resposta.startswith("alt"):
                escolhida = alternativas[int(resposta[3:]) - 1]
                p = self.base.pontuar(pergunta, escolhida)
                escolhida.exibir(nivel_confianca(p))
                ultima = (pergunta, escolhida.id, True)
                if self._sim_ou_nao("Essa outra orientação ajudou? (s/n): ") == "s":
                    self.registrar("pergunta", pergunta, escolhida.id, True, True, tentativas, inicio)
                    print("Que bom! Atendimento registrado.")
                    return
            print("Tudo bem. Tente escrever de outro jeito, ou 0 para voltar.")

    def _mostrar_resultado(self, pergunta, pontos, orientacao, confianca):
        orientacao.exibir(confianca)
        _, chaves, titulo = self.base.detalhar(pergunta, orientacao)
        print(f"(Pontuação: {pontos} | palavras-chave: {', '.join(chaves) or '-'}"
              f" | no título: {', '.join(titulo) or '-'})")

    def _perguntar_se_ajudou(self, alternativas):
        """Devolve 's', 'n' ou 'alt1'/'alt2'. Repete até receber algo válido."""
        if alternativas:
            print("\nOutras orientações parecidas:")
            for i, alt in enumerate(alternativas, start=1):
                print(f"  {i} - {alt.titulo}")
        while True:
            texto = "Isso resolveu sua dúvida? (s = sim, n = não"
            if alternativas:
                texto += ", " + "/".join(str(i) for i in range(1, len(alternativas) + 1)) + " = ver outra"
            escolha = normalizar_resposta(ler(texto + "): "))
            if escolha in ("s", "n"):
                return escolha
            if escolha.isdigit() and 1 <= int(escolha) <= len(alternativas):
                return f"alt{escolha}"
            print("Resposta inválida.")

    def _sim_ou_nao(self, mensagem):
        while True:
            escolha = normalizar_resposta(ler(mensagem))
            if escolha in ("s", "n"):
                return escolha
            print("Responda s ou n.")

    def navegar(self):
        """Navegação numerada: categorias -> orientações -> orientação. 0 volta sempre."""
        if not self.base.orientacoes:
            print("A base de conhecimento não foi carregada.")
            return
        categorias = self.base.categorias()
        while True:
            print("\nCATEGORIAS")
            for i, categoria in enumerate(categorias, start=1):
                print(f"{i} - {categoria}")
            print("0 - Voltar")
            escolha = ler("Escolha a categoria: ")
            if escolha == "0":
                return
            if not escolha.isdigit() or not 1 <= int(escolha) <= len(categorias):
                print("Opção inválida.")
                continue
            categoria = categorias[int(escolha) - 1]
            self._navegar_categoria(categoria)

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n{categoria.upper()}")
            for i, orientacao in enumerate(orientacoes, start=1):
                print(f"{i} - {orientacao.titulo}")
            print("0 - Voltar")
            escolha = ler("Escolha o assunto: ")
            if escolha == "0":
                return
            if not escolha.isdigit() or not 1 <= int(escolha) <= len(orientacoes):
                print("Opção inválida.")
                continue
            inicio = time.time()
            orientacao = orientacoes[int(escolha) - 1]
            orientacao.exibir()
            ajudou = self._sim_ou_nao("Isso resolveu sua dúvida? (s/n): ") == "s"
            self.registrar("categoria", categoria, orientacao.id, True, ajudou, 1, inicio)
            print("Atendimento registrado. Digite 0 para voltar ou escolha outro assunto.")

    # ------------------------------------------------------------------ indicadores e CSV
    def indicadores(self):
        """Calcula os indicadores a partir de self.historico. Devolve um dicionário."""
        total = len(self.historico)
        if total == 0:
            return None
        encontrados = sum(1 for r in self.historico if r["encontrou"])
        ajudaram = sum(1 for r in self.historico if r["ajudou"])
        tempo_total = sum(r["tempo"] for r in self.historico)
        tentativas_total = sum(r["tentativas"] for r in self.historico)
        notas = [r["facilidade"] for r in self.historico if r.get("facilidade")]
        sem_solucao = [r["pergunta"] for r in self.historico if not r["ajudou"]]
        return {
            "total": total,
            "perc_encontradas": round(encontrados / total * 100, 1),
            "perc_ajudou": round(ajudaram / total * 100, 1),
            "tempo_medio": round(tempo_total / total, 1),
            "tentativas_media": round(tentativas_total / total, 1),
            "facilidade_media": round(sum(notas) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        ind = self.indicadores()
        if ind is None:
            print("Ainda não há atendimentos registrados.")
            return
        print("\nINDICADORES")
        print(f"Atendimentos registrados: {ind['total']}")
        print(f"Respostas encontradas: {ind['perc_encontradas']}%")
        print(f"Atendimentos em que ajudou: {ind['perc_ajudou']}%")
        print(f"Tempo médio: {ind['tempo_medio']} segundos")
        print(f"Tentativas por atendimento: {ind['tentativas_media']}")
        facil = ind["facilidade_media"]
        print(f"Facilidade média (1 a 5): {facil if facil is not None else 'sem notas ainda'}")
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for pergunta in ind["sem_solucao"]:
                print(f"  - {pergunta}")
        else:
            print("  nenhuma")
        ler("\nEnter (ou 0) para voltar: ")

    def exportar_csv(self, caminho=CAMINHO_CSV):
        if not self.historico:
            print("Não há atendimentos para exportar.")
            return
        try:
            # utf-8-sig e ponto e vírgula: o Excel em português abre certinho.
            with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_HISTORICO,
                                          delimiter=";", extrasaction="ignore")
                escritor.writeheader()
                for registro in self.historico:
                    escritor.writerow(registro)
            print(f"{len(self.historico)} atendimentos exportados para {caminho}.")
        except OSError as e:
            print(f"Não foi possível exportar o CSV ({e}).")

    def sair(self):
        """Pede a nota de facilidade e grava nos atendimentos desta execução."""
        if self.sessao:
            while True:
                nota = ler("\nDe 1 a 5, quão fácil foi usar o Rumo? (0 para pular): ")
                if nota == "0":
                    break
                if nota in ("1", "2", "3", "4", "5"):
                    for registro in self.sessao:
                        registro["facilidade"] = int(nota)
                    self._salvar_historico()
                    print("Obrigado pela nota!")
                    break
                print("Digite um número de 1 a 5.")
        print(f"Até logo! {self.nome}: o caminho para a sua casa e pela sua cidade.")


def normalizar_resposta(texto):
    """Aceita 'S', 'sim', 'Não' etc. e devolve a primeira letra (ou o número)."""
    texto = texto.strip().lower()
    if texto in ("sim", "s", "ss"):
        return "s"
    if texto in ("nao", "não", "n"):
        return "n"
    return texto
