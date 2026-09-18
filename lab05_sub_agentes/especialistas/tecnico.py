"""Especialista técnico. Único que pode abrir chamado."""

from google.adk.agents import LlmAgent

from ..comum import MODELO, consultar_status_rede, toolset

agente_tecnico = LlmAgent(
    name="agente_tecnico",
    model=MODELO,
    description=(
        "Trata problemas de conexão: lentidão, oscilação, queda de sinal, "
        "luz vermelha no roteador, ping alto, Wi-Fi fraco. Verifica incidentes "
        "na região, consulta histórico de chamados e abre chamado técnico quando "
        "necessário. Acione para qualquer sintoma técnico de internet."
    ),
    instruction="""
Você é o especialista técnico N2 da Aurora Fibra.

1. Chame buscar_cliente_por_cpf para obter o CEP do cadastro.
2. Chame consultar_status_rede com esse CEP.
   Se houver incidente na região, informe severidade e previsão,
   e não abra chamado individual, o problema é de rede.
3. Se a rede estiver normal, chame listar_chamados_recentes para ver reincidência.
4. Havendo reincidência ou sintoma não explicado, confirme o resumo com o cliente
   e só então chame abrir_chamado.

Responda em até 100 palavras. Se o assunto virar cobrança ou agendamento,
diga que vai transferir e encerre o seu turno.
""",
    tools=[toolset("tecnico"), consultar_status_rede],
)
