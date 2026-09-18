# Roteiro de condução

Formato de referência: dois encontros de 4 horas.
Versão compacta de 8 horas em um dia no fim do documento.

---

## Encontro 1: do zero ao dado real

| Bloco | Tempo | Conteúdo | Momento chave |
|---|---|---|---|
| Abertura | 15 min | a história da Aurora Fibra e o contrato do curso | "vocês vão ver o agente quebrar seis vezes, de propósito" |
| Lab 01 | 45 min | agente puro, instruction como código | trocar instruction vaga por protocolo, mesma pergunta |
| Lab 02a | 50 min | state, escopos, persistência | matar o processo e a sessão sobreviver |
| Intervalo | 15 min | | |
| Lab 02b | 50 min | memória de longo prazo, load versus preload | comentar a linha de arquivamento e ver a memória sumir |
| Lab 03 | 60 min | function tool, docstring como contrato, guardrail | trocar a docstring por "Consulta coisas" |
| Fechamento | 25 min | recapitulação e a falha que abre o dia 2 | pedir a fatura e o agente não ter como saber |

## Encontro 2: do dado real ao processo

| Bloco | Tempo | Conteúdo | Momento chave |
|---|---|---|---|
| Retomada | 15 min | o quadro do DIFFS.md | onde estamos na escada |
| Lab 04 | 90 min | MCP Toolbox, governança de acesso a dados | editar o tools.yaml, reiniciar só o Toolbox, comportamento muda |
| Intervalo | 15 min | | |
| Lab 05 | 70 min | sub agentes, description como roteador, AgentTool | apagar a description e ver o roteamento desandar |
| Lab 06 | 80 min | sequencial, paralelo, loop | o cronômetro do run_demo.py na tela |
| Fechamento | 30 min | o que falta para produção | avaliação, observabilidade, custo, deploy |

---

## As seis demos que não podem falhar

Se o tempo apertar, corte exercício, nunca estas seis.

1. **Lab 01**: a mesma pergunta com instruction vaga e com instruction protocolo.
   Prova que prompt é código.
2. **Lab 02a**: `run_demo.py`, depois `run_demo.py --continuar`.
   Prova que estado é infraestrutura, não truque de prompt.
3. **Lab 02b**: comentar `add_session_to_memory` e ver o agente esquecer.
   Prova que memória tem escrita, e que ela é sua responsabilidade.
4. **Lab 03**: docstring trocada por "Consulta coisas".
   Prova que a documentação é o contrato com o modelo.
5. **Lab 04**: editar o `tools.yaml`, `docker compose restart toolbox`, comportamento novo.
   Prova o desacoplamento entre time de dados e time de IA.
6. **Lab 06**: `run_demo.py` com os dois tempos na tela.
   Prova que topologia é decisão de arquitetura com efeito medível.

---

## Falas que funcionam

**Na abertura do lab 03, antes de escrever a tool:**
o agente do lab anterior era eloquente e inútil. Eloquência sem acesso a dado
é a definição operacional de alucinação corporativa.

**Na abertura do lab 04:**
ninguém dá a senha do banco de produção para um estagiário no primeiro mês.
Dá um formulário com as consultas que ele pode fazer. É exatamente isso que vamos construir.

**No fim do lab 05, depois das dez execuções com ordem variável:**
o modelo não desobedeceu. Ele fez uma escolha razoável entre duas opções razoáveis.
O problema não é o modelo, é você ter colocado uma regra de compliance
num lugar que só aceita sugestão.

**No fechamento do lab 06:**
a pergunta que vale para o resto da carreira de vocês não é "dá para fazer com agente?".
É "qual parte disso precisa ser determinística?". Responder isso é arquitetura.
O resto é configuração.

---

## Perguntas que a turma sempre faz

**"Isso não fica caro?"**
Fica, e o lab 06 mostra onde. Três ramos paralelos são três chamadas simultâneas.
Custo por atendimento é métrica de produto, e entra no desenho desde o começo,
não na fatura do mês seguinte.

**"Por que não fazer tudo com um prompt gigante?"**
Funciona até uns três domínios. Depois você não consegue testar mudança isolada,
não consegue dar ownership por time, e cada ajuste no fluxo de cobrança
arrisca quebrar o fluxo técnico.

**"Dá para usar outro modelo?"**
Dá, o ADK não obriga Gemini. O que muda de verdade entre modelos aqui
é a qualidade da decisão de chamar tool, e isso se mede, não se opina.

**"E se a tool devolver dado errado?"**
O agente vai repetir com convicção. Por isso o guardrail do lab 03 e o
cardápio fechado do lab 04. Confiabilidade do agente é limitada pela
confiabilidade da tool, sempre.

**"Como eu testo isso?"**
Fora do escopo dos seis labs e é o assunto natural do próximo módulo:
conjunto de avaliação, trace comparado, métrica por etapa.

---

## Versão de 8 horas em um dia

Mesma sequência, com os cortes:

- Lab 02b reduzido para demo conduzida pelo instrutor, 25 minutos
- Lab 04 com a infra já subida antes da aula, economiza 25 minutos
- Lab 05 sem o experimento do AgentTool, que vira exercício para casa
- Lab 06 só sequencial e paralelo, o loop vira demo de 10 minutos

---

## Checklist do instrutor, véspera

- [ ] `docker compose up -d` rodando e `curl localhost:5000/api/toolset` respondendo
- [ ] `.env` com chave válida e cota conferida, aula com 30 alunos consome
- [ ] `aurora_sessoes.db` apagado, para o lab 02a começar limpo
- [ ] base restaurada, o lab 04 escreve chamado com `abrir_chamado`
- [ ] plano B de rede: os labs 01, 02 e 06-loop rodam sem Docker, só com a chave do modelo
- [ ] terminal com fonte grande e tema claro, o trace do `adk web` tem texto pequeno
