
import dotenv
import pytest
import vertexai, os
from google.adk.evaluation.agent_evaluator import AgentEvaluator

import os, sys
sys.path.insert(0, os.path.abspath(os.getcwd()))  # Adjust the path to your module

pytest_plugins = ("pytest_asyncio",)

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
    Test the agent's basic ability on 10 examples on criteria:

    a) response_match_score      (0.2 threshold)
    b) response_evaluation_score (2   threshold)

    The evaluation procedure will run each example 2 times, 
    and uses: 

    - for a) **ROUGE-1 metric** (unigram overlap) to compare the agent's responses with the expected responses
      ( cf: https://en.wikipedia.org/wiki/ROUGE_(metric) )
    - for b) **pointwise coherence metric** to evaluate the logical cohesion of the agent's responses
      ( cf: https://cloud.google.com/vertex-ai/generative-ai/docs/models/metrics-templates#pointwise_coherence )

    The goal of this test is to ensure the agent answers are on topic, even if they are not perfect.
    
    We use as test dataset: evalset.test.json
    We use as configuration file: test_config.json
    """
    print("Running evaluation for query_companion...")
    await AgentEvaluator.evaluate(
        agent_module="query_companion",
        agent_name="query_companion",
        eval_dataset_file_path_or_dir="tests/evalset.test.json"
    )