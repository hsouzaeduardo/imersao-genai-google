"""
O agente de Retenção da Aurora, em Microsoft Agent Framework.

Este arquivo é o "outro time". Ele não importa nada do ADK, não sabe que o
ARI existe e não sabe que quem vai chamá-lo é um agente Google. Ele publica
um agent card e atende JSON-RPC. Só isso.

Rodar:
    python lab07_a2a_interop/maf_retencao/servidor.py

Precisa de Azure. Em MAF 1.x o caminho para Azure OpenAI é o Microsoft
Foundry, via FoundryChatClient, não uma classe AzureOpenAIChatClient, que
não existe no pacote. Configure no .env:

    FOUNDRY_PROJECT_ENDPOINT=https://<seu-projeto>.services.ai.azure.com/api/projects/<nome>
    FOUNDRY_MODEL=gpt-4o-mini

E autentique com `az login`, porque o cliente usa DefaultAzureCredential.

Sem Azure à mão, use o servidor_stub.py ao lado: mesmo card, mesma porta,
mesmo protocolo, resposta canned. O lado ADK não distingue um do outro,
que é justamente o que o protocolo promete.
"""

import os
import sys

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from agent_framework import Agent
from agent_framework.a2a import A2AExecutor
from azure.identity import DefaultAzureCredential
from starlette.applications import Starlette

# Só o diretório deste servidor entra no path, nunca a raiz do repo: o
# agente do outro time não carrega o pacote do lab, que traria o ADK junto.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from card import POLITICA_RETENCAO, construir_card  # noqa: E402
from config import FOUNDRY_MODEL, FOUNDRY_PROJECT_ENDPOINT, MAF_A2A_URL  # noqa: E402

INSTRUCAO = f"""
Você é o agente de retenção da Aurora Fibra, provedor de internet.

Você recebe o contexto de um cliente que pediu cancelamento, vindo do
atendimento N1. O N1 não conhece a política abaixo, e não deve conhecer.
Quem decide oferta é você.

{POLITICA_RETENCAO}

Responda sempre com estas três partes, nesta ordem:

OFERTA
A contraproposta autorizada, ou "sem oferta" com o motivo em uma frase.

JUSTIFICATIVA
Qual regra da política se aplicou. Cite a faixa ou o bloqueio pelo nome.

PRÓXIMO PASSO
O que o atendimento deve fazer agora, em uma frase.

Até 120 palavras no total. Sem emojis. Se o contexto não trouxer tempo de
casa ou situação financeira, peça exatamente o dado que falta e não invente
uma oferta.
"""


def construir_agente() -> Agent:
    """Monta o agente MAF ligado ao Foundry."""
    if not FOUNDRY_PROJECT_ENDPOINT:
        raise SystemExit(
            "FOUNDRY_PROJECT_ENDPOINT não está no .env.\n"
            "Sem Azure, rode o servidor_stub.py, que fala o mesmo protocolo."
        )

    from agent_framework.foundry import FoundryChatClient

    cliente = FoundryChatClient(
        project_endpoint=FOUNDRY_PROJECT_ENDPOINT,
        model=FOUNDRY_MODEL,
        credential=DefaultAzureCredential(),
    )
    return Agent(
        client=cliente,
        name="Agente de Retencao Aurora",
        description="Decide ofertas de retenção segundo a política comercial da Aurora.",
        instructions=INSTRUCAO,
    )


def construir_app() -> Starlette:
    """Monta o servidor A2A em volta do agente MAF.

    O A2AExecutor é a peça do MAF que adapta um agente qualquer ao lado
    servidor do protocolo. Todo o resto, task store, rotas e card, vem do
    a2a-sdk, que é comum aos dois frameworks.
    """
    card = construir_card(MAF_A2A_URL)

    handler = DefaultRequestHandler(
        agent_executor=A2AExecutor(construir_agente(), stream=True),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )

    return Starlette(
        routes=[
            *create_agent_card_routes(card),
            *create_jsonrpc_routes(handler, "/"),
        ]
    )


if __name__ == "__main__":
    porta = int(os.getenv("MAF_A2A_PORT", "9999"))
    print(f"Agente de Retenção (MAF) em http://localhost:{porta}")
    print(f"Card em http://localhost:{porta}/.well-known/agent-card.json")
    uvicorn.run(construir_app(), host="0.0.0.0", port=porta)
