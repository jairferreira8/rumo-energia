"""Classe BaseConhecimento: carrega o JSON e faz a busca por pontuação."""

import json

from orientacao import Orientacao, CAMPOS_OBRIGATORIOS

# Dicionário usado pela função normalizar() para tirar os acentos.
ACENTOS = {
    "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ç": "c", "ñ": "n",
}

# Pesos da busca (ajustáveis; explicados no README).
PESO_PALAVRA_CHAVE = 3   # palavra-chave encontrada na pergunta
PESO_TITULO = 1          # palavra da pergunta (4+ letras) que aparece no título
TAMANHO_MINIMO_TITULO = 4
# Palavras comuns de 4+ letras que não ajudam a achar o assunto no título.
PALAVRAS_IGNORADAS = {"para", "pelo", "pela", "mais", "esta", "isso", "sobre"}
LIMITE_ALTA = 6          # 6 ou mais pontos  -> confiança ALTA
LIMITE_MEDIA = 3         # 3 a 5 pontos       -> confiança MÉDIA  (menos de 3: não encontrei)


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.

    Exemplo: "Tenho 62 anos, pago ÔNIBUS?" -> "tenho 62 anos pago onibus"
    """
    texto = texto.lower()
    for letra_acentuada, letra_simples in ACENTOS.items():
        texto = texto.replace(letra_acentuada, letra_simples)
    limpo = ""
    for caractere in texto:
        if caractere.isalnum() or caractere == " ":
            limpo += caractere
        else:
            limpo += " "          # pontuação vira espaço
    return " ".join(limpo.split())  # tira espaços repetidos


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []     # lista de objetos Orientacao
        self.erro = None          # mensagem caso o JSON não carregue

    def carregar(self):
        """Lê o JSON e cria os objetos. Nunca trava: devolve True ou False."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo {self.caminho} não encontrado."
            return False
        except json.JSONDecodeError as e:
            self.erro = f"Arquivo {self.caminho} está corrompido (linha {e.lineno})."
            return False
        except OSError as e:
            self.erro = f"Não foi possível ler {self.caminho}: {e}"
            return False

        if not isinstance(dados, list):
            self.erro = "O JSON deveria ser uma lista de orientações."
            return False

        for item in dados:
            # Só aceita dicionários com todos os campos obrigatórios.
            if not isinstance(item, dict) or not all(c in item for c in CAMPOS_OBRIGATORIOS):
                print(f"Aviso: orientação ignorada por falta de campos: {item.get('id', '?') if isinstance(item, dict) else item}")
                continue
            dados_orientacao = {campo: item[campo] for campo in CAMPOS_OBRIGATORIOS}
            self.orientacoes.append(Orientacao(**dados_orientacao))

        if not self.orientacoes:
            self.erro = "Nenhuma orientação válida no arquivo."
            return False
        self.erro = None
        return True

    def categorias(self):
        """Lista de categorias sem repetição, na ordem em que aparecem no JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def detalhar(self, pergunta, orientacao):
        """Calcula os pontos e diz POR QUE: (pontos, chaves_achadas, palavras_titulo)."""
        pergunta_norm = normalizar(pergunta)
        pergunta_com_espacos = f" {pergunta_norm} "
        pontos = 0

        chaves_achadas = []
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            # Espaços dos dois lados: "idoso" não casa dentro de "idosos" por acidente
            # e palavras-chave com várias palavras ("bilhete unico") também funcionam.
            if chave_norm and f" {chave_norm} " in pergunta_com_espacos:
                pontos += PESO_PALAVRA_CHAVE
                chaves_achadas.append(chave_norm)

        palavras_titulo = normalizar(orientacao.titulo).split()
        palavras_achadas = []
        for palavra in set(pergunta_norm.split()):   # set: cada palavra conta uma vez
            if (len(palavra) >= TAMANHO_MINIMO_TITULO and palavra not in PALAVRAS_IGNORADAS
                    and palavra in palavras_titulo):
                pontos += PESO_TITULO
                palavras_achadas.append(palavra)

        return pontos, chaves_achadas, sorted(palavras_achadas)

    def pontuar(self, pergunta, orientacao):
        """Devolve só o número de pontos da orientação para a pergunta."""
        return self.detalhar(pergunta, orientacao)[0]

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao) com pontos > 0, da maior para a menor."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
