# Lab 05: promovido a líder de equipe

**Tempo sugerido:** 70 minutos
**Pré-requisito:** `docker compose up -d`

## A cena

A Aurora contrata mais três estagiários. ARI vira coordenador e para de atender.
Cada especialista fica com a fatia de tools que lhe cabe,
e o agente de cobrança nunca enxerga a tool que abre chamado técnico.

## Rodar

```bash
adk run lab05_sub_agentes
```

## Roteiro do lab

### 1. Por que dividir (10 min)

Abra o `lab04_mcp_toolbox/agent.py` e conte os protocolos na instruction: cinco.
Agora imagine o time de cobrança querendo mudar a regra de religação.
Ele mexe no mesmo arquivo que o time técnico. Não escala.

Divisão de agentes não é elegância arquitetural, é limite de contexto
e limite organizacional, nessa ordem.

### 2. A description é o roteador (25 min)

Este é o experimento central do lab.

Rode: "minha internet caiu e o roteador está com luz vermelha".
O trace mostra a transferência para `agente_tecnico`.

Agora, em `especialistas/tecnico.py`, troque a description por:

```python
description="Agente técnico."
```

Rode a mesma frase. O roteamento fica instável,
e frases ambíguas passam a cair no especialista errado.

A instruction não mudou, as tools não mudaram.
O coordenador só enxerga nome e description dos filhos na hora de decidir.
É esse texto que precisa dizer **quando acionar**, não **o que o agente é**.

### 3. Isolamento de tools (10 min)

Peça ao agente de cobrança, já transferido, para abrir um chamado técnico.
Ele não consegue, porque `abrir_chamado` não está no toolset `cobranca`.

Compare com a alternativa que quase todo mundo tenta primeiro:
um agente com todas as tools e uma instruction dizendo "não use esta tool para aquilo".
A primeira versão é arquitetura. A segunda é torcida.

### 4. Sub agente versus AgentTool (15 min)

Em `agent.py`, troque a última linha para usar o agente de `agent_tool_demo.py`:

```python
from .agent_tool_demo import root_agent_como_tool as root_agent
```

Rode nos dois modos a frase de dois assuntos:

> "minha fatura venceu e o roteador está piscando vermelho"

| | sub_agents | AgentTool |
|---|---|---|
| Quem fala com o cliente | o especialista | o coordenador |
| Trace | evento de transferência | tool call e tool response |
| Resposta | duas vozes, em sequência | uma voz, integrada |
| Quando usar | o especialista conduz a conversa | você precisa juntar várias consultas |

### 5. O limite da delegação por LLM (10 min)

Rode a frase de dois assuntos dez vezes seguidas, sessão nova a cada vez,
e anote a ordem das transferências.

Ela vai variar. Em algumas execuções o técnico vem primeiro,
mesmo com a instruction mandando resolver cobrança antes.

Isso não é bug de prompt, é a natureza da decisão:
roteamento por LLM é probabilístico.
Quando o compliance exige ordem fixa, prompt não é o instrumento certo.

Esse é o lab 06.

## Gotchas

- **`description` vaga é a causa número um de bug neste lab.** Ela é prompt de roteamento.
- **Um agente só pode ter um pai.** Reaproveitar a mesma instância em duas árvores quebra.
  Crie outra instância ou use `AgentTool`.
- **Sub agente não herda a conversa inteira automaticamente.**
  O que ele enxerga passa pelo state e pelo histórico da sessão. Se o especialista
  "esqueceu" o CPF, grave no state em vez de confiar no repasse.
- **Depois da transferência, o especialista continua no comando nos turnos seguintes.**
  Se o assunto mudar, ele precisa saber devolver. Por isso a última linha da instruction
  de cada especialista manda encerrar o turno quando o assunto sair do escopo.
- **Nome de agente entra no prompt do roteador.** `agente_cobranca` roteia melhor que `agent2`.

## Critério de aprovação

Para "minha fatura venceu e o roteador está piscando vermelho",
o coordenador aciona cobrança e técnico, nessa ordem,
e nenhum especialista usa tool fora do seu toolset.
