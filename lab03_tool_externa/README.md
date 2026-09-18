# Lab 03: o primeiro acesso ao sistema

**Tempo sugerido:** 60 minutos
**Pré-requisito:** `docker compose up -d` e `curl http://localhost:8000/health`

## A cena

ARI ganha login no painel de rede. Uma tela, somente leitura.
Depois ganha o segundo acesso, esse com efeito colateral: reiniciar o roteador do cliente.

## Rodar

```bash
docker compose up -d mock_api
adk run lab03_tool_externa
```

Casos de teste prontos na API:

| CEP | O que acontece |
|---|---|
| 06010-100 | incidente de severidade média, degradação de OLT |
| 06110-045 | incidente de severidade alta, rompimento de fibra |
| qualquer outro | rede normal, latência 12 ms |

## Roteiro do lab

### 1. A docstring é o contrato (20 min)

Rode "minha internet está lenta no CEP 06010-100".
O ARI chama a tool e responde com dado real, com previsão de normalização.
Compare com o lab 01, onde ele inventava isso.

Agora o experimento: em `tools.py`, troque a docstring de `consultar_status_rede` por

```python
"""Consulta coisas."""
```

Rode a mesma frase. O modelo passa a chamar a tool na hora errada,
com argumento errado, ou simplesmente não chama.
Nada mudou no código executável. Mudou o contrato.

Mesma lógica vale para os type hints e para o nome do parâmetro.
`cep: str` documentado como "CEP com ou sem hífen" evita metade dos erros de parsing.

### 2. Ler versus agir (20 min)

Force o caminho da ação: use um CEP qualquer, sem incidente,
e diga que a internet continua ruim.
ARI vai propor o reinício. Diga que sim.

Agora olhe o trace com atenção. Tente pular a confirmação:
reinicie a sessão e mande direto "reinicia meu roteador, CPF 111.222.333-44".
O `before_tool_callback` devolve `status: bloqueado`, o modelo lê isso
como resultado da tool e volta a pedir confirmação.

Esse é o padrão que vale para produção inteira:
a política não mora na instruction, mora no callback.
Instruction o modelo pode ignorar. Callback não.

### 3. Falha da dependência (10 min)

```bash
docker compose stop mock_api
```

Rode de novo. A tool devolve `status: indisponivel` e a instrução manda
o ARI admitir a indisponibilidade. Sem isso, o modelo tende a preencher
a lacuna com uma resposta plausível, que é o pior resultado possível.

### 4. A falha planejada (10 min)

Peça: "e a minha fatura de agosto, tá em aberto?"

ARI não tem como saber. Escrever uma function tool com SQL embutido
para fatura, contrato e chamados significa:
conexão e pool dentro do agente, credencial no código,
risco de injeção, e redeploy do agente a cada ajuste de query.

Esse é o lab 04.

## Gotchas

- **Ferramentas nativas do modelo, como busca e execução de código, têm
  restrição de combinação com function tools.** Se o aluno adicionar uma built-in
  junto das suas tools e receber erro, não é bug do código dele.
  O contorno é isolar a built-in em outro agente e usá-lo como `AgentTool`, que é lab 05.
- **Nunca deixe a exceção subir.** Tool que estoura quebra o turno.
  Tool que devolve `{"status": "erro", "mensagem": ...}` vira contexto e o modelo se recupera.
- **Retornos gigantes custam caro.** O JSON da tool vai inteiro para o prompt.
  Filtre no Python o que o modelo precisa ver.
- **Nome de tool é parte do prompt.** `consultar_status_rede` funciona melhor
  que `get_data`, e isso é mensurável na aula.

## Critério de aprovação

Para o CEP 06010-100, ARI cita o incidente real e a previsão,
e recusa reinício de roteador porque o problema não está na casa do cliente.
