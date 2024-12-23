.PHONY: all
all:
	@echo "Run make help to see available commands"

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make airflow-start  - Run Airflow Docker setup with Astro CLI"
	@echo "  make airflow-stop   - Stop Airflow"
	@echo "  make run-agent      - Run PydanticAI Airflow agent"

.PHONY: airflow-start
airflow-start: airflow-start
	astro dev start

.PHONY: airflow-stop
airflow-stop: airflow-stop
	astro dev stop

.PHONY: run-agent
run-agent:
	poetry run python pydantic_airflow_agent/agent.py
