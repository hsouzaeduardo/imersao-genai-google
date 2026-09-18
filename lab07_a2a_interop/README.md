# Lab 07: o agente que não é seu

**Tempo sugerido:** 70 minutos
**Pré-requisitos:** labs 01 e 05 feitos, `pip install -r requirements.txt`.
Azure é opcional: o `servidor_stub.py` roda o lab inteiro sem credencial.

## A cena

O cliente liga dizendo que vai cancelar. ARI já sabe rotear, já sabe consultar
o banco, e mesmo assim não pode responder: quem decide desconto na Aurora é o
time de CX, que não é da sua área, não usa o seu framework e não vai te
entregar a tabela de descontos.

## A dor

No lab 05 o ARI virou coordenador e ganhou três especialistas. Delegar custou um `import`:
todos eram ADK, no mesmo processo, no mesmo deploy, do mesmo time.

O agente de retenção não é nada disso. Ele roda em **Microsoft Agent Framework** sobre
Azure. Você não vai reescrever o agente deles em ADK, eles não vão migrar para o seu, e
nenhum dos dois lados vai entregar a própria política para o outro.

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

## Gotchas

- **`RemoteA2aAgent` resolve o card no primeiro uso, não na importação.**
  Um card inacessível não quebra `adk run`; quebra no turno em que o roteamento
  escolhe o agente remoto. Isso confunde: o lab parece ter subido bem.
- **Quem roteia é a `description` do lado ADK, não o card.** O ADK lê o card para
  saber onde falar, mas a decisão de transferir sai da `description` que você
  escreveu no `RemoteA2aAgent`. Card bom com `description` vaga não roteia.
- **Versão do `a2a-sdk` importa mais do que parece.** A linha 1.x gera os tipos a
  partir de protobuf: campos em snake_case, e helpers antigos como
  `new_agent_text_message` não existem mais. Exemplo escrito para a 0.3 não roda.
- **Em MAF 1.x não existe `AzureOpenAIChatClient`.** O caminho para Azure OpenAI é
  o `FoundryChatClient`, do pacote `agent-framework-foundry`. Muito tutorial ainda
  cita a classe que não existe.
- **O agente remoto não vê o seu `state`.** Tudo que ele sabe é o que você mandou
  na mensagem. Por isso a `instruction` do ARI manda reunir os três dados antes de
  transferir: sem isso o outro lado responde pedindo o que falta, e você gasta
  dois turnos de rede.

## Critério de aprovação

Com o servidor do outro time no ar, o ARI reúne tempo de casa, situação
financeira e motivo antes de transferir, e a oferta que aparece ao cliente é a
que veio pelo A2A, não uma inventada por ele. Com o servidor derrubado, ele diz
que o time de retenção está indisponível em vez de improvisar um desconto.

## O que fica

O A2A resolve organização, não tecnologia. Quando o outro agente é de outro time, com outro
ciclo de deploy e outra política que você não pode ver, o custo de integrar por protocolo é
menor do que o de unificar a stack. Em compensação, você troca uma chamada de função por uma
chamada de rede, e passa a ter que tratar indisponibilidade.
