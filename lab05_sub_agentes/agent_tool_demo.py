"""
O contraste do lab 05: os mesmos especialistas, como AgentTool.

Rode este arquivo e o agent.py com a MESMA frase, e compare os traces.

  sub_agents: o controle passa para o especialista, que fala direto com o cliente.
              O coordenador sai de cena até o próximo turno.

  AgentTool:  o especialista é chamado como ferramenta, devolve o resultado,
              e o coordenador redige a resposta final juntando tudo.

Regra prática: use sub_agents quando o especialista deve conduzir a conversa.
Use AgentTool quando você precisa consultar vários especialistas
e responder uma coisa só.

    adk run lab05_sub_agentes  (com root_agent trocado abaixo)
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .comum import MODELO
from .especialistas import agente_agendamento, agente_cobranca, agente_tecnico

root_agent_como_tool = LlmAgent(
    name="ari_maestro",
    model=MODELO,
    description="Coordenador que consulta especialistas e redige uma resposta única.",
    instruction="""
Você é o ARI, coordenador do atendimento da Aurora Fibra.

Você tem três consultores internos disponíveis como ferramentas.
Consulte quantos forem necessários ANTES de responder, e entregue ao cliente
uma resposta única, integrada, em até 120 palavras.

Se o cliente trouxer problema financeiro e técnico juntos, consulte os dois
e explique a relação entre eles, por exemplo contrato suspenso derrubando o serviço.

Nunca mencione que consultou ferramentas ou outros agentes.
""",
    tools=[
        AgentTool(agent=agente_cobranca),
        AgentTool(agent=agente_tecnico),
        AgentTool(agent=agente_agendamento),
    ],
)
