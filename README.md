# Conversational agent

This repo contains the code for the IBAIC chatbot, built using Google's [Agent Development Kit](https://google.github.io/adk-docs/) (ADK), and relies on the following GCP project variables:

* **PROJECT_ID** = ``
* **GEMINI_REGION** = ``

This project was written with Python 3.13.x, and assumes familiarity with `venv`:
```bash
python -m venv .venv --prompt agents
source .venv/bin/activate
pip install -r requirements
```

## GCP authentication

Running this agent on a localhost requires prior authentication to GCP. On the command line, type:

```bash
gcloud auth login <your_name>@<domain> # get a session token
gcloud auth application-default login # authorize client libraries
```

and follow the login instructions. GCP session tokens last for a day (circa 24H). The nice thing is that it authorizes your localhost, provided you add the following global variable to your `.bashrc` file and/or Bash session

```bash
export GOOGLE_APPLICATION_CREDENTIALS=<path/to/.config_dir>/.config/gcloud/application_default_credentials.json
```

## Running the agent in debug mode

```bash
cd query_companion
echo -e "GOOGLE_GENAI_USE_VERTEXAI=TRUE\nGOOGLE_CLOUD_PROJECT=<PROJECT_ID>\nGOOGLE_CLOUD_LOCATION=<GEMINI_REGION>" >> .env
adk web
```

## Importing tools from MCP servers

By default, the agent connects to the Knowledge Graph MCP server at `https://knowledge-graph-mcp-1098449730426.us-central1.run.app/mcp` and exposes only `query_dbpedia` and `query_dblp_topic`. This server uses streamable HTTP and currently accepts unauthenticated connections. Set `MCP_SERVER_URL` in the agent's `.env` to override the endpoint.

To configure other MCP servers, set `MCP_SERVERS` in the agent's `.env` as a JSON array. Each entry creates an MCP toolset; `transport` can be `stdio` (the default), `sse`, or `streamable_http`. For example:

```bash
MCP_SERVERS='[{"transport":"streamable_http","url":"http://localhost:8000/mcp"}]'
```

For a local stdio server, provide its executable and arguments instead:

```bash
MCP_SERVERS='[{"transport":"stdio","command":"uvx","args":["your-mcp-server"]}]'
```

Entries may also include `headers` for HTTP/SSE authentication and `tool_filter` to expose only selected tool names. The local server executable must be installed and available to the process running `adk web`.

## Run unit tests

Unit tests ensure agent's basic abilities, in particular enforce that answers are on topic, even if not perfect. We test on 10 examples and 2 criteria:

* `response_match_score`. This criterion measures  **[ROUGE-1](https://en.wikipedia.org/wiki/ROUGE_(metric))** (unigram overlap) between the agent's responses and reference expected responses.
    The test succeeds if ROUGE-1 is equal or greater than 0.2.
* `response_evaluation_score`. This criterion measures Google's **[pointwise coherence metric](https://cloud.google.com/vertex-ai/generative-ai/docs/models/metrics-templates#pointwise_coherence)**, an LLM-based ordinal score ranging from 0 to 5, that assesses the logical cohesion of an agent responses. We define success as scoring at least 2.

We follow ADK's testing practices for `pytest`, using as test set dataset `evalset.test.json`, and as configuration file: `test_config.json`. The tests are located under ``tests`. In order for them to work, you'll need to create another `.env`:
```bash
cd tests
echo -e "GOOGLE_GENAI_USE_VERTEXAI=TRUE\nGOOGLE_CLOUD_PROJECT=<PROJECT_ID>\nGOOGLE_CLOUD_LOCATION=<GEMINI_REGION>" >> .env
```
Once this done, you can run the tests by typing from within the root directory of the project:
```bash
cd ..
pytest -v tests
```
