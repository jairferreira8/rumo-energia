"""Rumo - o caminho para a sua casa e pela sua cidade.

Assistente de terminal da Global Solution 2026.2 (CitizenTech / Citizen Assist AI).
Execute a partir desta pasta:  python main.py
"""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

# Garante que os caminhos "data/..." funcionem mesmo se rodar de outra pasta.
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    base = BaseConhecimento("data/base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Rumo", base)
    assistente.iniciar()   # menu principal: perguntar(), navegar(), indicadores...


if __name__ == "__main__":
    main()
