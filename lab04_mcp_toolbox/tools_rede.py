"""
A tool de rede do lab 03, trazida para cá.

Duplicar é proposital: cada lab roda sozinho, sem import entre pastas irmãs,
porque o ADK trata cada pasta de agente como um pacote independente.
Em projeto real isso vira um pacote compartilhado.
"""

import os

import httpx

API = os.getenv("AURORA_API_URL", "http://localhost:8000")


def consultar_status_rede(cep: str) -> dict:
    """Consulta o painel de rede da Aurora e retorna a situação de um CEP.

    Use sempre que o cliente relatar lentidão, oscilação ou falta de conexão.

    Args:
        cep: CEP do endereço de instalação, com ou sem hífen. Ex: "06010-100".

    Returns:
        dict com status da chamada e a situação da rede naquele CEP.
    """
    try:
        resposta = httpx.get(f"{API}/status-rede/{cep}", timeout=8.0)
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
