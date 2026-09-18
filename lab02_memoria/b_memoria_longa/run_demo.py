"""
Demo do lab 02b: duas sessões diferentes, o mesmo cliente.

    python lab02_memoria/b_memoria_longa/run_demo.py

Sessão 1: o cliente conta preferências e o problema.
Fim da sessão 1: a conversa vira memória.
Sessão 2: sessão nova, state zerado, e mesmo assim o ARI lembra.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from lab02_memoria.b_memoria_longa.agent import root_agent

APP = "aurora_lab02b"
USER = "cliente_marcela"


async def falar(runner: Runner, sessao_id: str, texto: str) -> None:
    print(f"\n\033[1mCliente:\033[0m {texto}")
    conteudo = types.Content(role="user", parts=[types.Part(text=texto)])
    async for evento in runner.run_async(user_id=USER, session_id=sessao_id, new_message=conteudo):
        for fc in evento.get_function_calls() or []:
            print(f"  \033[90m[tool] {fc.name}({fc.args})\033[0m")
        if evento.is_final_response() and evento.content and evento.content.parts:
            print(f"\033[1mARI:\033[0m {evento.content.parts[0].text.strip()}")


async def main() -> None:
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    runner = Runner(
        app_name=APP,
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )

    # ---------------- Sessão 1 ----------------
    print("\033[94m=== ATENDIMENTO 1, terça-feira ===\033[0m")
    await session_service.create_session(app_name=APP, user_id=USER, session_id="atend_01")
    await falar(runner, "atend_01", "oi, sou a Marcela, CPF 111.222.333-44, internet lenta à noite")
    await falar(runner, "atend_01", "se precisar de visita técnica, só de manhã, e me avise por WhatsApp, nunca por telefone")

    # A conversa vira prontuário. Este passo é explícito de propósito.
    sessao1 = await session_service.get_session(app_name=APP, user_id=USER, session_id="atend_01")
    await memory_service.add_session_to_memory(sessao1)
    print("\n\033[93m>>> Sessão 1 arquivada na memória de longo prazo.\033[0m")

    # ---------------- Sessão 2 ----------------
    print("\n\033[94m=== ATENDIMENTO 2, três semanas depois, sessão nova ===\033[0m")
    await session_service.create_session(app_name=APP, user_id=USER, session_id="atend_02")
    await falar(runner, "atend_02", "oi, voltou a ficar lenta. dá pra mandar um técnico?")
    await falar(runner, "atend_02", "vocês já sabem meu horário e como falar comigo, né?")

    print(
        "\n\033[93mVerificação: o ARI propôs manhã e WhatsApp sem perguntar?"
        "\nSe sim, a memória funcionou. Se ele perguntou de novo, olhe o trace:"
        "\nprovavelmente ele não chamou load_memory.\033[0m"
    )


if __name__ == "__main__":
    asyncio.run(main())
