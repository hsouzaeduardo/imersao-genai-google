# Lab 02a: o caderno de anotações

**Tempo sugerido:** 50 minutos
**Conceito:** estado de sessão, a memória de trabalho do agente

## A cena

ARI ganha um caderno. Durante o atendimento ele anota quem é o cliente
e o que foi relatado, e passa a consultar essas anotações a cada turno.

## Rodar

```bash
adk web                                              # interativo
python lab02_memoria/a_estado_sessao/run_demo.py     # demo da persistência
python lab02_memoria/a_estado_sessao/run_demo.py --continuar
```

## Roteiro do lab

### 1. O state escrito pela tool (15 min)

Abra `agent.py` e mostre as três linhas que fazem tudo:

```python
tool_context.state["user:nome"] = nome
tool_context.state["user:cpf"] = apenas_digitos
tool_context.state["sintomas"] = sintomas
```

No `adk web`, aba State, o aluno vê as chaves aparecendo em tempo real
conforme conversa. Esse é o momento "ah, então é só um dicionário".
Sim, é só um dicionário, e é isso que torna o conceito ensinável.

### 2. O state lido pela instruction (15 min)

A instruction aqui não é string, é função. O ADK chama
`instruction_com_caderno(ctx)` a cada turno e injeta o caderno no prompt.

Pergunte ao ARI algo que ele já sabe. Ele não pergunta de novo.
Apague o bloco do caderno na função, rode igual, e ele volta a perguntar.
É a prova de que o state só existe para o modelo se alguém colocar no prompt.

### 3. A persistência (20 min)

```bash
python lab02_memoria/a_estado_sessao/run_demo.py
python lab02_memoria/a_estado_sessao/run_demo.py --continuar
```

Entre as duas execuções o processo Python morreu inteiro.
O `DatabaseSessionService` gravou tudo em `aurora_sessoes.db`.
Abra o arquivo com qualquer cliente SQLite e mostre a tabela de sessões.

Troque para `InMemorySessionService` e repita: a segunda execução esquece tudo.
Essa é a diferença entre demo e produção, em uma linha de código.

## Gotchas

- **Prefixos de escopo mudam o significado da chave.**
  `nome` vale nesta sessão. `user:nome` vale para todas as sessões do usuário.
  `app:` vale para a aplicação inteira. `temp:` não é persistido.
  Aluno que usa chave sem prefixo para preferência do cliente vai perder o dado.
- **State não é memória de longo prazo.** Ele resolve o atendimento atual.
  Recuperar "o que combinamos no mês passado" é o lab 02b.
- **Mutação em lugar não persiste de forma confiável.**
  Prefira reatribuir a chave, como no `anotar_sintoma`, em vez de dar `append`
  direto na lista que veio do state.
- **State cresce.** Tudo que entra ali vai para o prompt em algum momento,
  e prompt é fatura. Defina o que merece ser anotado.

## Critério de aprovação

Na execução com `--continuar`, ARI responde corretamente CPF e sintomas
informados na execução anterior, sem que nada disso esteja na conversa atual.
