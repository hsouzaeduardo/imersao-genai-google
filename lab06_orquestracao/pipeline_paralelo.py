"""
LAB 06b: as três verificações que não dependem uma da outra.

Antes de responder qualquer chamado, a Aurora checa três coisas:
  bloqueio financeiro, incidente na região, histórico de chamados.

Nenhuma depende do resultado da outra, então rodam juntas.
Depois um agregador lê as três chaves do state e conclui.

Regra de ouro do ParallelAgent: cada ramo escreve em um output_key
diferente. Dois ramos na mesma chave se sobrescrevem em ordem imprevisível.

Segunda regra, do ADK: um agente só tem um pai. Como o run_demo monta as
mesmas três checagens em sequência e em paralelo, cada arranjo pede
instâncias próprias. É para isso que servem as funções `criar_*`.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from .comum import MODELO, consultar_status_rede, listar_eventos_massivos, toolset


def criar_checagem_financeira() -> LlmAgent:
    """Cria uma instância nova da checagem financeira."""
    return LlmAgent(
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


def criar_checagem_rede() -> LlmAgent:
    """Cria uma instância nova da checagem de rede."""
    return LlmAgent(
        name="checagem_rede",
        model=MODELO,
        description="Verifica incidente de rede na região do cliente.",
        instruction="""
Você verifica se existe incidente de rede no endereço DESTE cliente.

1. Chame buscar_cliente_por_cpf e guarde o CEP do cadastro.
2. Chame consultar_status_rede com esse CEP.
3. Chame listar_eventos_massivos.

COMO DECIDIR, e esta parte é obrigatória:
`incidente_regiao` sai EXCLUSIVAMENTE do consultar_status_rede do CEP deste
cliente. É true apenas se aquela consulta voltar com situacao igual a
"incidente". Se voltar "normal", é false, ponto final.

O listar_eventos_massivos mostra incidentes de toda a base, quase sempre em
CEPs de outros clientes. Ele NUNCA torna `incidente_regiao` verdadeiro.
Serve só para preencher `eventos_ativos_na_base`, que é contexto do plantão,
não diagnóstico deste atendimento.

`severidade` e `previsao` também vêm do consultar_status_rede deste CEP.
Se a situação for "normal", devolva string vazia nos dois.

Responda APENAS com JSON:
{"incidente_regiao": true|false, "severidade": "...", "previsao": "...",
 "cep_consultado": "...", "eventos_ativos_na_base": 0}
""",
        tools=[toolset("atendimento_n1"), consultar_status_rede, listar_eventos_massivos],
        output_key="check_rede",
    )


def criar_checagem_historico() -> LlmAgent:
    """Cria uma instância nova da checagem de histórico."""
    return LlmAgent(
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


def criar_consolidador() -> LlmAgent:
    """Cria uma instância nova do consolidador."""
    return LlmAgent(
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


def criar_verificacoes() -> ParallelAgent:
    """Monta o bloco paralelo com checagens novas, livres de pai."""
    return ParallelAgent(
        name="verificacoes_simultaneas",
        description="Roda as três verificações de abertura ao mesmo tempo.",
        sub_agents=[
            criar_checagem_financeira(),
            criar_checagem_rede(),
            criar_checagem_historico(),
        ],
    )


def criar_pipeline_paralelo() -> SequentialAgent:
    """Monta verificações paralelas mais consolidação, tudo novo."""
    return SequentialAgent(
        name="abertura_com_verificacoes",
        description="Três verificações simultâneas e uma conduta consolidada.",
        sub_agents=[criar_verificacoes(), criar_consolidador()],
    )


# Instâncias canônicas do lab: é este pipeline que `adk run` carrega.
checagem_financeira = criar_checagem_financeira()
checagem_rede = criar_checagem_rede()
checagem_historico = criar_checagem_historico()

verificacoes = ParallelAgent(
    name="verificacoes_simultaneas",
    description="Roda as três verificações de abertura ao mesmo tempo.",
    sub_agents=[checagem_financeira, checagem_rede, checagem_historico],
)

consolidador = criar_consolidador()

pipeline_paralelo = SequentialAgent(
    name="abertura_com_verificacoes",
    description="Três verificações simultâneas e uma conduta consolidada.",
    sub_agents=[verificacoes, consolidador],
)
