
import dotenv
import pytest
import warnings
import vertexai, os
from google.adk.evaluation.agent_evaluator import AgentEvaluator

import os, sys
sys.path.insert(0, os.path.abspath(os.getcwd()))  # Adjust the path to your module

pytest_plugins = ("pytest_asyncio",)

warnings.filterwarnings("ignore",
                        category=DeprecationWarning,
                        module="google.cloud")

@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    dotenv.load_dotenv(env_file, override=True)
    if not os.environ.get('GOOGLE_CLOUD_PROJECT'):
        raise EnvironmentError("Environment variable 'GOOGLE_CLOUD_PROJECT' is not set.")
    if not os.environ.get('GOOGLE_CLOUD_LOCATION'):
        raise EnvironmentError("Environment variable 'GOOGLE_CLOUD_LOCATION' is not set.")
    print("Environment variables loaded from .env file.")
    vertexai.init(project=os.environ['GOOGLE_CLOUD_PROJECT'], 
                  location=os.environ['GOOGLE_CLOUD_LOCATION'], 
                  api_transport='rest')
    print("Vertex AI initialized with project and location.")

@pytest.mark.asyncio
async def test_all():
    """
    Test the agent's basic ability on criteria defined in:  test_config.json
    We use as test dataset:                                 evalset.test.json
    """
    print("Running evaluation for query_companion...")
    await AgentEvaluator.evaluate(
        num_runs=1,
        agent_module="query_companion",
        agent_name="query_companion",
        eval_dataset_file_path_or_dir=os.path.join(os.path.dirname(__file__), 
                                                   "evalset.test.json")
    )