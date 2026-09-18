"""
LAB 06b: as três verificações que não dependem uma da outra.

Antes de responder qualquer chamado, a Aurora checa três coisas:
  bloqueio financeiro, incidente na região, histórico de chamados.

Nenhuma depende do resultado da outra, então rodam juntas.
Depois um agregador lê as três chaves do state e conclui.

Regra de ouro do ParallelAgent: cada ramo escreve em um output_key
diferente. Dois ramos na mesma chave se sobrescrevem em ordem imprevisível.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from .comum import MODELO, consultar_status_rede, listar_eventos_massivos, toolset

checagem_financeira = LlmAgent(
    name="checagem_financeira",
    model=MODELO,
    description="Verifica bloqueio financeiro do cliente.",
    instruction="""
Chame buscar_cliente_por_cpf e listar_faturas_em_aberto para o CPF informado
pelo usuário, em dígitos.

Responda APENAS com JSON:
{"bloqueio_financeiro": true|false, "faturas_vencidas": 0, "detalhe": "..."}
""",
    tools=[toolset("cobranca")],
    output_key="check_financeiro",
)

checagem_rede = LlmAgent(
    name="checagem_rede",
    model=MODELO,
    description="Verifica incidente de rede na região do cliente.",
    instruction="""
Chame buscar_cliente_por_cpf para obter o CEP e depois consultar_status_rede,
e também listar_eventos_massivos.

Responda APENAS com JSON:
{"incidente_regiao": true|false, "severidade": "...", "previsao": "..."}
""",
    tools=[toolset("atendimento_n1"), consultar_status_rede, listar_eventos_massivos],
    output_key="check_rede",
)

checagem_historico = LlmAgent(
    name="checagem_historico",
    model=MODELO,
    description="Verifica reincidência nos últimos 90 dias.",
    instruction="""
Chame listar_chamados_recentes para o CPF informado.

Responda APENAS com JSON:
{"reincidente": true|false, "chamados_90d": 0, "ultimo": "..."}
""",
    tools=[toolset("tecnico")],
    output_key="check_historico",
)

verificacoes = ParallelAgent(
    name="verificacoes_simultaneas",
    description="Roda as três verificações de abertura ao mesmo tempo.",
    sub_agents=[checagem_financeira, checagem_rede, checagem_historico],
)

consolidador = LlmAgent(
    name="consolidador",
    model=MODELO,
    description="Junta as três verificações e define a conduta.",
    instruction="""
Você consolida a abertura do atendimento da Aurora Fibra.

Financeiro: {check_financeiro}
Rede: {check_rede}
Histórico: {check_historico}

Regras de conduta, nesta precedência:
1. Bloqueio financeiro presente: trate cobrança primeiro, o resto não resolve.
2. Incidente na região: informe severidade e previsão, não abra chamado individual.
3. Reincidência sem incidente de rede: encaminhe para N2 com prioridade.
4. Nada disso: siga o roteiro padrão de diagnóstico.

Responda ao cliente em até 100 palavras, sem jargão,
e informe qual das quatro condutas foi aplicada.
""",
    output_key="conduta",
)

pipeline_paralelo = SequentialAgent(
    name="abertura_com_verificacoes",
    description="Três verificações simultâneas e uma conduta consolidada.",
    sub_agents=[verificacoes, consolidador],
)
