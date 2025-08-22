# Memory: Long-Term Knowledge with `MemoryService`

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

We've seen how `Session` tracks the history (`events`) and temporary data (`state`) for a *single, ongoing conversation*. But what if an agent needs to recall information from *past* conversations or access external knowledge bases? This is where the concept of **Long-Term Knowledge** and the **`MemoryService`** come into play.

Think of it this way:

* **`Session` / `State`:** Like your short-term memory during one specific chat.
* **Long-Term Knowledge (`MemoryService`)**: Like a searchable archive or knowledge library the agent can consult, potentially containing information from many past chats or other sources.

## The `MemoryService` Role

The `BaseMemoryService` defines the interface for managing this searchable, long-term knowledge store. Its primary responsibilities are:

1. **Ingesting Information (`add_session_to_memory`):** Taking the contents of a (usually completed) `Session` and adding relevant information to the long-term knowledge store.
2. **Searching Information (`search_memory`):** Allowing an agent (typically via a `Tool`) to query the knowledge store and retrieve relevant snippets or context based on a search query.

## Choosing the Right Memory Service

The ADK offers three distinct `MemoryService` implementations, each tailored to different use cases. Use the table below to decide which is the best fit for your agent.

| **Feature** | **InMemoryMemoryService** | **VertexAiMemoryBankService** | **VertexAiRagMemoryService** |
| :--- | :--- | :--- | :--- |
| **Persistence** | None (data is lost on restart) | Yes (Managed by Vertex AI) | Yes (Managed by Vertex AI) |
| **Primary Use Case** | Prototyping, local development, and simple testing. | Building meaningful, evolving memories from user conversations. | Retrieving information from a knowledge base using RAG. |
| **Memory Extraction** | Stores full conversation | Extracts [meaningful information](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) from conversations and consolidates it with existing memories (powered by LLM) | Stores and indexes raw text for retrieval. |
| **Search Capability** | Basic keyword matching. | Advanced semantic search. | Advanced semantic search using RAG. |
| **Setup Complexity** | None. It's the default. | Low. Requires an [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) in Vertex AI. | Low. Requires a [RAG Corpus](https://cloud.google.com/vertex-ai/generative-ai/docs/rag) in Vertex AI. |
| **Dependencies** | None. | Google Cloud Project, Vertex AI API | Google Cloud Project, Vertex AI API |
| **When to use it** | When you want to search across multiple sessions’ chat histories for prototyping. | When you want your agent to remember and learn from past interactions. | When you want your agent to have access to a large knowledge base. |

## In-Memory Memory

The `InMemoryMemoryService` stores session information in the application's memory and performs basic keyword matching for searches. It requires no setup and is best for prototyping and simple testing scenarios where persistence isn't required.

```py
from google.adk.memory import InMemoryMemoryService
memory_service = InMemoryMemoryService()
```

**Example: Adding and Searching Memory**

This example demonstrates the basic flow using the `InMemoryMemoryService` for simplicity.

??? "Full Code"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # Import MemoryService
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # Tool to query memory
    from google.genai.types import Content, Part

    # --- Constants ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-2.0-flash" # Use a valid model

    # --- Agent Definitions ---
    # Agent 1: Simple agent to capture information
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="Acknowledge the user'''s statement.",
    )

    # Agent 2: Agent that can use memory
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="Answer the user'''s question. Use the '''load_memory''' tool "
                    "if the answer might be in past conversations.",
        tools=[load_memory] # Give the agent the tool
    )

    # --- Services ---
    # Services must be shared across runners to share state and memory
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # Use in-memory for demo

    async def run_scenario():
        # --- Scenario ---

        # Turn 1: Capture some information in a session
        print("--- Turn 1: Capturing Information ---")
        runner1 = Runner(
            # Start with the info capture agent
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # Provide the memory service to the Runner
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")

        # Run the agent
        final_response_text = "(No final response)"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"Agent 1 Response: {final_response_text}")

        # Get the completed session
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # Add this session's content to the Memory Service
        print("\n--- Adding Session 1 to Memory ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("Session added to memory.")

        # Turn 2: Recall the information in a new session
        print("\n--- Turn 2: Recalling Information ---")
        runner2 = Runner(
            # Use the second agent, which has the memory tool
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # Reuse the same service
            memory_service=memory_service   # Reuse the same service
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="What is my favorite project?")], role="user")

        # Run the second agent
        final_response_text_2 = "(No final response)"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"Agent 2 Response: {final_response_text_2}")

    # To run this example, you can use the following snippet:
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

## Vertex AI Memory Bank

The `VertexAiMemoryBankService` connects your agent to [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview), a fully managed Google Cloud service that provides sophisticated, persistent memory capabilities for conversational agents.

### How It Works

The service automatically handles two key operations:

*   **Generating Memories:** At the end of a conversation, the ADK sends the session's events to the Memory Bank, which intelligently processes and stores the information as "memories."
*   **Retrieving Memories:** Your agent code can issue a search query against the Memory Bank to retrieve relevant memories from past conversations.

### Prerequisites

Before you can use this feature, you must have:

1.  **A Google Cloud Project:** With the Vertex AI API enabled.
2.  **An Agent Engine:** You need to create an Agent Engine in Vertex AI. This will provide you with the **Agent Engine ID** required for configuration.
3.  **Authentication:** Ensure your local environment is authenticated to access Google Cloud services. The simplest way is to run:
    ```bash
    gcloud auth application-default login
    ```
4.  **Environment Variables:** The service requires your Google Cloud Project ID and Location. Set them as environment variables:
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

### Configuration

To connect your agent to the Memory Bank, you use the `--memory_service_uri` flag when starting the ADK server (`adk web` or `adk api_server`). The URI must be in the format `agentengine://<agent_engine_id>`.

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

Or, you can configure your agent to use the Memory Bank by manually instantiating the `VertexAiMemoryBankService` and passing it to the `Runner`.

```py
from google.adk.memory import VertexAiMemoryBankService

# The project, location, and agent_engine_id are optional.
# If not provided, they will be read from the environment variables
# GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION, and the
# agent_engine_id will be parsed from the --memory_service_uri flag.
memory_service = VertexAiMemoryBankService()

runner = adk.Runner(
    ...
    memory_service=memory_service
)
```

## Vertex AI RAG Memory Service

The `VertexAiRagMemoryService` uses [Vertex AI RAG](https://cloud.google.com/vertex-ai/generative-ai/docs/rag) to provide a powerful retrieval-augmented generation memory service.

### How It Works

This service allows you to connect your agent to a RAG corpus, which can contain a large amount of information. When your agent needs to answer a question, it can search the RAG corpus for relevant information and use it to generate a more informed response.

### Prerequisites

1.  **A Google Cloud Project:** With the Vertex AI API enabled.
2.  **A RAG Corpus:** You need to create a RAG corpus in Vertex AI. This will provide you with the **RAG Corpus ID** required for configuration.
3.  **Authentication:** Ensure your local environment is authenticated to access Google Cloud services.
    ```bash
    gcloud auth application-default login
    ```
4.  **Environment Variables:**
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

### Configuration

To connect your agent to a RAG corpus, use the `--memory_service_uri` flag with the `rag://` scheme:

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="rag://your-rag-corpus-id"
```

You can also manually instantiate the `VertexAiRagMemoryService`:

```py
from google.adk.memory import VertexAiRagMemoryService

memory_service = VertexAiRagMemoryService(
    rag_corpus="your-rag-corpus-id"
)

runner = adk.Runner(
    ...
    memory_service=memory_service
)
```

## Memory Tools

The ADK provides two tools for interacting with the `MemoryService`: `load_memory` and `preload_memory`.

### `load_memory` Tool

The `load_memory` tool allows your agent to explicitly search the memory for information. You should include this tool in your agent's tool list if you want it to be able to search the memory.

When the `load_memory` tool is included in an agent, the agent is instructed to use it when it needs to look up information from the memory.

```python
from google.adk.tools import load_memory

my_agent = LlmAgent(
    ...
    tools=[load_memory]
)
```

### `preload_memory` Tool

The `preload_memory` tool is an automatic tool that preloads memory for each LLM request. It is not called by the model directly. For each request, it searches the memory with the user's query and injects the search results into the LLM's context.

This tool is useful for providing the LLM with relevant context from past conversations without requiring the agent to explicitly call a tool.

The `preload_memory` tool is enabled by default.

### Using Memory in Your Agent

With the service configured, the ADK automatically saves session data to the Memory Bank. To make your agent use this memory, you need to call the `search_memory` method from your agent's code.

This is typically done at the beginning of a turn to fetch relevant context before generating a response.

**Example:**

```python
from google.adk.agents import Agent
from google.genai import types

class MyAgent(Agent):
    async def run(self, request: types.Content, **kwargs) -> types.Content:
        # Get the user's latest message
        user_query = request.parts[0].text

        # Search the memory for context related to the user's query
        search_result = await self.search_memory(query=user_query)

        # Create a prompt that includes the retrieved memories
        prompt = f"Based on my memory, here'''s what I recall about your query: {search_result.memories}\n\nNow, please respond to: {user_query}"

        # Call the LLM with the enhanced prompt
        return await self.llm.generate_content_async(prompt)
```

## Advanced Concepts

### How Memory Works in Practice

The memory workflow internally involves these steps:

1. **Session Interaction:** A user interacts with an agent via a `Session`, managed by a `SessionService`. Events are added, and state might be updated.
2. **Ingestion into Memory:** At some point (often when a session is considered complete or has yielded significant information), your application calls `memory_service.add_session_to_memory(session)`. This extracts relevant information from the session's events and adds it to the long-term knowledge store (in-memory dictionary or RAG Corpus).
3. **Later Query:** In a *different* (or the same) session, the user might ask a question requiring past context (e.g., \"What did we discuss about project X last week?\").
4. **Agent Uses Memory Tool:** An agent equipped with a memory-retrieval tool (like the built-in `load_memory` tool) recognizes the need for past context. It calls the tool, providing a search query (e.g., \"discussion project X last week\").
5. **Search Execution:** The tool internally calls `memory_service.search_memory(app_name, user_id, query)`.
6. **Results Returned:** The `MemoryService` searches its store (using keyword matching or semantic search) and returns relevant snippets as a `SearchMemoryResponse` containing a list of `MemoryResult` objects (each potentially holding events from a relevant past session).
7. **Agent Uses Results:** The tool returns these results to the agent, usually as part of the context or function response. The agent can then use this retrieved information to formulate its final answer to the user.

### Can an agent have access to more than one memory service?

*   **Through Standard Configuration: No.** The framework (`adk web`, `adk api_server`) is designed to be configured with one single memory service at a time via the `--memory_service_uri` flag. This single service is then provided to the agent and accessed through the built-in `self.search_memory()` method. From a configuration standpoint, you can only choose one backend (`InMemory`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`) for all agents served by that process.

*   **Within Your Agent's Code: Yes, absolutely.** There is nothing preventing you from manually importing and instantiating another memory service directly inside your agent's code. This allows you to access multiple memory sources within a single agent turn.

For example, your agent could use the framework-configured `VertexAiMemoryBankService` to recall conversational history, and also manually instantiate a `VertexAiRagMemoryService` to look up information in a technical manual.

#### Example: Using Two Memory Services

Here’s how you could implement that in your agent's code:

```python
from google.adk.agents import Agent
from google.adk.memory import VertexAiMemoryBankService, VertexAiRagMemoryService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.vertexai_memorybank_service = VertexAiMemoryBankService()
        # Manually instantiate a second memory service for document lookups
        self.vertexai_rag_service = VertexAiRagMemoryService(
            rag_corpus="your-rag-corpus-id"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. Search conversational history using the framework-provided memory
        #    (This would be VertexAiMemoryBankService if configured)
        conversation_context = await self.search_memory(query=user_query)

        # 2. Search the document knowledge base using the manually created service
        document_context = await self.vertexai_rag_service.search_memory(query=user_query)

        # Combine the context from both sources to generate a better response
        prompt = "From our past conversations, I remember:\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "From the technical manuals, I found:\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += f"Based on all this, here is my answer to ''{user_query}''':"

        return await self.llm.generate_content_async(prompt)
```