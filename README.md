# ARI, o estagiário da Aurora Fibra

Um roteiro de aprendizado de agentes com **Google ADK**, em seis labs, onde cada etapa só existe porque a anterior falhou de um jeito específico.

A empresa é a **Aurora Fibra**, provedor regional de internet com 400 mil assinantes.
O agente é o **ARI**, Assistente de Rede Inteligente, contratado como estagiário do suporte N1.

A regra pedagógica do curso inteiro é uma só: **a dor vem antes do remédio**.
Você roda o lab anterior, vê o agente quebrar na sua frente, e só então aprende o recurso que resolve.

---

## Mapa dos labs

| Lab | Capítulo | Conceito | Construto ADK | Dor que resolve |
|---|---|---|---|---|
| 1 | Primeiro dia, sem crachá | Agente puro | `LlmAgent`, `Runner`, `adk web` | nenhuma, é o baseline |
| 2a | O caderno de anotações | Estado de sessão | `SessionService`, `state`, `output_key` | esquece dentro do atendimento |
| 2b | O prontuário do cliente | Memória de longo prazo | `MemoryService`, `load_memory` | esquece entre atendimentos |
| 3 | O primeiro acesso ao sistema | Tool externa | `FunctionTool` | inventa dados que não tem |
| 4 | A chave do banco de dados | MCP Toolbox | `ToolboxToolset`, `tools.yaml` | acesso a dados sem governança |
| 5 | Promovido a líder de equipe | Sub agentes | `sub_agents`, `AgentTool` | um prompt gigante fazendo tudo |
| 6 | O processo operacional | Orquestração | `SequentialAgent`, `ParallelAgent`, `LoopAgent` | delegação probabilística onde o negócio exige previsibilidade |

Cada lab tem seu próprio `README.md` com roteiro, gotchas e critério de aprovação.
O arquivo [`DIFFS.md`](DIFFS.md) mostra, em uma tela, o que mudou de um lab para o outro.
O arquivo [`docs/ROTEIRO_AULA.md`](docs/ROTEIRO_AULA.md) traz os tempos, as falas e as demos.

---

## Setup

### 1. Dependências Python

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Credenciais

```bash
cp .env.example .env
# edite .env e coloque sua GOOGLE_API_KEY do AI Studio
```

Cada pasta de agente também carrega o `.env` da raiz, então uma chave só serve para os seis labs.

### 3. Infra dos labs 3 e 4

```bash
docker compose up -d
```

Isso sobe:

- `mock_api` na porta 8000, a API de status de rede da Aurora, usada no lab 3
- `postgres` na porta 5432, já populado com `data/seed_aurora.sql`, usado no lab 4
- `toolbox` na porta 5000, o MCP Toolbox for Databases lendo `lab04_mcp_toolbox/tools.yaml`

Confira:

```bash
curl http://localhost:8000/health
curl http://localhost:5000/api/toolset
```

### 4. Rodar um lab

```bash
adk web            # na raiz do repositório, escolha o agente no seletor
```

ou, para os labs que precisam de um runner explícito:

```bash
python lab02_memoria/b_memoria_longa/run_demo.py
```

---

## Capítulo 1: primeiro dia, sem crachá

ARI chega na Aurora Fibra. Sabe português, sabe ser educado, não tem acesso a nada.
Recebe um manual de atendimento, que no ADK se chama `instruction`, e é colocado no chat.

O que você vai provar nesse lab: **a instruction é código, não decoração**.
Trocar "seja útil" por um protocolo de atendimento em seis linhas muda o comportamento inteiro,
e o trace do `adk web` mostra a anatomia de um turno.

E no fim, a falha planejada: pergunte o status da sua conexão.
ARI responde com confiança absoluta, e é ficção.

## Capítulo 2: o caderno de anotações

Duas coisas que todo mundo confunde, separadas de propósito em dois labs.

O **estado de sessão** é o caderno que ARI usa durante o atendimento.
Ele anota o CPF que o cliente informou no turno 2 e ainda tem isso no turno 9.
Troque o serviço de sessão em memória por um em banco e o caderno sobrevive ao restart do processo.

A **memória de longo prazo** é o prontuário.
É o que ARI lembra do cliente três semanas depois, em outra sessão, em outro dispositivo.
Escopo de usuário, não de conversa.

Falha planejada: ARI agora lembra do cliente, e continua inventando o status da conexão.

## Capítulo 3: o primeiro acesso ao sistema

ARI ganha login no painel de status da rede. Uma tela só, somente leitura.
Depois ganha o segundo acesso, esse com efeito colateral: reiniciar o roteador do cliente.

A diferença entre ler e agir aparece aqui, e com ela o primeiro guardrail,
um `before_tool_callback` que barra ação destrutiva sem confirmação.

Falha planejada: o negócio pede fatura, contrato e histórico de chamados.
Escrever uma function tool com SQL embutido para cada uma significa conexão, pool,
injeção de SQL, credencial dentro do código do agente e redeploy a cada mudança de query.

## Capítulo 4: a chave do banco de dados

O time de Dados da Aurora não entrega a senha do Postgres para um estagiário.
Entrega um balcão de atendimento com um cardápio fixo de consultas aprovadas.

Esse balcão é o MCP Toolbox for Databases.
Você declara as tools em YAML, cada uma mapeada para uma query parametrizada,
e o Toolbox cuida de pool de conexão, autenticação e observabilidade.
O agente carrega o toolset em duas linhas.

A demo que vende o conceito sozinha: mude a query no `tools.yaml`,
reinicie apenas o Toolbox, e o comportamento do agente muda sem tocar em uma linha de Python.

Falha planejada: a instruction virou um monstro de 200 linhas cobrindo
cobrança, suporte técnico e agendamento, e ARI mistura os fluxos.

## Capítulo 5: promovido a líder de equipe

A Aurora contrata mais três estagiários. ARI vira coordenador e para de atender.
Cada especialista fica com a fatia de tools que lhe cabe,
e o Agente de Cobrança nunca enxerga a tool que reinicia roteador.

Aqui entra a distinção que separa quem leu a doc de quem entendeu:
sub agente **transfere** o controle, `AgentTool` **chama e devolve**.

Falha planejada: o compliance da Aurora exige que todo chamado passe por
triagem, depois diagnóstico, depois registro, sempre nessa ordem.
Delegação decidida por LLM não garante isso.

## Capítulo 6: o processo operacional

O jurídico e a operação escrevem um POP.
Certas etapas não são negociáveis com o bom senso do modelo.

`SequentialAgent` para a ordem obrigatória.
`ParallelAgent` para as três verificações que não dependem uma da outra, com ganho de latência medido no relógio.
`LoopAgent` para o revisor que refina a resposta ao cliente até ela passar nos critérios.

ARI deixa de ser um chatbot esperto e vira um processo operacional auditável.
Esse é o arco inteiro do curso em uma frase.

---

## Critério de aprovação

Cada lab termina com uma pergunta que o agente da etapa anterior erra e o da etapa atual acerta.
Isso dá ao aluno prova objetiva de progresso, e ao instrutor seis momentos naturais de aplauso.

| Lab | Pergunta de verificação | Agente anterior | Agente do lab |
|---|---|---|---|
| 1 | "Quem é você e o que você consegue fazer?" | n/a | responde dentro do escopo, sem prometer o que não tem |
| 2a | "Qual CPF eu te passei lá no começo?" | esquece | recupera do `state` |
| 2b | "Lembra da minha preferência de horário?" (nova sessão) | esquece | recupera da memória |
| 3 | "Minha internet está lenta no CEP 06010-100" | inventa | consulta a API e responde com dado real |
| 4 | "Tenho fatura em aberto?" | inventa ou pede para ligar | consulta o Postgres via Toolbox |
| 5 | "Minha fatura venceu e o roteador está piscando vermelho" | mistura os dois fluxos | roteia para cobrança e depois para técnico |
| 6 | mesmo caso do lab 5, dez vezes seguidas | ordem varia | ordem idêntica nas dez execuções |

---

## Aviso sobre dados

Todos os CPFs, nomes, endereços e contratos em `data/seed_aurora.sql` são fictícios,
gerados para aula. Nenhum dado real de cliente entra neste repositório.
