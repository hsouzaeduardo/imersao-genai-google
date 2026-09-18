# Lab 01: primeiro dia, sem crachá

**Tempo sugerido:** 45 minutos
**Pré-requisitos:** `pip install -r requirements.txt` e `.env` com a chave

## A cena

ARI chega na Aurora Fibra. Sabe português, sabe ser educado, não tem acesso a nada.
Recebe o manual de atendimento e é colocado no chat.

## Rodar

```bash
adk web          # na raiz do repositório, escolha lab01_agente_puro
# ou
adk run lab01_agente_puro
```

## Roteiro do lab

### 1. Anatomia de um turno (10 min)

Mande "oi, minha internet está ruim" e abra a aba de eventos no `adk web`.
Mostre os três blocos: evento do usuário, chamada ao LLM, resposta final.
Esse é o ciclo que vai se repetir, cada vez mais complexo, até o lab 06.

### 2. A instruction é código (20 min)

No `agent.py`, troque:

```python
INSTRUCTION_ATIVA = INSTRUCTION_PROTOCOLO
```

por

```python
INSTRUCTION_ATIVA = INSTRUCTION_VAGA
```

Rode exatamente a mesma pergunta nas duas versões:

> "Minha internet está lenta, quando vocês vão consertar?"

Com a versão vaga, ARI inventa previsão de reparo.
Com a versão protocolo, ele classifica o problema e admite que não tem acesso ao sistema.

Isso é o experimento central do lab. Nada mudou no código,
no modelo ou na infraestrutura. Mudou o texto.

### 3. A falha planejada (15 min)

Com a boa instruction ativa, faça esta sequência:

1. "Meu CPF é 111.222.333-44"
2. "Qual o status da minha conexão?"
3. Encerre a sessão, abra uma nova, e pergunte "qual era mesmo o meu CPF?"

Resultados esperados:
na pergunta 2 ele admite que não tem acesso, o que é correto, mas inútil para o cliente.
Na pergunta 3 ele não faz ideia de quem você é, mesmo tendo perguntado dois minutos antes.

Essas duas lacunas são exatamente os labs 02 e 03.

## Gotchas

- **Instruction longa não é instruction boa.** O ganho vem de restrição explícita
  ("nunca invente número de protocolo"), não de volume de texto.
- **O bloco de LIMITES é o que impede alucinação aqui.** Remova ele e rode de novo
  para mostrar a diferença. É a demo mais barata e mais convincente do lab.
- **`description` versus `instruction`.** Neste lab a `description` parece inútil.
  Anote isso: no lab 05 ela vira o campo que decide o roteamento entre agentes.
- Se o `adk web` não listar o agente, confira se a pasta tem `__init__.py`
  com `from . import agent` e se `agent.py` expõe a variável `root_agent`.

## Critério de aprovação

ARI responde dentro do escopo e recusa explicitamente o que não pode fazer,
sem inventar dado nenhum, em cinco perguntas seguidas.
