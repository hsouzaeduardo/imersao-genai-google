"""
O mesmo agente de Retenção, sem LLM nenhum.

Serve para duas coisas:

  1. Ver o A2A funcionando antes de ter credencial de Azure. O card é o
     mesmo, a porta é a mesma, o protocolo é o mesmo. O lado ADK não
     percebe diferença, e essa é exatamente a promessa do protocolo.

  2. Testar a integração de verdade. Com LLM dos dois lados, um teste que
     falha não diz se o problema foi o protocolo ou o modelo. Aqui a
     resposta é determinística, então falha é falha de integração.

Rodar:
    python lab07_a2a_interop/maf_retencao/servidor_stub.py

Note que este arquivo não importa nem ADK nem MAF: é a2a-sdk puro. Um
servidor A2A é um servidor A2A, venha de onde vier. Por isso ele também
não importa o pacote do lab: puxar lab07_a2a_interop traria o agente ADK
junto, e o "outro time" não tem o seu código.
"""

import os
import re
import sys
import uuid

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import Message, Part, Role
from starlette.applications import Starlette

# Só o diretório deste servidor entra no path, nunca a raiz do repo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from card import construir_card  # noqa: E402
from config import MAF_A2A_URL  # noqa: E402

# Termos que indicam pendência financeira, e as negações que os anulam.
# "sem fatura vencida" contém "vencida": procurar o termo solto marcaria
# o cliente adimplente como devedor, então a negação é testada primeiro.
TERMOS_DEBITO = (
    r"(?:faturas?|pend[êe]ncias?|d[ée]bitos?|atrasad\w+|atraso|vencid\w+|suspens\w+)"
)
NEGACOES = r"(?:sem|nenhum\w*|zero|n[ãa]o\s+(?:h[áa]|tem|possui|est[áa]))"


def decidir_oferta(contexto: str) -> str:
    """Aplica a política de retenção sem modelo nenhum, só com regras.

    É de propósito grosseira: a graça do lab está no protocolo, não aqui.

    Args:
        contexto: o texto que o agente remoto recebeu do ARI.

    Returns:
        A resposta no mesmo formato de três partes que o agente real usa.
    """
    texto = contexto.lower()

    anos = 0
    achado = re.search(r"(\d+)\s*anos?", texto)
    if achado:
        anos = int(achado.group(1))

    negado = re.search(rf"\b{NEGACOES}\s+(?:\w+\s+)?{TERMOS_DEBITO}\b", texto)
    citado = re.search(rf"\b{TERMOS_DEBITO}\b", texto)
    inadimplente = bool(citado) and not negado

    if inadimplente:
        oferta = "sem oferta, regularização pendente"
        regra = "Bloqueio: contrato suspenso ou fatura vencida vence qualquer faixa."
        passo = "Transfira para cobrança e retome a retenção após a regularização."
    elif anos > 3:
        oferta = "30% de desconto por 12 meses, ou upgrade de plano pelo mesmo preço"
        regra = "Faixa acima de 3 anos de casa."
        passo = "Confirme a escolha com o cliente e registre o aceite."
    elif anos >= 1:
        oferta = "15% de desconto por 6 meses"
        regra = "Faixa de 1 a 3 anos de casa."
        passo = "Ofereça e, se recusar, encerre sem insistir."
    else:
        oferta = "sem oferta, falta informação"
        regra = "Contexto não informou tempo de casa."
        passo = "Peça ao N1 há quanto tempo o cliente está na base."

    return f"OFERTA\n{oferta}\n\nJUSTIFICATIVA\n{regra}\n\nPRÓXIMO PASSO\n{passo}"


class ExecutorRetencaoStub(AgentExecutor):
    """Lado servidor do A2A, implementado direto no a2a-sdk.

    É o mesmo papel que o A2AExecutor do MAF cumpre no servidor.py:
    receber a mensagem, produzir a resposta, devolver na fila de eventos.
    """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        pergunta = context.get_user_input()
        resposta = decidir_oferta(pergunta)

        await event_queue.enqueue_event(
            Message(
                message_id=str(uuid.uuid4()),
                context_id=context.context_id or "",
                task_id=context.task_id or "",
                role=Role.ROLE_AGENT,
                parts=[Part(text=resposta)],
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Nada a cancelar: a resposta é síncrona e imediata."""
        return None


def construir_app() -> Starlette:
    """Monta o mesmo servidor A2A do servidor.py, com o executor stub."""
    card = construir_card(MAF_A2A_URL)

    handler = DefaultRequestHandler(
        agent_executor=ExecutorRetencaoStub(),
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
    print(f"Agente de Retenção STUB, sem LLM, em http://localhost:{porta}")
    print(f"Card em http://localhost:{porta}/.well-known/agent-card.json")
    uvicorn.run(construir_app(), host="0.0.0.0", port=porta)
