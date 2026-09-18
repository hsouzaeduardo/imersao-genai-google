"""
Demo do lab 02a: a sessão sobrevive ao fim do processo.

Rode uma vez:      python lab02_memoria/a_estado_sessao/run_demo.py
Rode de novo:      python lab02_memoria/a_estado_sessao/run_demo.py --continuar

Na segunda execução o processo é outro, o objeto Runner é outro,
e mesmo assim o ARI ainda sabe quem é o cliente, porque o state
está no SQLite e não na RAM.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from lab02_memoria.a_estado_sessao.agent import root_agent

APP = "aurora_lab02a"
USER = "cliente_marcela"
SESSAO = "atendimento_001"
DB_URL = "sqlite:///./aurora_sessoes.db"


async def falar(runner: Runner, texto: str) -> None:
    print(f"\n\033[1mCliente:\033[0m {texto}")
    conteudo = types.Content(role="user", parts=[types.Part(text=texto)])
    async for evento in runner.run_async(user_id=USER, session_id=SESSAO, new_message=conteudo):
        if evento.get_function_calls():
            for fc in evento.get_function_calls():
                print(f"  \033[90m[tool] {fc.name}({fc.args})\033[0m")
        if evento.is_final_response() and evento.content and evento.content.parts:
            print(f"\033[1mARI:\033[0m {evento.content.parts[0].text.strip()}")


async def main() -> None:
    continuar = "--continuar" in sys.argv

    session_service = DatabaseSessionService(db_url=DB_URL)
    runner = Runner(app_name=APP, agent=root_agent, session_service=session_service)

    sessao = await session_service.get_session(app_name=APP, user_id=USER, session_id=SESSAO)
    if sessao is None:
        sessao = await session_service.create_session(app_name=APP, user_id=USER, session_id=SESSAO)
        print("Sessão nova criada.")
    else:
        print("Sessão existente recuperada do SQLite.")
        print(f"State atual: {dict(sessao.state)}")

    if not continuar:
        await falar(runner, "boa tarde, minha internet está muito lenta à noite")
        await falar(runner, "meu nome é Marcela Tavares Pinto e meu CPF é 111.222.333-44")
        await falar(runner, "além disso, ontem caiu tudo por umas duas horas")
        print("\n\033[93mAgora rode de novo com --continuar. O processo morre, o caderno não.\033[0m")
    else:
        await falar(runner, "você ainda lembra do meu CPF e do que eu reclamei?")

    final = await session_service.get_session(app_name=APP, user_id=USER, session_id=SESSAO)
    print(f"\n\033[90mState persistido: {dict(final.state)}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
