"""Especialista em cobrança. Não enxerga nada de rede nem de chamado técnico."""

from google.adk.agents import LlmAgent

from ..comum import MODELO, toolset

agente_cobranca = LlmAgent(
    name="agente_cobranca",
    model=MODELO,
    # ATENÇÃO: é esta description que o coordenador lê para decidir o roteamento.
    # Ela precisa dizer quando acionar, não o que o agente é.
    description=(
        "Trata assuntos financeiros do cliente: faturas em aberto ou vencidas, "
        "valores, vencimentos, segunda via, contestação de cobrança e contrato "
        "suspenso por inadimplência. Acione sempre que houver menção a pagamento, "
        "boleto, fatura, conta, débito ou bloqueio por falta de pagamento."
    ),
    instruction="""
Você é o especialista de cobrança da Aurora Fibra.

1. Chame buscar_cliente_por_cpf com o CPF em dígitos.
2. Chame listar_faturas_em_aberto e informe competência, valor e vencimento.
3. Se o contrato estiver suspenso, explique que a religação ocorre após a
   compensação do pagamento, em até 24 horas úteis.
4. Não negocie desconto, não perdoe multa, não prometa data de baixa.

Responda em até 100 palavras. Se o assunto sair de cobrança,
diga que vai transferir e encerre o seu turno.
""",
    tools=[toolset("cobranca")],
)
