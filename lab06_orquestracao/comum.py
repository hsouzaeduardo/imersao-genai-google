"""Infra compartilhada pelos três pipelines do lab 06."""

import os

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MODELO = os.getenv("ARI_MODEL", "gemini-2.5-flash")
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://localhost:5000")
API_REDE = os.getenv("AURORA_API_URL", "http://localhost:8000")

try:
    from google.adk.tools.toolbox_toolset import ToolboxToolset
except ImportError:  # pragma: no cover
    from toolbox_adk import ToolboxToolset


def toolset(nome: str):
    """Carrega uma fatia do cardápio do MCP Toolbox."""
    try:
        return ToolboxToolset(server_url=TOOLBOX_URL, toolset_name=nome)
    except TypeError:
        return ToolboxToolset(server_url=TOOLBOX_URL)


def consultar_status_rede(cep: str) -> dict:
    """Consulta a situação da rede da Aurora para um CEP.

    Args:
        cep: CEP do endereço de instalação, com ou sem hífen.

    Returns:
        dict com status da chamada e a situação da rede.
    """
    try:
        r = httpx.get(f"{API_REDE}/status-rede/{cep}", timeout=8.0)
        r.raise_for_status()
        return {"status": "ok", "dados": r.json()}
    except Exception as e:  # noqa: BLE001
        return {"status": "indisponivel", "mensagem": f"Painel indisponível: {e}"}


def listar_eventos_massivos() -> dict:
    """Lista os incidentes de rede ativos na base da Aurora.

    Returns:
        dict com status da chamada e a lista de eventos em andamento.
    """
    try:
        r = httpx.get(f"{API_REDE}/eventos-massivos", timeout=8.0)
        r.raise_for_status()
        return {"status": "ok", "dados": r.json()}
    except Exception as e:  # noqa: BLE001
        return {"status": "indisponivel", "mensagem": f"Painel indisponível: {e}"}
