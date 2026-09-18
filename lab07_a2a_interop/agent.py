"""
LAB 07: o agente que não é seu.

No lab 05 o ARI virou coordenador e ganhou três especialistas. Todos em
ADK, no mesmo processo, no mesmo deploy, no mesmo time. Delegar ali custa
um import.

Agora o cliente pede cancelamento. Quem decide desconto na Aurora é o time
de CX, e o agente deles roda em Microsoft Agent Framework sobre Azure. Você
não vai reescrever o agente deles em ADK, e eles não vão migrar para o seu.
Nenhum dos dois lados vai entregar a política comercial para o outro.

A dor do lab é essa: sub_agents só atravessa o seu próprio framework.

O remédio é o A2A. Do lado ADK ele cabe em um objeto, o RemoteA2aAgent, que
por fora é um sub-agente como qualquer outro: entra em sub_agents, é
escolhido pela description, recebe o turno. Por dentro, ele lê um agent card
por HTTP e conversa JSON-RPC com um processo que não é seu.

Rodar:
    1. sobe o agente do outro time, numa janela separada
       python lab07_a2a_interop/maf_retencao/servidor_stub.py
    2. adk run lab07_a2a_interop

Experimento do lab: derrube o servidor do passo 1 no meio da conversa e
peça de novo o cancelamento. Compare com o lab 05, onde o especialista
nunca some porque mora no seu processo. Um sub-agente remoto é rede, e rede
cai. Repare também que trocar o servidor_stub pelo servidor real muda o
motor do outro lado sem mudar uma linha deste arquivo.
"""

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent

from .comum import MAF_A2A_URL, MODELO

# ------------------------------------------------------------------
# O agente do outro time, visto daqui
# ------------------------------------------------------------------
# Não há import do MAF nesta linha, nem poderia haver. O que o ADK recebe
# é uma URL de card. Tudo que ele sabe do agente remoto, ele leu do card.
agente_retencao = RemoteA2aAgent(
    name="agente_retencao",
    description=(
        "Time de retenção da Aurora. Acione quando o cliente disser que quer "
        "cancelar, ameaçar cancelar, citar proposta de concorrente ou reclamar "
        "que o preço está alto demais para continuar. Ele decide qual desconto "
        "ou contraproposta a política comercial autoriza."
    ),
    agent_card=f"{MAF_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)


INSTRUCTION = """
Você é o ARI, atendimento N1 da Aurora Fibra.

Você resolve o que é N1. Cancelamento não é N1.

QUANDO O ASSUNTO FOR CANCELAMENTO
Antes de transferir para o time de retenção, junte o contexto, porque eles
não têm acesso ao seu histórico e vão responder com o que você mandar:

1. Há quanto tempo o cliente é da Aurora.
2. Se há fatura vencida ou contrato suspenso.
3. O motivo do cancelamento, nas palavras do cliente.

Faça no máximo duas perguntas por vez para levantar isso. Com os três dados
em mãos, transfira para o agente_retencao passando o contexto reunido.

LIMITES
Você não conhece a política de desconto da Aurora e não deve inventá-la.
Nunca prometa desconto, isenção de multa ou valor de qualquer espécie.
Quem diz o que é possível é o time de retenção, não você.
Se o time de retenção estiver fora do ar, diga isso ao cliente com todas as
letras e ofereça registrar o pedido para retorno. Não improvise a oferta.

ESTILO
Português do Brasil, cordial e direto. Até 100 palavras. Sem emojis.
"""

root_agent = LlmAgent(
    name="ari_com_a2a",
    model=MODELO,
    description="Atendimento N1 da Aurora, com acesso ao time de retenção via A2A.",
    instruction=INSTRUCTION,
    sub_agents=[agente_retencao],
)
