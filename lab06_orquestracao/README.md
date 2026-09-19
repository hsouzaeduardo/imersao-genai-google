# Lab 06: o processo operacional

**Tempo sugerido:** 80 minutos
**Pré-requisito:** `docker compose up -d`

## A cena

O jurídico e a operação da Aurora escrevem um POP.
Certas etapas não são negociáveis com o bom senso do modelo.

No lab 05 o roteamento era decidido pelo LLM, e a ordem variava entre execuções.
Aqui a ordem vira código.

## Rodar

```bash
# escolha o pipeline no fim de agent.py: sequencial, paralelo, loop ou completo
adk run lab06_orquestracao

# a demo do cronômetro
python lab06_orquestracao/run_demo.py
```

## Roteiro do lab

### 1. Sequencial: a ordem obrigatória (25 min)

`pipeline_sequencial.py`: triagem, diagnóstico, registro.

O que amarra as etapas é o par `output_key` e `{chave}`:

```python
triagem      = LlmAgent(..., output_key="triagem")
diagnostico  = LlmAgent(..., instruction="Resultado da triagem:\n{triagem}\n...")
```

O primeiro grava no state, o segundo lê no prompt. Não existe mágica,
existe um dicionário e uma interpolação.

Rode dez vezes a mesma entrada e compare com o lab 05:
a ordem é idêntica nas dez. Esse é o ponto inteiro da aula.

Exercício: inverta `diagnostico` e `registro` na lista `sub_agents`.
O registro passa a ler uma chave que ainda não existe,
e a resposta sai vazia ou inventada. Ordem é contrato.

### 2. Paralelo: o cronômetro (25 min)

```bash
python lab06_orquestracao/run_demo.py
```

As mesmas três verificações, duas topologias, dois tempos na tela.

Depois abra `pipeline_paralelo.py` e mostre a estrutura real:
`ParallelAgent` para os ramos, e um `SequentialAgent` por fora
para garantir que o consolidador só rode depois que todos terminarem.

Discussão de arquitetura: por que consolidar num agente separado
em vez de deixar um dos ramos concluir? Porque o ramo não enxerga
o resultado dos irmãos, cada um roda isolado e grava a sua chave.

### 3. Loop: o revisor (20 min)

`pipeline_loop.py`: redator e crítico, girando até aprovar.

Rode com um caso difícil, por exemplo um cliente irritado com queda recorrente.
Acompanhe no trace: primeira versão cheia de jargão, crítica apontando os critérios,
segunda versão limpa, aprovação.

A saída do loop acontece quando a tool `aprovar_resposta` seta
`tool_context.actions.escalate = True`. Comente essa linha e rode de novo:
o loop vai até `max_iterations=3` e para por limite, não por qualidade.
Sem o `max_iterations`, roda para sempre.

### 4. O desenho completo (10 min)

Troque `PIPELINE_ATIVO` para `"completo"`.

Verificações em paralelo, depois triagem e diagnóstico em ordem,
depois o loop de revisão na resposta final.

É assim que um atendimento real se parece:
determinístico onde o negócio exige, probabilístico onde o julgamento ajuda.
E agora você consegue apontar no código qual pedaço é qual.

## Gotchas

- **Dois ramos paralelos no mesmo `output_key` se sobrescrevem.**
  Chaves distintas, sempre. É o bug mais comum e o mais silencioso.
- **A ordem de término no paralelo não é determinística.**
  Se o seu consolidador depende de ordem, o desenho está errado.
- **`{chave}` que não existe no state quebra a instruction.**
  Use `{chave?}` para opcional, como no redator do loop.
- **Paralelo não multiplica só velocidade, multiplica custo por minuto e
  pressão sobre rate limit.** Três chamadas simultâneas é três vezes a cota no mesmo instante.
- **`LoopAgent` sem condição de saída e sem `max_iterations` é uma fatura.**
  Sempre os dois, cinto e suspensório.
- **Workflow agent não é LLM.** `SequentialAgent`, `ParallelAgent` e `LoopAgent`
  não têm modelo nem instruction, eles só executam a topologia.
  Quem raciocina são os filhos.
- **Ramo que recebe duas tools de escopos diferentes funde as duas.**
  A `checagem_rede` chama `consultar_status_rede`, que é do CEP daquele cliente,
  e `listar_eventos_massivos`, que é da base inteira. Pedir um único
  `incidente_regiao` no fim fazia o modelo responder `true` para cliente sem
  incidente nenhum, emprestando a severidade do incidente de outro CEP.
  O ramo parecia funcionar: o JSON vinha bem formado e a conduta final não
  mudava, porque o bloqueio financeiro tem precedência. Só aparece quando você
  confere ramo por ramo contra o dado real. A correção foi dizer de qual tool
  sai cada campo e dar chave própria ao contexto da base.

## Critério de aprovação

A mesma entrada, dez execuções, ordem de etapas idêntica nas dez,
e o `run_demo.py` mostrando ganho de tempo mensurável no paralelo.
