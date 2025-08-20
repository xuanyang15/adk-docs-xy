# Enterprise Web Search Tool

The `enterprise_web_search` tool is a built-in tool for Gemini 2+ models that enables web grounding for enterprise compliance. This tool is designed to be used in enterprise environments where search results must meet specific compliance and data handling requirements.

## How it Works

The `enterprise_web_search` tool leverages Google's web grounding technology to provide search results that are suitable for enterprise use cases. When this tool is enabled, the agent's responses will be grounded in information from the web, with a focus on providing reliable and compliant results.

For more detailed information on how web grounding works in Vertex AI, please refer to the official [Google Cloud documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/web-grounding-enterprise).

## How to Use

To use the `enterprise_web_search` tool, simply import it from `google.adk.tools` and add it to the `tools` list of your `LlmAgent`.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import enterprise_web_search

# --- Example Agent using the enterprise_web_search tool ---

agent = LlmAgent(
    model="gemini-2.0-pro",
    name="enterprise_search_agent",
    instruction="You are a helpful assistant that can search the web for enterprise-compliant information.",
    tools=[enterprise_web_search],
)
```

When this agent is run, it will automatically use the `enterprise_web_search` tool to ground its responses in web search results.

## Limitations

*   **Model Compatibility:** The `enterprise_web_search` tool is only compatible with Gemini models. An error will be raised if you try to use it with a non-Gemini model.
*   **Gemini 1.x Limitation:** For Gemini 1.x models, the `enterprise_web_search` tool cannot be used in conjunction with other tools. If you need to use other tools, you must use a Gemini 2+ model.

By using the `enterprise_web_search` tool, you can build agents that provide reliable and compliant information for your enterprise users.
