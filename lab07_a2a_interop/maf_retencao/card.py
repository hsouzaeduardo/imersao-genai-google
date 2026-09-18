"""
O agent card do time de Retenção.

Este arquivo é a fronteira entre os dois mundos. O servidor MAF publica
este card; o RemoteA2aAgent do ADK lê exatamente este card para saber o
que o agente remoto faz e por onde falar com ele.

Repare que não há uma linha de ADK nem de MAF aqui: são tipos do a2a-sdk,
que os dois frameworks compartilham. É esse o ponto do protocolo.

Atenção à versão: o a2a-sdk 1.x gera estes tipos a partir de protobuf,
então os campos são snake_case e listas não aceitam None. Exemplos em
blogs escritos para a linha 0.3 usam nomes camelCase e não funcionam aqui.
"""

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils import TransportProtocol

SKILL_RETENCAO = AgentSkill(
    id="oferta_retencao",
    name="Oferta de retenção",
    description=(
        "Avalia um pedido de cancelamento e devolve a contraproposta que a "
        "política comercial da Aurora autoriza para aquele perfil de cliente."
    ),
    tags=["retencao", "cancelamento", "desconto", "churn"],
    examples=[
        "Cliente quer cancelar, está há 7 anos na base e tem 3 faturas vencidas.",
        "Cliente reclama de preço e citou proposta de concorrente.",
    ],
)


def construir_card(url: str) -> AgentCard:
    """Monta o card anunciado pelo servidor A2A.

    Args:
        url: endereço público onde o JSON-RPC deste agente atende.

    Returns:
        O AgentCard que o ADK vai ler no caminho /.well-known/agent-card.json.
    """
    return AgentCard(
        name="Agente de Retencao Aurora",
        description=(
            "Especialista em retenção da Aurora Fibra. Recebe o contexto de um "
            "cliente que pediu cancelamento e responde com a oferta autorizada, "
            "o motivo da recusa quando não há oferta, e o próximo passo. "
            "Mantido pelo time de CX, fora da stack do atendimento N1."
        ),
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(url=url, protocol_binding=TransportProtocol.JSONRPC),
        ],
        skills=[SKILL_RETENCAO],
    )


# A política que o agente aplica. Fica aqui para o servidor real e o stub
# responderem pela mesma regra, e para o aluno ver que a regra é do outro
# time: o ARI não conhece nada disso.
POLITICA_RETENCAO = """
POLÍTICA DE RETENÇÃO DA AURORA FIBRA, USO INTERNO

Faixas de oferta, por tempo de casa:
  até 1 ano      sem desconto, oferecer apenas upgrade de velocidade sem custo
  1 a 3 anos     até 15% por 6 meses
  acima de 3 anos até 30% por 12 meses, ou upgrade de plano mantendo o preço

Bloqueios, que vencem qualquer faixa acima:
  contrato suspenso ou com fatura vencida: nenhuma oferta antes da regularização
  cliente já retido nos últimos 12 meses: no máximo metade da faixa
  pedido por mudança de endereço sem cobertura: não há oferta, só o distrato

Nunca prometa prazo de instalação, valor de multa ou data de visita:
isso é do sistema de contratos, não seu.
"""
