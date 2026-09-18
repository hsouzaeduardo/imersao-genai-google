"""
Demo do lab 06: o cronômetro é o argumento.

    python lab06_orquestracao/run_demo.py

Roda a mesma pergunta em dois desenhos:
  1. três verificações em sequência
  2. as mesmas três em paralelo

E imprime o tempo de parede de cada um.
"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

from lab06_orquestracao.pipeline_paralelo import (
    criar_checagem_financeira,
    criar_checagem_historico,
    criar_checagem_rede,
    criar_consolidador,
    criar_verificacoes,
)

PERGUNTA = (
    "Meu CPF é 44455566677. Minha internet não funciona há dois dias "
    "e eu já liguei antes sobre isso."
)

# Os dois arranjos usam agentes equivalentes, mas nunca as mesmas instâncias:
# no ADK um agente pertence a um único pai, então cada montagem cria os seus.
em_sequencia = SequentialAgent(
    name="abertura_sequencial",
    description="As mesmas três verificações, uma depois da outra.",
    sub_agents=[
        criar_checagem_financeira(),
        criar_checagem_rede(),
        criar_checagem_historico(),
        criar_consolidador(),
    ],
)

em_paralelo = SequentialAgent(
    name="abertura_paralela",
    description="As três verificações ao mesmo tempo, depois consolidação.",
    sub_agents=[criar_verificacoes(), criar_consolidador()],
)


async def rodar(agente, rotulo: str) -> float:
    runner = InMemoryRunner(agent=agente, app_name=f"lab06_{rotulo}")
    await runner.session_service.create_session(
        app_name=f"lab06_{rotulo}", user_id="aluno", session_id="s1"
    )
    conteudo = types.Content(role="user", parts=[types.Part(text=PERGUNTA)])

    print(f"\n\033[94m=== {rotulo.upper()} ===\033[0m")
    inicio = time.perf_counter()
    async for evento in runner.run_async(user_id="aluno", session_id="s1", new_message=conteudo):
        if evento.is_final_response() and evento.content and evento.content.parts:
            texto = (evento.content.parts[0].text or "").strip()
            if texto:
                print(f"\033[90m[{evento.author}]\033[0m {texto[:400]}")
    decorrido = time.perf_counter() - inicio
    print(f"\033[93mTempo de parede: {decorrido:.1f}s\033[0m")
    return decorrido


async def main() -> None:
    t_seq = await rodar(em_sequencia, "sequencial")
    t_par = await rodar(em_paralelo, "paralelo")

    print("\n" + "=" * 52)
    print(f"Sequencial: {t_seq:.1f}s")
    print(f"Paralelo:   {t_par:.1f}s")
    if t_par > 0:
        print(f"Ganho:      {t_seq / t_par:.1f}x")
    print("=" * 52)
    print(
        "\nPergunta para a turma: o ganho é próximo de 3x?"
        "\nSe não for, por quê? Pense no consolidador, que roda sozinho nos dois casos,"
        "\ne na latência do modelo, que não some, só deixa de ser somada."
    )


if __name__ == "__main__":
    asyncio.run(main())
