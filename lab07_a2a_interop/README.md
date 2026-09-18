# Lab 07: o agente que não é seu

## A dor

No lab 05 o ARI virou coordenador e ganhou três especialistas. Delegar custou um `import`:
todos eram ADK, no mesmo processo, no mesmo deploy, do mesmo time.

Agora o cliente diz que quer cancelar.

Quem decide desconto na Aurora é o time de CX, e o agente deles roda em **Microsoft Agent
Framework** sobre Azure. Você não vai reescrever o agente deles em ADK. Eles não vão migrar
para o seu. E nenhum dos dois lados vai entregar a política comercial para o outro.

`sub_agents` só atravessa o seu próprio framework. É aqui que ele acaba.

## O remédio

O **A2A**, Agent2Agent, é o protocolo que faz dois agentes de frameworks diferentes
conversarem. Cada lado publica um **agent card**, um JSON em
`/.well-known/agent-card.json` que diz quem ele é e o que sabe fazer, e atende JSON-RPC.

Do lado ADK isso cabe em um objeto:

```python
agente_retencao = RemoteA2aAgent(
    name="agente_retencao",
    description="Acione quando o cliente disser que quer cancelar...",
    agent_card=f"{MAF_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = LlmAgent(..., sub_agents=[agente_retencao])
```

Por fora, é um sub-agente como os do lab 05: entra em `sub_agents`, é escolhido pela
`description`, recebe o turno. Por dentro, é HTTP contra um processo que não é seu.

## Os arquivos

| Arquivo | Lado | O que é |
|---|---|---|
| `agent.py` | ADK | o ARI com o `RemoteA2aAgent`. É o lab. |
| `maf_retencao/card.py` | nenhum | o agent card e a política. Só tipos do `a2a-sdk`. |
| `maf_retencao/servidor.py` | MAF | o agente real, com Azure via Foundry |
| `maf_retencao/servidor_stub.py` | nenhum | o mesmo card e protocolo, sem LLM |

Repare no que **não** existe: nenhum arquivo importa os dois frameworks. O `agent.py` não
conhece MAF. Os servidores não conhecem ADK, e por isso nem importam o pacote deste lab,
que traria o `agent.py` junto. O único contrato entre os dois lados é o card publicado por HTTP.

## Rodar

Você precisa de duas janelas.

**Janela 1, o agente do outro time:**

```bash
python lab07_a2a_interop/maf_retencao/servidor_stub.py
```

**Janela 2, o ARI:**

```bash
adk run lab07_a2a_interop
```

Confira o card antes de começar:

```bash
curl http://localhost:9999/.well-known/agent-card.json
```

### Com Azure de verdade

O stub existe para você ver o protocolo sem credencial nenhuma. Com Azure, troque a janela 1
por `servidor.py` e **não mude nada na janela 2**: o lado ADK não distingue um do outro.

No `.env`:

```
FOUNDRY_PROJECT_ENDPOINT=https://<seu-projeto>.services.ai.azure.com/api/projects/<nome>
FOUNDRY_MODEL=gpt-4o-mini
```

E `az login`, porque o cliente usa `DefaultAzureCredential`.

> Em MAF 1.x o caminho para Azure OpenAI é o **Microsoft Foundry**, via `FoundryChatClient`
> do pacote `agent-framework-foundry`. Não existe `AzureOpenAIChatClient` no pacote, embora
> muito exemplo na internet ainda cite essa classe.

## Os experimentos

**1. Derrube o outro time.** Com a conversa em andamento, mate a janela 1 e peça o
cancelamento de novo. O ADK falha ao resolver o agent card:

```
Failed to resolve remote A2A agent agente_retencao: ... All connection attempts failed
```

Compare com o lab 05, onde o especialista nunca some porque mora no seu processo.
Um sub-agente remoto é rede, e rede cai. É por isso que a `instruction` do ARI manda
dizer isso ao cliente com todas as letras em vez de improvisar uma oferta.

**2. Troque o motor sem tocar no cliente.** Rode o `servidor_stub.py`, converse, mate,
suba o `servidor.py` e converse de novo. O `agent.py` não muda. Essa é a promessa do
protocolo, e vale a pena ver acontecendo.

**3. Mexa na `description` do `RemoteA2aAgent`.** Troque por algo vago como
`"agente de retenção"` e veja o ARI deixar de rotear, ou rotear na hora errada.
É a mesma lição do lab 05: quem decide o roteamento é a `description`, não a `instruction`
do agente remoto, que o ADK nem enxerga.

**4. Leia o card.** Abra o JSON e repare que `skills`, `description` e `capabilities` são
tudo que o ADK sabe sobre o outro agente. Ele nunca viu a `POLITICA_RETENCAO`, que fica no
servidor. Esse é o ponto: o protocolo carrega capacidade, não implementação.

## O que fica

O A2A resolve organização, não tecnologia. Quando o outro agente é de outro time, com outro
ciclo de deploy e outra política que você não pode ver, o custo de integrar por protocolo é
menor do que o de unificar a stack. Em compensação, você troca uma chamada de função por uma
chamada de rede, e passa a ter que tratar indisponibilidade.
