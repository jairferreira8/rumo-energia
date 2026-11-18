"""Classe Orientacao: representa UMA orientação da base de conhecimento.

Cada dicionário do JSON vira um objeto Orientacao. Os atributos têm os
mesmos nomes dos campos obrigatórios do JSON.
"""

CAMPOS_OBRIGATORIOS = [
    "id", "categoria", "titulo", "palavras_chave", "resposta",
    "documentos", "onde", "fonte", "verificado_em",
]

AVISO = "Atenção: este assistente não é canal oficial. Confirme sempre no órgão responsável."


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave      # lista de textos
        self.resposta = resposta
        self.documentos = documentos              # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em        # "AAAA-MM-DD"

    def data_verificacao(self):
        """Converte 2026-11-16 em 16/11/2026 para mostrar ao cidadão."""
        partes = self.verificado_em.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return self.verificado_em

    def exibir(self, confianca=None):
        """Mostra a orientação completa na tela, sempre com fonte, data e aviso."""
        print()
        print("=" * 60)
        print(f"[{self.categoria}] {self.titulo}")
        if confianca:
            print(f"Confiança da resposta: {confianca}")
        print("-" * 60)
        print(self.resposta)
        print()
        print("Documentos:")
        for doc in self.documentos:
            print(f"  - {doc}")
        print(f"Onde ir: {self.onde}")
        print()
        print(f"Fonte: {self.fonte}")
        print(f"Informação verificada em: {self.data_verificacao()}")
        print(AVISO)
        print("=" * 60)
