"""
LAB 04: a chave do banco de dados.

Compare com o lab 03. Lá, cada acesso a dado era uma função Python
com conexão, tratamento e query dentro do agente.
Aqui, o agente carrega um toolset de um servidor MCP e não sabe
nem que existe um Postgres do outro lado.

As tools vivem em tools.yaml. Mudar uma query é reiniciar o Toolbox,
não redeployar o agente. Esse desacoplamento é o conteúdo do lab.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .tools_rede import consultar_status_rede

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://localhost:5000")

# O SDK mudou de casa entre versões. Este bloco funciona nas duas.
try:
    from google.adk.tools.toolbox_toolset import ToolboxToolset
except ImportError:  # pragma: no cover
    from toolbox_adk import ToolboxToolset


def carregar_toolset():
    """Carrega o cardápio de consultas aprovadas do servidor Toolbox.

    Sem `toolset_name`, o agente recebe todas as tools publicadas.
    Com `toolset_name`, ele recebe só a fatia que lhe cabe,
    que é o que vamos usar no lab 05.
    """
    try:
        return ToolboxToolset(server_url=TOOLBOX_URL, toolset_name="atendimento_n1")
    except TypeError:
        # versões antigas do SDK não aceitam toolset_name
        return ToolboxToolset(server_url=TOOLBOX_URL)


INSTRUCTION = """
Você é o ARI, assistente de suporte N1 da Aurora Fibra.
Fale em português do Brasil, tom cordial e direto, respostas de até 120 palavras.

PROTOCOLO
1. Se o cliente ainda não informou o CPF, peça. Assim que tiver o CPF,
   inclusive quando ele vier já na primeira mensagem, chame buscar_cliente_por_cpf
   antes de qualquer outra consulta. Passe apenas dígitos, sem pontos nem hífen.
2. Assunto de cobrança: chame listar_faturas_em_aberto e informe competência,
   valor e vencimento. Não negocie desconto, não prometa prazo de baixa.
3. Assunto técnico: chame consultar_status_rede com o CEP do cadastro,
   e chame listar_chamados_recentes para verificar reincidência.
4. Antes de oferecer visita técnica, chame consultar_agenda_tecnica.
   Se já existir visita agendada, informe a data em vez de agendar outra.
5. Se o contrato estiver suspenso por inadimplência, trate a cobrança primeiro.
   Suporte técnico em contrato suspenso não resolve nada.

LIMITES
Use exclusivamente o que as tools retornarem. Se uma tool vier vazia,
diga que não localizou o registro. Nunca preencha lacuna com suposição.
"""


root_agent = LlmAgent(
    name="ari_com_dados",
    model=MODELO,
    description="Atendente N1 da Aurora com acesso ao painel de rede e à base de clientes.",
    instruction=INSTRUCTION,
    tools=[carregar_toolset(), consultar_status_rede],
)
