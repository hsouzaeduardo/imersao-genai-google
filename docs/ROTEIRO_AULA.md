# Roteiro de condução

Formato de referência: dois encontros de 4 horas, mais um encontro 3 opcional
para o lab 07. Versão compacta de 8 horas em um dia no fim do documento.

Cada lab tem o seu próprio roteiro detalhado no README da pasta. Este documento
é o de condução: tempo, ordem, o que não pode falhar e o que dizer.

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

## Encontro 3, opcional: quando o agente não é seu

Vale como módulo avulso de 2 horas. Só depende dos labs 01 e 05.

| Bloco | Tempo | Conteúdo | Momento chave |
|---|---|---|---|
| Retomada | 10 min | por que `sub_agents` não resolve tudo | "e se o especialista for de outro time?" |
| Lab 07 | 70 min | A2A, agent card, `RemoteA2aAgent` | trocar o servidor stub pelo real sem tocar no cliente |
| Discussão | 30 min | protocolo versus biblioteca, quando integrar e quando unificar | "o A2A resolve organização, não tecnologia" |

O lab 07 roda sem Azure: o `servidor_stub.py` publica o mesmo card e fala o mesmo
protocolo, sem LLM nenhum. Use ele na aula e deixe o `servidor.py` para quem tiver
credencial. Aliás, rodar o stub primeiro é melhor didática: a resposta é
determinística, então quando algo falha a turma sabe que foi integração, não modelo.

---

## As sete demos que não podem falhar

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
7. **Lab 07**: matar o servidor do outro time no meio da conversa.
   Prova que sub-agente remoto é rede, e que rede cai.

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

**Na abertura do lab 07, antes de mostrar o RemoteA2aAgent:**
até aqui, delegar custou um import. Isso porque todo mundo era ADK, no seu processo,
no seu deploy. Agora o especialista tem outro dono, outro ciclo de release e uma
política que ele não pode te mostrar. Nenhum import resolve problema de organograma.

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

**"A2A substitui o MCP?"**
Não, resolvem coisas diferentes. MCP é o agente falando com ferramenta, que é o lab 04.
A2A é agente falando com agente, que é o lab 07. No mesmo sistema você usa os dois:
o agente de retenção do lab 07 provavelmente tem o próprio MCP do lado dele.

**"Por que não expor o outro agente como uma tool e pronto?"**
Dá para fazer, e às vezes é o certo. A diferença é que tool é uma chamada que volta,
enquanto o A2A carrega conversa: contexto, tarefa longa, status. Se o outro lado
precisa fazer perguntas de volta ao cliente, tool aperta.

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

- [ ] `docker compose up -d` rodando e `curl localhost:5000/healthz` respondendo
- [ ] `.env` com chave válida e cota conferida, aula com 30 alunos consome
- [ ] `aurora_sessoes.db` apagado, para o lab 02a começar limpo
- [ ] base restaurada, o lab 04 escreve chamado com `abrir_chamado`
- [ ] plano B de rede: os labs 01, 02 e 06-loop rodam sem Docker, só com a chave do modelo
- [ ] terminal com fonte grande e tema claro, o trace do `adk web` tem texto pequeno
- [ ] se for dar o lab 07: `python lab07_a2a_interop/maf_retencao/servidor_stub.py`
      numa janela separada e `curl localhost:9999/.well-known/agent-card.json` devolvendo 200
