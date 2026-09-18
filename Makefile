.PHONY: setup infra down web lab1 lab2a lab2b lab3 lab4 lab5 lab6 lab7 maf maf-azure check

setup:
	pip install -r requirements.txt
	@test -f .env || cp .env.example .env
	@echo "Agora edite .env com sua GOOGLE_API_KEY"

infra:
	docker compose up -d
	@sleep 3
	@curl -s http://localhost:8000/health || echo "mock_api ainda subindo"
	@curl -sf http://localhost:5000/healthz >/dev/null && echo "toolbox ok" || echo "toolbox ainda subindo"

down:
	docker compose down

web:
	adk web

lab1:
	adk run lab01_agente_puro
lab2a:
	python lab02_memoria/a_estado_sessao/run_demo.py
lab2b:
	python lab02_memoria/b_memoria_longa/run_demo.py
lab3:
	adk run lab03_tool_externa
lab4:
	adk run lab04_mcp_toolbox
lab5:
	adk run lab05_sub_agentes
lab6:
	python lab06_orquestracao/run_demo.py
lab7:
	adk run lab07_a2a_interop

# O agente do outro time. Suba numa janela separada, antes do lab7.
maf:
	python lab07_a2a_interop/maf_retencao/servidor_stub.py
maf-azure:
	python lab07_a2a_interop/maf_retencao/servidor.py

check:
	python -c "import google.adk, sys; print('adk ok', google.adk.__version__ if hasattr(google.adk,'__version__') else '')"
