# Lab 04: a chave do banco de dados

**Tempo sugerido:** 90 minutos, o setup pesa
**Pré-requisito:** `docker compose up -d`

## A cena

O time de Dados da Aurora não entrega a senha do Postgres para um estagiário.
Entrega um balcão com um cardápio fixo de consultas aprovadas.
Esse balcão é o MCP Toolbox for Databases.

## Verificar a infra antes de começar

```bash
docker compose up -d
docker compose ps                       # postgres, toolbox e mock_api de pé
curl http://localhost:5000/api/toolset  # deve listar as tools do tools.yaml
psql postgresql://aurora:aurora@localhost:5432/aurora_fibra -c "select count(*) from clientes;"
```

```bash
adk run lab04_mcp_toolbox
```

## Roteiro do lab

### 1. Ler o `tools.yaml` antes de ver o código Python (20 min)

Abra o `tools.yaml` e percorra as três seções:

- `sources`: onde está o banco, com credencial vindo de variável de ambiente,
  nunca versionada
- `tools`: cada uma é nome, descrição, parâmetros tipados e uma query parametrizada.
  A `description` aqui faz o mesmo papel da docstring do lab 03,
  é o que o modelo lê para decidir
- `toolsets`: fatias do cardápio. `atendimento_n1`, `cobranca` e `tecnico`

Pergunta para a turma: quantas linhas de Python existem neste arquivo? Zero.

### 2. O agente em duas linhas (10 min)

```python
toolset = ToolboxToolset(server_url="http://localhost:5000", toolset_name="atendimento_n1")
root_agent = LlmAgent(..., tools=[toolset])
```

Compare lado a lado com `lab03_tool_externa/tools.py`.
Lá eram 60 linhas de Python para dois endpoints.
Aqui são cinco tools de banco em duas linhas, com pool de conexão,
query parametrizada e observabilidade resolvidos pelo servidor.

### 3. A demo que vende o conceito (20 min)

Pergunte ao ARI: "tenho fatura em aberto? CPF 111.222.333-44".
Ele responde com a competência 2026-08 vencida.

Agora, sem parar o agente, edite o `tools.yaml` e acrescente
`f.vencimento < NOW() AS atrasada` na query `listar_faturas_em_aberto`.

```bash
docker compose restart toolbox
```

Faça a mesma pergunta. O comportamento mudou.
Nenhuma linha de Python foi tocada, nenhum deploy de agente aconteceu.

Esse é o argumento de governança inteiro, em 30 segundos:
quem manda na query é o time de dados, no ciclo de vida dele,
não o time de IA no ciclo de vida do agente.

### 4. Casos de teste da base (20 min)

| CPF | O que exercita |
|---|---|
| 111.222.333-44 | fatura vencida e chamado de lentidão aberto |
| 444.555.666-77 | contrato suspenso com três faturas vencidas, o caso do protocolo 5 |
| 333.444.555-66 | chamado em andamento com visita já agendada para 16/09 |
| 999.999.999-99 | não existe, para ver o agente admitir que não localizou |

O caso do CPF suspenso é o mais rico: o cliente liga reclamando de internet,
e a resposta certa é de cobrança. Isso é regra de negócio virando instruction,
e é o que separa um agente de demo de um agente de operação.

### 5. Segurança, a parte que não pode ser pulada (20 min)

Pergunte para a turma: o que impede o modelo de passar
o CPF de outra pessoa em `buscar_cliente_por_cpf`?

Resposta honesta: nada, neste lab. O CPF chega como argumento escolhido pelo modelo
a partir do que o usuário digitou. Em produção isso é parâmetro autenticado,
vinculado ao token da sessão, e o modelo nem enxerga o campo.
Esse é o ponto onde a aula deixa de ser demo.

Segundo ponto: existe tool genérica de `execute_sql` disponível no Toolbox,
ótima para explorar schema no IDE, e inaceitável para agente em produção.
Cardápio fechado é feature, não limitação.

## Gotchas

- **O protocolo nativo do Toolbox está depreciado, o padrão hoje é MCP.**
  Tutorial antigo que força `Protocol.TOOLBOX` vai confundir a turma.
- **`toolset_name` errado devolve toolset vazio sem erro claro.**
  O agente fica mudo sobre dados e parece "burro". Cheque `/api/toolset` primeiro.
- **Credencial em `${VAR}`, sempre.** Nunca deixe senha no `tools.yaml`,
  ele vai para o repositório.
- **Tool de escrita precisa de confirmação.** `abrir_chamado` faz INSERT.
  A defesa aqui é a mesma do lab 03: `before_tool_callback`, não instruction.
- **A `description` no YAML é prompt.** Descrição preguiçosa gera tool call errada,
  exatamente como docstring preguiçosa no lab 03.

## A falha planejada

Mande de uma vez:

> "minha fatura venceu e meu roteador está piscando vermelho"

A instruction já tem cinco protocolos disputando espaço,
e o ARI mistura os dois assuntos numa resposta só, ou resolve um e esquece o outro.
Some a isso o fato de que o agente de cobrança não deveria nem enxergar
a tool de abrir chamado técnico.

Esse é o lab 05.
