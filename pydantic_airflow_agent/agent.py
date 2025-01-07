import asyncio
import json
import logging
from dataclasses import dataclass
from devtools import pprint

import colorlog
import httpx
from httpx import AsyncClient
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.vertexai import VertexAIModel

log_format = '%(log_color)s%(asctime)s [%(levelname)s] %(reset)s%(purple)s[%(name)s] %(reset)s%(blue)s%(message)s'
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(log_format))
logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger(__name__)

@dataclass
class Deps:
    airflow_api_base_uri: str
    airflow_api_port: int
    airflow_api_user: str
    airflow_api_pass: str

class DAGStatus(BaseModel):
    dag_id: str = Field(description='ID of the DAG')
    dag_display_name: str = Field(description='Display name of the DAG')
    is_paused: bool = Field(description='Whether the DAG is paused')
    next_dag_run_data_interval_start: str = Field(description='Next DAG run data interval start')
    next_dag_run_data_interval_end: str = Field(description='Next DAG run data interval end')
    last_dag_run_id: str = Field(default='No DAG run', description='Last DAG run ID')
    last_dag_run_state: str = Field(default='No DAG run', description='Last DAG run state')
    total_dag_runs: int = Field(description='Total number of DAG runs')

model = VertexAIModel(
    model_name='gemini-2.0-flash-exp',
    service_account_file='gcp-credentials.json'
)

airflow_agent = Agent(
    model=model,
    system_prompt='You are an Airflow monitoring assistant',
    result_type=DAGStatus,
    deps_type=Deps,
    retries=2
)

@airflow_agent.tool
async def list_dags(ctx: RunContext[Deps]) -> str:
    """
    Get a list of all DAGs from the Airflow instance. Returns DAGs with their IDs and display names.
    """
    logger.info('Getting available DAGs...')
    uri = f'{ctx.deps.airflow_api_base_uri}:{ctx.deps.airflow_api_port}/api/v1/dags'
    auth = (ctx.deps.airflow_api_user, ctx.deps.airflow_api_pass)

    async with AsyncClient() as client:
        response = await client.get(uri, auth=auth)
        response.raise_for_status()

        dags_data = response.json()['dags']
        result = json.dumps([
            {'dag_id': dag['dag_id'], 'dag_display_name': dag['dag_display_name'], 'description': dag['description']}
            for dag in dags_data
        ])
        logger.debug(f'Available DAGs: {result}')
        return result

@airflow_agent.tool
async def get_dag_status(ctx: RunContext[Deps], dag_id: str) -> str:
    """
    Get detailed status information for a specific DAG by DAG ID.
    """
    logger.info(f'Getting status for DAG with ID: {dag_id}')
    base_url = f'{ctx.deps.airflow_api_base_uri}:{ctx.deps.airflow_api_port}/api/v1'
    auth = (ctx.deps.airflow_api_user, ctx.deps.airflow_api_pass)

    try:
        async with AsyncClient() as client:
            dag_response = await client.get(f'{base_url}/dags/{dag_id}', auth=auth)
            dag_response.raise_for_status()

            runs_response = await client.get(
                f'{base_url}/dags/{dag_id}/dagRuns',
                auth=auth,
                params={'order_by': '-execution_date', 'limit': 1}
            )
            runs_response.raise_for_status()

            result = {
                'dag_data': dag_response.json(),
                'runs_data': runs_response.json()
            }

            logger.debug(f'DAG status: {json.dumps(result)}')
            return json.dumps(result)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f'DAG with ID {dag_id} not found'
        raise

async def chat_loop(deps: Deps):
    while True:
        prompt = input('💬 > ')
        if prompt.lower() in ('q', ':q', 'quit', 'exit'):
            break
        else:
            result = await airflow_agent.run(prompt, deps=deps)
            usage = result.usage()
            print('🤖 AI Agent response:')
            pprint(result.data)
            print(f'LLM requests: {usage.requests}, total tokens used: {usage.total_tokens}')

async def main():
    deps = Deps(
        airflow_api_base_uri='http://localhost',
        airflow_api_port=8080,
        airflow_api_user='admin',
        airflow_api_pass='admin'
    )

    # Example: The payment report for yesterday is empty, are there any known issues?
    await chat_loop(deps)

if __name__ == "__main__":
    asyncio.run(main())
