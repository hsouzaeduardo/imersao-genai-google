"""
LAB 06: o processo operacional.

Três formas de orquestração determinística, em um arquivo só.
Troque PIPELINE_ATIVO e rode `adk run lab06_orquestracao`.

  sequencial  ordem obrigatória, uma etapa alimenta a próxima
  paralelo    verificações independentes ao mesmo tempo, depois consolidação
  loop        refinamento até passar no critério

E o quarto caso, o mais realista: os três combinados.

Repare que o combinado é montado pelas funções `criar_*`, não pelas
instâncias já usadas nos outros pipelines. No ADK um agente pertence a
um único pai, então reaproveitar a mesma instância em dois pipelines
quebra na construção. Cada arranjo recebe agentes próprios.
"""

from google.adk.agents import SequentialAgent

from .pipeline_loop import criar_pipeline_loop, pipeline_loop
from .pipeline_paralelo import criar_verificacoes, pipeline_paralelo
from .pipeline_sequencial import criar_diagnostico, criar_triagem, pipeline_sequencial

# ------------------------------------------------------------------
# Combinação: verificações em paralelo, depois POP em ordem, depois revisão
# ------------------------------------------------------------------
pipeline_completo = SequentialAgent(
    name="atendimento_aurora_completo",
    description="Verificações paralelas, procedimento padrão e revisão de qualidade.",
    sub_agents=[
        criar_verificacoes(),
        criar_triagem(),
        criar_diagnostico(),
        criar_pipeline_loop(),
    ],
)


PIPELINES = {
    "sequencial": pipeline_sequencial,
    "paralelo": pipeline_paralelo,
    "loop": pipeline_loop,
    "completo": pipeline_completo,
}

PIPELINE_ATIVO = "sequencial"

root_agent = PIPELINES[PIPELINE_ATIVO]
