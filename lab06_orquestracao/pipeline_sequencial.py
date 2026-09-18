"""
LAB 06a: o POP da Aurora, em ordem fixa.

Triagem, depois diagnóstico, depois registro. Sempre.
Nenhum LLM decide essa ordem, ela está no código.

A cola entre as etapas é o state: cada agente grava em `output_key`,
e o próximo lê essa chave na instruction com a sintaxe {chave}.
"""

from google.adk.agents import LlmAgent, SequentialAgent

from .comum import MODELO, consultar_status_rede, toolset

triagem = LlmAgent(
    name="etapa_triagem",
    model=MODELO,
    description="Classifica o chamado e identifica o cliente.",
    instruction="""
Você é a triagem da Aurora Fibra.

Com base no relato do cliente:
1. Chame buscar_cliente_por_cpf com o CPF informado, em dígitos.
2. Classifique em uma categoria: lentidao, sem_conexao, cobranca ou instalacao.

Responda APENAS com um JSON, sem texto ao redor, sem crase, no formato:
{"cpf": "...", "nome": "...", "cep": "...", "categoria": "...", "relato": "..."}
""",
    tools=[toolset("atendimento_n1")],
    output_key="triagem",
)

diagnostico = LlmAgent(
    name="etapa_diagnostico",
    model=MODELO,
    description="Investiga a causa provável usando rede e histórico.",
    instruction="""
Você é o diagnóstico técnico da Aurora Fibra.

Resultado da triagem:
{triagem}

1. Chame consultar_status_rede com o CEP da triagem.
2. Chame listar_chamados_recentes com o CPF da triagem.
3. Conclua a causa provável em no máximo três frases, dizendo explicitamente
   se o problema é de rede, individual ou financeiro.

Responda APENAS com um JSON, sem texto ao redor, no formato:
{"causa": "...", "escopo": "rede|individual|financeiro", "evidencias": ["...", "..."]}
""",
    tools=[toolset("atendimento_n1"), consultar_status_rede],
    output_key="diagnostico",
)

registro = LlmAgent(
    name="etapa_registro",
    model=MODELO,
    description="Redige a resposta ao cliente e o registro interno do atendimento.",
    instruction="""
Você é o registro do atendimento da Aurora Fibra.

Triagem: {triagem}
Diagnóstico: {diagnostico}

Produza duas partes, nesta ordem e com estes títulos exatos:

RESPOSTA AO CLIENTE
Até 100 palavras, em português claro, sem jargão de rede,
dizendo o que foi identificado e qual é o próximo passo.

REGISTRO INTERNO
Três linhas: categoria, causa provável e ação tomada.
""",
    output_key="registro",
)

pipeline_sequencial = SequentialAgent(
    name="pop_atendimento",
    description="Procedimento operacional padrão da Aurora: triagem, diagnóstico, registro.",
    sub_agents=[triagem, diagnostico, registro],
)
