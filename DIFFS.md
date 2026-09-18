# O que muda de um lab para o outro

Uma tela para se localizar quando a turma se perder.
Cada linha é o mínimo que precisa mudar no código para o agente ganhar a capacidade nova.

---

## Lab 01 para 02a: o agente ganha caderno

```diff
+ from google.adk.tools import ToolContext
+
+ def registrar_identificacao(nome: str, cpf: str, tool_context: ToolContext) -> dict:
+     tool_context.state["user:nome"] = nome
+     return {"status": "ok"}

  root_agent = LlmAgent(
      name="ari_n1",
-     instruction=INSTRUCTION_PROTOCOLO,
+     instruction=instruction_com_caderno,   # função, lê o state a cada turno
+     tools=[registrar_identificacao, anotar_sintoma, encerrar_atendimento],
  )
```

E no runner:

```diff
- session_service = InMemorySessionService()
+ session_service = DatabaseSessionService(db_url="sqlite:///./aurora_sessoes.db")
```

## Lab 02a para 02b: o caderno vira prontuário

```diff
+ from google.adk.tools import load_memory

  root_agent = LlmAgent(
-     tools=[registrar_identificacao, anotar_sintoma, encerrar_atendimento],
+     tools=[load_memory],
+     after_agent_callback=gravar_memoria_ao_fim,
  )
```

E alguém precisa arquivar a sessão, senão a memória fica vazia para sempre:

```diff
+ runner = Runner(..., memory_service=InMemoryMemoryService())
+ await memory_service.add_session_to_memory(sessao_encerrada)
```

## Lab 02b para 03: o agente ganha acesso a um sistema

```diff
+ def consultar_status_rede(cep: str) -> dict:
+     """Docstring é o contrato que o modelo lê."""
+     resposta = httpx.get(f"{API}/status-rede/{cep}", timeout=8.0)
+     return {"status": "ok", "dados": resposta.json()}

  root_agent = LlmAgent(
-     tools=[load_memory],
+     tools=[consultar_status_rede, registrar_autorizacao_reinicio, reiniciar_roteador],
+     before_tool_callback=guardrail_acao_destrutiva,   # política fora da instruction
  )
```

## Lab 03 para 04: as tools saem do agente

```diff
- def consultar_fatura(cpf: str) -> dict:
-     conn = psycopg.connect(DSN)          # conexão dentro do agente
-     cur.execute("SELECT ... WHERE cpf = %s", (cpf,))
-     ...                                   # e mais quatro funções iguais a essa

+ from google.adk.tools.toolbox_toolset import ToolboxToolset
+ toolset = ToolboxToolset(server_url="http://localhost:5000", toolset_name="atendimento_n1")

  root_agent = LlmAgent(
-     tools=[consultar_status_rede, consultar_fatura, listar_chamados, ...],
+     tools=[toolset, consultar_status_rede],
  )
```

O que sumiu do Python apareceu em `tools.yaml`, que pertence ao time de dados
e tem ciclo de vida próprio.

## Lab 04 para 05: um agente vira quatro

```diff
- root_agent = LlmAgent(
-     name="ari_com_dados",
-     instruction=INSTRUCTION_COM_CINCO_PROTOCOLOS,
-     tools=[toolset("atendimento_n1"), consultar_status_rede],
- )

+ agente_cobranca = LlmAgent(description="Acione para fatura, boleto...", tools=[toolset("cobranca")])
+ agente_tecnico  = LlmAgent(description="Acione para lentidão, queda...",  tools=[toolset("tecnico"), consultar_status_rede])
+
+ root_agent = LlmAgent(
+     name="ari_coordenador",
+     instruction="SEU TRABALHO É ROTEAR, NÃO RESOLVER.",
+     sub_agents=[agente_cobranca, agente_tecnico, agente_agendamento],
+ )
```

Variante do mesmo lab, com efeito diferente:

```diff
- sub_agents=[agente_cobranca, agente_tecnico]      # transfere o controle
+ tools=[AgentTool(agent=agente_cobranca),          # chama e devolve
+        AgentTool(agent=agente_tecnico)]
```

## Lab 05 para 06: a ordem sai do prompt e entra no código

```diff
- root_agent = LlmAgent(
-     instruction="resolva cobrança primeiro, depois o técnico",   # pedido, não garantia
-     sub_agents=[agente_cobranca, agente_tecnico],
- )

+ triagem     = LlmAgent(..., output_key="triagem")
+ diagnostico = LlmAgent(..., instruction="Triagem: {triagem}", output_key="diagnostico")
+ registro    = LlmAgent(..., instruction="Diagnóstico: {diagnostico}")
+
+ root_agent = SequentialAgent(sub_agents=[triagem, diagnostico, registro])
```

Paralelo, para etapas independentes:

```diff
+ verificacoes = ParallelAgent(sub_agents=[check_financeiro, check_rede, check_historico])
+ root_agent   = SequentialAgent(sub_agents=[verificacoes, consolidador])
```

Loop, para refinamento com critério de saída:

```diff
+ def aprovar_resposta(tool_context: ToolContext) -> dict:
+     tool_context.actions.escalate = True      # esta linha encerra o loop
+     return {"status": "aprovada"}
+
+ root_agent = LoopAgent(sub_agents=[redator, critico], max_iterations=3)
```

---

## O quadro inteiro

| | Lab 01 | Lab 02 | Lab 03 | Lab 04 | Lab 05 | Lab 06 |
|---|---|---|---|---|---|---|
| Agentes | 1 | 1 | 1 | 1 | 4 | 4 a 7 |
| Tools | 0 | 3 locais | 3 externas | 5 via MCP | isoladas por papel | por etapa |
| Memória | nenhuma | state e memória | state | state | state | state |
| Quem decide a ordem | o modelo | o modelo | o modelo | o modelo | o modelo | o código |
| Onde mora a política | instruction | instruction | callback | YAML e callback | topologia | topologia |
