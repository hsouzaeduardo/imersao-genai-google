"""
LAB 06: o processo operacional.

Três formas de orquestração determinística, em um arquivo só.
Troque PIPELINE_ATIVO e rode `adk run lab06_orquestracao`.

  sequencial  ordem obrigatória, uma etapa alimenta a próxima
  paralelo    verificações independentes ao mesmo tempo, depois consolidação
  loop        refinamento até passar no critério

E o quarto caso, o mais realista: os três combinados.
"""

from google.adk.agents import SequentialAgent

from .pipeline_loop import pipeline_loop
from .pipeline_paralelo import pipeline_paralelo, verificacoes
from .pipeline_sequencial import diagnostico, pipeline_sequencial, triagem

# ------------------------------------------------------------------
# Combinação: verificações em paralelo, depois POP em ordem, depois revisão
# ------------------------------------------------------------------
pipeline_completo = SequentialAgent(
    name="atendimento_aurora_completo",
    description="Verificações paralelas, procedimento padrão e revisão de qualidade.",
    sub_agents=[verificacoes, triagem, diagnostico, pipeline_loop],
)


PIPELINES = {
    "sequencial": pipeline_sequencial,
    "paralelo": pipeline_paralelo,
    "loop": pipeline_loop,
    "completo": pipeline_completo,
}

PIPELINE_ATIVO = "sequencial"

root_agent = PIPELINES[PIPELINE_ATIVO]
