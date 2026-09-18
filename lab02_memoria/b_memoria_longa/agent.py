"""
LAB 02b: o prontuário do cliente.

State é o caderno do atendimento de hoje. Memória é o prontuário,
o que o ARI sabe sobre esse cliente independente da conversa atual.

Duas formas de recuperar memória:
  - load_memory       o modelo decide quando buscar, custa menos, às vezes ele não busca
  - PreloadMemoryTool busca no início de todo turno, sempre tem contexto, custa tokens

A escrita da memória não acontece sozinha. Alguém precisa chamar
add_session_to_memory, seja o seu código, seja um callback.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_memory

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")


INSTRUCTION = """
Você é o ARI, assistente de suporte N1 da Aurora Fibra.
Fale em português do Brasil, tom cordial e direto, respostas de até 120 palavras.

USO DE MEMÓRIA, PARTE OBRIGATÓRIA DO SEU PROTOCOLO
No primeiro turno de qualquer atendimento, chame a tool load_memory buscando
pelo assunto do contato, para recuperar o histórico deste cliente.
Chame load_memory de novo sempre que o cliente disser "como da última vez",
"igual eu pedi", "vocês já sabem" ou qualquer referência a contato anterior.

Se a memória trouxer preferências, use sem perguntar de novo.
Se a memória vier vazia, siga o atendimento normalmente e não invente histórico.

LIMITES
Você ainda não tem acesso a status de rede, faturas ou chamados.
Nunca invente esses dados.
"""


async def gravar_memoria_ao_fim(callback_context: CallbackContext):
    """Fecha o prontuário ao término do turno do agente.

    Em produção com Memory Bank, este callback dispara a geração de memórias
    a partir dos eventos da sessão. Com o InMemoryMemoryService do lab,
    a gravação é feita explicitamente no run_demo.py para ficar visível.
    """
    try:
        await callback_context.add_session_to_memory()
    except (AttributeError, NotImplementedError):
        # serviço de memória local não implementa geração automática
        pass
    return None


root_agent = LlmAgent(
    name="ari_com_prontuario",
    model=MODELO,
    description="Atendente N1 da Aurora que lembra do cliente entre atendimentos.",
    instruction=INSTRUCTION,
    tools=[load_memory],
    after_agent_callback=gravar_memoria_ao_fim,
)


# ------------------------------------------------------------------
# Variante Memory Bank, para quem estiver com projeto Vertex AI
# ------------------------------------------------------------------
# from google.adk.memory import VertexAiMemoryBankService
# from google.adk.tools.preload_memory_tool import PreloadMemoryTool
#
# memory_service = VertexAiMemoryBankService(
#     project=os.getenv("GOOGLE_CLOUD_PROJECT"),
#     location=os.getenv("GOOGLE_CLOUD_LOCATION"),
#     agent_engine_id=os.getenv("AGENT_ENGINE_ID"),
# )
#
# Troque tools=[load_memory] por tools=[PreloadMemoryTool()] e compare:
# com Preload, o contexto aparece em todo turno sem tool call visível no trace.
