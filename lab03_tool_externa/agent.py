"""
LAB 03: o primeiro acesso ao sistema.

Duas tools, e a distinção que importa entre elas:
  consultar_status_rede  lê o mundo
  reiniciar_roteador     muda o mundo

Toda tool que muda o mundo precisa de um ponto de política antes da execução.
No ADK esse ponto é o before_tool_callback.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool, ToolContext

from .tools import consultar_status_rede, reiniciar_roteador

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")

ACOES_DESTRUTIVAS = {"reiniciar_roteador"}


def guardrail_acao_destrutiva(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> Optional[dict]:
    """Barra ação destrutiva sem confirmação registrada na sessão.

    Retornar um dict aqui cancela a execução da tool e devolve esse dict
    ao modelo como se fosse o resultado. Retornar None deixa passar.
    """
    if tool.name not in ACOES_DESTRUTIVAS:
        return None

    if tool_context.state.get("autorizacao_reinicio") is True:
        return None

    return {
        "status": "bloqueado",
        "mensagem": (
            "Reinício não autorizado. Explique ao cliente que a conexão cairá por "
            "cerca de 3 minutos, pergunte se ele autoriza, e só então chame "
            "registrar_autorizacao_reinicio."
        ),
    }


def registrar_autorizacao_reinicio(autorizado: bool, tool_context: ToolContext) -> dict:
    """Registra que o cliente autorizou o reinício do roteador.

    Só chame depois de o cliente responder que sim, de forma explícita.

    Args:
        autorizado: True apenas se o cliente disse que autoriza.

    Returns:
        dict com status do registro.
    """
    tool_context.state["autorizacao_reinicio"] = bool(autorizado)
    return {"status": "ok", "autorizacao_reinicio": bool(autorizado)}


INSTRUCTION = """
Você é o ARI, assistente de suporte N1 da Aurora Fibra.
Fale em português do Brasil, tom cordial e direto, respostas de até 120 palavras.

PROTOCOLO TÉCNICO
1. Diante de lentidão, oscilação ou queda, peça o CEP e chame consultar_status_rede.
2. Se houver incidente na região, informe a severidade e a previsão de normalização,
   e NÃO proponha reinício de roteador, o problema não está na casa do cliente.
3. Se a rede estiver normal, aí sim proponha o reinício remoto.
   Avise que a conexão cai por cerca de 3 minutos, pergunte se ele autoriza,
   e ao receber o sim chame registrar_autorizacao_reinicio e depois reiniciar_roteador.
4. Se uma tool retornar status indisponivel ou erro, diga isso ao cliente com
   honestidade e ofereça abrir um chamado. Nunca preencha a lacuna com suposição.

LIMITES
Você não tem acesso a faturas, contratos ou histórico de chamados.
Nunca invente esses dados.
"""


root_agent = LlmAgent(
    name="ari_com_acesso",
    model=MODELO,
    description="Atendente N1 da Aurora com acesso ao painel de rede.",
    instruction=INSTRUCTION,
    tools=[consultar_status_rede, registrar_autorizacao_reinicio, reiniciar_roteador],
    before_tool_callback=guardrail_acao_destrutiva,
)
