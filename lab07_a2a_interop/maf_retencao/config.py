"""
Configuração do lado MAF, deliberadamente separada do lado ADK.

Poderia importar de lab07_a2a_interop.comum e economizar seis linhas. Não
importa de propósito: puxar aquele pacote executaria o agent.py do ADK, e
o agente do outro time não tem, nem deveria ter, o seu código instalado.

Essa duplicação é o lab falando: o único contrato entre os dois lados é o
agent card publicado por HTTP.
"""

import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Endereço que este servidor anuncia no próprio card.
MAF_A2A_URL = os.getenv("MAF_A2A_URL", "http://localhost:9999")

# Azure, usado só pelo servidor.py. O stub não lê nada disto.
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "")
FOUNDRY_MODEL = os.getenv("FOUNDRY_MODEL", "gpt-4o-mini")
