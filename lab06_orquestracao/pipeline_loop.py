"""
LAB 06c: o revisor que não deixa a resposta sair torta.

Um LoopAgent com dois papéis: quem escreve e quem critica.
O loop só termina quando o crítico aprova, ou quando bate max_iterations.

A saída do loop é feita por uma tool que seta escalate na ação do turno.
Sem isso, e sem max_iterations, o loop vira fatura de API.

As funções `criar_*` existem porque o mesmo loop é montado em mais de um
pipeline neste lab, e no ADK cada agente pertence a um único pai.
"""

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import ToolContext

from .comum import MODELO

CRITERIOS = """
CRITÉRIOS DE QUALIDADE DA AURORA
1. Até 100 palavras.
2. Zero jargão técnico sem explicação: OLT, ONU, LOS, latência, pacote.
3. Diz claramente qual é o próximo passo e de quem é a responsabilidade.
4. Nenhuma promessa de prazo que não veio de uma tool.
5. Tom cordial, sem pedir desculpas mais de uma vez.
"""

INSTRUCTION_REDATOR = f"""
Você redige a resposta final ao cliente da Aurora Fibra.

Se existir uma crítica anterior no campo abaixo, reescreva corrigindo
exatamente o que foi apontado. Se não existir, escreva a primeira versão.

Crítica anterior: {{critica?}}

{CRITERIOS}

Responda apenas com o texto da resposta ao cliente.
"""

INSTRUCTION_CRITICO = f"""
Você é o revisor de qualidade da Aurora Fibra.

Resposta a avaliar:
{{resposta}}

{CRITERIOS}

Se a resposta cumprir todos os critérios, chame a tool aprovar_resposta
e não escreva mais nada.

Se falhar em algum critério, NÃO chame a tool. Escreva apenas a lista dos
problemas encontrados, um por linha, começando pelo número do critério.
Seja específico: aponte a palavra ou a frase que precisa mudar.
"""


def aprovar_resposta(tool_context: ToolContext) -> dict:
    """Aprova a resposta atual e encerra o ciclo de revisão.

    Chame somente quando a resposta cumprir todos os critérios de qualidade.

    Returns:
        dict confirmando a aprovação.
    """
    tool_context.actions.escalate = True
    return {"status": "aprovada"}


def criar_redator() -> LlmAgent:
    """Cria uma instância nova do redator."""
    return LlmAgent(
        name="redator",
        model=MODELO,
        description="Escreve ou reescreve a resposta ao cliente.",
        instruction=INSTRUCTION_REDATOR,
        output_key="resposta",
    )


def criar_critico() -> LlmAgent:
    """Cria uma instância nova do crítico."""
    return LlmAgent(
        name="critico",
        model=MODELO,
        description="Avalia a resposta contra os critérios de qualidade.",
        instruction=INSTRUCTION_CRITICO,
        tools=[aprovar_resposta],
        output_key="critica",
    )


def criar_pipeline_loop() -> LoopAgent:
    """Monta um ciclo de revisão novo, livre de pai."""
    return LoopAgent(
        name="revisao_de_qualidade",
        description="Refina a resposta ao cliente até passar nos critérios.",
        sub_agents=[criar_redator(), criar_critico()],
        max_iterations=3,
    )


# Instâncias canônicas do lab: é este pipeline que `adk run` carrega.
redator = criar_redator()
critico = criar_critico()

pipeline_loop = LoopAgent(
    name="revisao_de_qualidade",
    description="Refina a resposta ao cliente até passar nos critérios.",
    sub_agents=[redator, critico],
    max_iterations=3,
)
