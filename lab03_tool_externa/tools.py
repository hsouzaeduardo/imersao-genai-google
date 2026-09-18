"""
Tools do lab 03: o primeiro acesso do ARI a um sistema da Aurora.

Regras que valem para toda function tool do ADK:
  - a docstring e os type hints são o contrato que o modelo lê
  - o retorno é sempre um dict, com uma chave "status" legível
  - erro tratado é dado, exceção estourada é trace quebrado
"""

import os

import httpx

API = os.getenv("AURORA_API_URL", "http://localhost:8000")
TIMEOUT = 8.0


def consultar_status_rede(cep: str) -> dict:
    """Consulta o painel de rede da Aurora e retorna a situação de um CEP.

    Use sempre que o cliente relatar lentidão, oscilação ou falta de conexão,
    antes de qualquer diagnóstico. Não use para assuntos de cobrança.

    Args:
        cep: CEP do endereço de instalação, com ou sem hífen. Ex: "06010-100".

    Returns:
        dict com status da chamada e, em caso de sucesso, a situação da rede,
        a severidade, a descrição do incidente e a previsão de normalização.
    """
    try:
        resposta = httpx.get(f"{API}/status-rede/{cep}", timeout=TIMEOUT)
        if resposta.status_code == 400:
            return {"status": "erro", "mensagem": "CEP inválido. Peça o CEP com 8 dígitos."}
        resposta.raise_for_status()
        return {"status": "ok", "dados": resposta.json()}
    except httpx.ConnectError:
        return {
            "status": "indisponivel",
            "mensagem": "Painel de rede fora do ar. Informe o cliente e não invente diagnóstico.",
        }
    except httpx.HTTPError as e:
        return {"status": "erro", "mensagem": f"Falha ao consultar o painel: {e}"}


def reiniciar_roteador(id_cliente: str) -> dict:
    """Envia um comando de reinício remoto para o roteador do cliente.

    AÇÃO COM EFEITO COLATERAL: derruba a conexão do cliente por cerca de 3 minutos.
    Só chame depois de o cliente confirmar explicitamente que autoriza o reinício.

    Args:
        id_cliente: CPF sem pontuação ou identificador do contrato.

    Returns:
        dict com status da chamada e a previsão de retorno da conexão.
    """
    try:
        resposta = httpx.post(
            f"{API}/roteador/reiniciar",
            json={"id_cliente": id_cliente},
            timeout=TIMEOUT,
        )
        resposta.raise_for_status()
        return {"status": "ok", "dados": resposta.json()}
    except httpx.ConnectError:
        return {"status": "indisponivel", "mensagem": "Não foi possível falar com o painel de rede."}
    except httpx.HTTPError as e:
        return {"status": "erro", "mensagem": f"Falha ao reiniciar: {e}"}
