"""
LAB 02a: o caderno de anotações do atendimento.

Aqui entra o `state`: a memória de trabalho, válida dentro de uma sessão.
O ARI anota o que o cliente diz e passa a ler essas anotações a cada turno.

Dois pontos que o aluno precisa enxergar no código:
1. tools escrevem no state através de `tool_context.state`
2. a instruction é montada em tempo de execução lendo o state
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import ToolContext

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")


# ------------------------------------------------------------------
# Tools que escrevem no caderno
# ------------------------------------------------------------------
def registrar_identificacao(nome: str, cpf: str, tool_context: ToolContext) -> dict:
    """Registra a identificação do cliente no atendimento em andamento.

    Use assim que o cliente informar nome e CPF. Chame uma única vez por atendimento.

    Args:
        nome: nome completo informado pelo cliente.
        cpf: CPF com ou sem pontuação.

    Returns:
        dict com status e o que foi registrado.
    """
    apenas_digitos = "".join(c for c in cpf if c.isdigit())
    if len(apenas_digitos) != 11:
        return {"status": "erro", "mensagem": "CPF precisa ter 11 dígitos."}

    # prefixo "user:" faz o dado valer para todas as sessões deste usuário
    tool_context.state["user:nome"] = nome
    tool_context.state["user:cpf"] = apenas_digitos
    return {"status": "ok", "nome": nome, "cpf": apenas_digitos}


def anotar_sintoma(categoria: str, descricao: str, tool_context: ToolContext) -> dict:
    """Anota um sintoma relatado pelo cliente no caderno do atendimento.

    Args:
        categoria: uma entre lentidao, sem_conexao, cobranca, instalacao, outros.
        descricao: o relato do cliente em uma frase.

    Returns:
        dict com status e a lista atualizada de sintomas.
    """
    validas = {"lentidao", "sem_conexao", "cobranca", "instalacao", "outros"}
    if categoria not in validas:
        return {
            "status": "erro",
            "mensagem": f"Categoria inválida. Use uma de: {', '.join(sorted(validas))}.",
        }

    sintomas = list(tool_context.state.get("sintomas", []))
    sintomas.append({"categoria": categoria, "descricao": descricao})
    tool_context.state["sintomas"] = sintomas
    return {"status": "ok", "sintomas": sintomas}


def encerrar_atendimento(resumo: str, tool_context: ToolContext) -> dict:
    """Fecha o atendimento gravando o resumo do que foi combinado.

    Args:
        resumo: até três linhas com o que foi combinado com o cliente.

    Returns:
        dict com status e o resumo gravado.
    """
    tool_context.state["resumo_atendimento"] = resumo
    return {"status": "ok", "resumo": resumo}


# ------------------------------------------------------------------
# Instruction dinâmica: lida do state a cada turno
# ------------------------------------------------------------------
BASE = """
Você é o ARI, assistente de suporte N1 da Aurora Fibra.
Fale em português do Brasil, tom cordial e direto, respostas de até 120 palavras.

PROTOCOLO
1. Se ainda não souber quem é o cliente, peça nome e CPF e chame registrar_identificacao.
2. A cada problema relatado, chame anotar_sintoma com a categoria correta.
3. Nunca pergunte de novo algo que já está no seu caderno abaixo.
4. Ao encerrar, chame encerrar_atendimento com o resumo.

LIMITES
Você ainda não tem acesso a status de rede, faturas ou chamados.
Nunca invente esses dados.
"""


def instruction_com_caderno(ctx: ReadonlyContext) -> str:
    """Monta a instruction do turno anexando o caderno atual."""
    state = ctx.state
    nome = state.get("user:nome")
    cpf = state.get("user:cpf")
    sintomas = state.get("sintomas", [])

    if not nome and not sintomas:
        caderno = "CADERNO DO ATENDIMENTO\n(vazio, este é o começo da conversa)"
    else:
        linhas = ["CADERNO DO ATENDIMENTO"]
        if nome:
            linhas.append(f"Cliente: {nome} (CPF {cpf})")
        if sintomas:
            linhas.append("Sintomas já anotados:")
            for i, s in enumerate(sintomas, start=1):
                linhas.append(f"  {i}. [{s['categoria']}] {s['descricao']}")
        caderno = "\n".join(linhas)

    return f"{BASE}\n\n{caderno}"


root_agent = LlmAgent(
    name="ari_com_caderno",
    model=MODELO,
    description="Atendente N1 da Aurora com memória de trabalho dentro da sessão.",
    instruction=instruction_com_caderno,
    tools=[registrar_identificacao, anotar_sintoma, encerrar_atendimento],
)
