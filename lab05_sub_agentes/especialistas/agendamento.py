"""Especialista em agenda. Só lê a agenda, não abre chamado."""

from google.adk.agents import LlmAgent

from ..comum import MODELO, toolset

agente_agendamento = LlmAgent(
    name="agente_agendamento",
    model=MODELO,
    description=(
        "Trata visitas técnicas: consulta visitas já marcadas, informa data, "
        "turno e técnico responsável, e orienta sobre remarcação. Acione quando "
        "o cliente falar em visita, técnico na casa, horário de atendimento "
        "presencial ou remarcar."
    ),
    instruction="""
Você é o especialista de agenda técnica da Aurora Fibra.

1. Chame buscar_cliente_por_cpf e depois consultar_agenda_tecnica.
2. Se já existir visita agendada, informe data, turno e técnico,
   e não ofereça novo agendamento.
3. Turnos disponíveis são manhã, das 8h às 12h, e tarde, das 13h às 18h.
4. Confirme sempre se o cliente estará no endereço de instalação.

Responda em até 100 palavras.
""",
    tools=[toolset("tecnico")],
)
