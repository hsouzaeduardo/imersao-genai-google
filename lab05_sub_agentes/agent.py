"""
LAB 05: ARI promovido a coordenador.

Ele para de atender e passa a distribuir. Três especialistas,
cada um com a sua fatia de tools e a sua regra de negócio.

O que o aluno precisa internalizar aqui:
  sub_agents  -> transfere o controle, o especialista responde ao cliente
  AgentTool   -> chama e devolve, o coordenador continua no comando

E o campo que decide o roteamento não é a instruction do especialista,
é a description dele.
"""

from google.adk.agents import LlmAgent

from .comum import MODELO
from .especialistas import agente_agendamento, agente_cobranca, agente_tecnico

INSTRUCTION = """
Você é o ARI, coordenador do atendimento da Aurora Fibra.

SEU TRABALHO É ROTEAR, NÃO RESOLVER.
Você não consulta fatura, não consulta rede, não abre chamado.

1. Cumprimente e peça o CPF, se ainda não tiver.
2. Identifique o assunto e transfira para o especialista correto.
3. Se o cliente trouxer dois assuntos no mesmo pedido, trate um de cada vez:
   resolva a pendência financeira primeiro, porque suporte técnico em contrato
   suspenso não resolve nada, e só depois transfira para o técnico.
4. Se não der para classificar, faça UMA pergunta de esclarecimento.

Nunca peça desculpa pela transferência nem narre o procedimento interno.
Responda em até 60 palavras.
"""

root_agent = LlmAgent(
    name="ari_coordenador",
    model=MODELO,
    description="Coordenador do atendimento da Aurora Fibra, roteia para os especialistas.",
    instruction=INSTRUCTION,
    sub_agents=[agente_cobranca, agente_tecnico, agente_agendamento],
)
