# Índice dos labs

O roteiro detalhado de cada lab está no README da própria pasta, junto do código
que ele explica. Esta página é o mapa: o que cada um pede para rodar, quanto tempo
leva e qual falha ele abre.

Para a condução da aula, tempo por bloco e falas, veja [ROTEIRO_AULA.md](ROTEIRO_AULA.md).

## A escada

| Lab | Roteiro | Tempo | Conceito | Falha que ele deixa aberta |
|---|---|---|---|---|
| 01 | [lab01_agente_puro](../lab01_agente_puro/README.md) | 45 min | `LlmAgent`, instruction como código | esquece tudo entre turnos |
| 02a | [a_estado_sessao](../lab02_memoria/a_estado_sessao/README.md) | 50 min | `SessionService`, `state`, `output_key` | esquece entre atendimentos |
| 02b | [b_memoria_longa](../lab02_memoria/b_memoria_longa/README.md) | 50 min | `MemoryService`, `load_memory` | lembra do cliente, mas inventa os dados dele |
| 03 | [lab03_tool_externa](../lab03_tool_externa/README.md) | 60 min | `FunctionTool`, docstring como contrato | cada novo dado é mais código Python no agente |
| 04 | [lab04_mcp_toolbox](../lab04_mcp_toolbox/README.md) | 90 min | MCP Toolbox, `tools.yaml` | uma instruction só, com cinco protocolos brigando |
| 05 | [lab05_sub_agentes](../lab05_sub_agentes/README.md) | 70 min | `sub_agents`, `description` como roteador | a ordem das etapas varia entre execuções |
| 06 | [lab06_orquestracao](../lab06_orquestracao/README.md) | 80 min | `SequentialAgent`, `ParallelAgent`, `LoopAgent` | delegar só funciona dentro do seu framework |
| 07 | [lab07_a2a_interop](../lab07_a2a_interop/README.md) | 70 min | A2A, agent card, `RemoteA2aAgent` | — |

## O que cada lab exige no ar

| Lab | Chave do modelo | Postgres | Toolbox | mock_api | Outro |
|---|---|---|---|---|---|
| 01 | sim | — | — | — | — |
| 02a | sim | — | — | — | grava `aurora_sessoes.db` local |
| 02b | sim | — | — | — | Memory Bank real pede Vertex AI |
| 03 | sim | — | — | **sim** | — |
| 04 | sim | **sim** | **sim** | **sim** | o agente também consulta o painel de rede |
| 05 | sim | **sim** | **sim** | **sim** | — |
| 06 | sim | **sim** | **sim** | **sim** | — |
| 07 | sim | — | — | — | servidor A2A na porta 9999 |

O lab 07 é o único que roda com uma parte sem LLM nenhum: o `servidor_stub.py`
responde por regra, então dá para ver o protocolo funcionando antes de ter
qualquer credencial.

## Subir a infra

```bash
cp .env.example .env          # e preencha GOOGLE_API_KEY
pip install -r requirements.txt

docker compose up -d          # postgres, toolbox e mock_api
curl http://localhost:8000/health
curl http://localhost:5000/healthz
```

Para o lab 07, numa janela separada:

```bash
python lab07_a2a_interop/maf_retencao/servidor_stub.py
curl http://localhost:9999/.well-known/agent-card.json
```

## Caminhos mais curtos

**Só tenho a chave do modelo, sem Docker.** Labs 01, 02a e 02b rodam inteiros.
O lab 07 roda com o servidor stub. São quatro labs sem infra nenhuma.

**Quero mostrar governança de dados em uma hora.** Lab 04 direto, com a infra
já subida antes. Leia o `tools.yaml` antes do código Python.

**Quero mostrar multiagente em uma hora.** Lab 05 e depois lab 07. O 05 mostra
delegação dentro do framework, o 07 mostra o que fazer quando ela não basta.

## Ordem que importa

Os labs 01 a 06 são uma escada: cada um só faz sentido depois de ver o anterior
falhar. Pular quebra a narrativa, porque o remédio aparece antes da dor.

O lab 07 é a exceção. Ele depende do 01 e do 05, mas não do 04 nem do 06, e
funciona bem como módulo avulso para quem já conhece ADK.
