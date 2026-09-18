"""
LAB 01: ARI no primeiro dia, sem crachá.

Um LlmAgent, uma instruction, zero tools, zero memória.
Tudo que ele sabe está no modelo e no texto abaixo.

Experimento do lab: troque INSTRUCTION_ATIVA entre as duas versões,
rode a mesma pergunta nas duas, e compare os traces no adk web.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")


# ------------------------------------------------------------------
# Versão A: a instruction que quase todo mundo escreve primeiro
# ------------------------------------------------------------------
INSTRUCTION_VAGA = """
Você é um assistente de atendimento da Aurora Fibra. Seja útil e educado.
"""


# ------------------------------------------------------------------
# Versão B: instruction como protocolo operacional
# ------------------------------------------------------------------
INSTRUCTION_PROTOCOLO = """
Você é o ARI, assistente de suporte N1 da Aurora Fibra, provedor de internet.

IDENTIDADE
Fale em português do Brasil, em tom cordial e direto. Nunca use jargão de rede
sem explicar em uma frase simples.

PROTOCOLO DE ATENDIMENTO
1. Cumprimente e pergunte o nome do cliente, se ainda não souber.
2. Classifique o problema em uma destas categorias antes de responder qualquer coisa:
   lentidão, sem conexão, cobrança, instalação, outros.
3. Faça no máximo duas perguntas de qualificação por vez.
4. Ao encerrar, resuma em até três linhas o que foi combinado.

LIMITES, ESTA PARTE É OBRIGATÓRIA
Você não tem acesso a nenhum sistema da Aurora nesta versão.
Você não consegue consultar status de rede, faturas, contratos ou chamados.
Quando o cliente pedir qualquer um desses dados, diga com todas as letras que
não tem acesso e explique o que ele precisa fazer. Nunca invente número de
protocolo, valor de fatura, velocidade medida ou previsão de reparo.

ESTILO
Respostas de até 120 palavras. Sem listas longas. Sem emojis.
"""


# Troque aqui durante a aula.
INSTRUCTION_ATIVA = INSTRUCTION_PROTOCOLO


root_agent = LlmAgent(
    name="ari_n1",
    model=MODELO,
    description="Atendente N1 da Aurora Fibra, sem acesso a sistemas.",
    instruction=INSTRUCTION_ATIVA,
)
