"""
Configuração compartilhada entre o lado ADK e o lado MAF do lab 07.

O único acoplamento legítimo entre os dois frameworks é o endereço do
servidor A2A. Nada de import cruzado: o ADK não conhece o MAF, o MAF não
conhece o ADK. Cada um fala protocolo.
"""

import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")

# Onde o agente de Retenção, que é do outro time, está publicado.
MAF_A2A_URL = os.getenv("MAF_A2A_URL", "http://localhost:9999")

# Credenciais do lado MAF. Só o servidor usa, o ADK nunca vê isso.
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "")
FOUNDRY_MODEL = os.getenv("FOUNDRY_MODEL", "gpt-4o-mini")
