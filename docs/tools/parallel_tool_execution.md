# Parallel Tool Execution

The Agent Development Kit (ADK) supports the parallel execution of tools, which can significantly improve the performance and responsiveness of your agents. This guide explains how parallel tool execution works in the ADK and how to design your tools to take full advantage of this feature.

## How it Works

When an agent needs to call multiple tools to fulfill a user's request, the ADK can execute these calls concurrently. This is achieved using Python's `asyncio` library, which allows for non-blocking I/O operations. The ADK's core logic for handling tool calls uses `asyncio.gather` to run multiple awaitable tool functions at the same time.

This means that if you have three tools that each take 2 seconds to run, the total execution time will be approximately 2 seconds, not 6 seconds. This is a significant performance improvement, especially for agents that rely on multiple external APIs or long-running tasks.

## Writing Parallel-Ready Tools

To enable parallel execution, your tool functions must be defined as asynchronous functions using `async def`. This allows the ADK to run them concurrently in the `asyncio` event loop.

### Use Non-Blocking Operations

It is crucial to use non-blocking operations within your async tool functions. If you use a blocking operation, such as `time.sleep()`, it will block the entire event loop and prevent other tools from running in parallel.

Instead, use `await asyncio.sleep()` for non-blocking delays. Similarly, when making network requests, use an `asyncio`-compatible HTTP library, such as `aiohttp`, to ensure that your tool does not block the event loop.

Here is an example of a parallel-ready tool:

```python
import asyncio
from google.adk.tools.tool_context import ToolContext

async def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Get the current weather for a city."""
    # Simulate a non-blocking network request
    await asyncio.sleep(2)
    # ... rest of the tool logic
```

### Thread Safety and State Management

When multiple tools run in parallel, they may need to access or modify shared state. The ADK provides a thread-safe mechanism for managing state through the `tool_context.state` dictionary. You can safely read from and write to this dictionary from multiple concurrent tools without worrying about race conditions.

Here is an example of how to use `tool_context.state` in a thread-safe way:

```python
async def my_tool(tool_context: ToolContext) -> dict:
    """A tool that modifies shared state."""
    # Safely update the shared state
    if "requests" not in tool_context.state:
        tool_context.state["requests"] = []
    tool_context.state["requests"].append({"tool": "my_tool"})
    return {"status": "success"}
```

## Example: A Parallel-Ready Agent

Here is an example of an agent with multiple parallel-ready tools:

```python
from google.adk import Agent
import asyncio
from typing import List
from google.adk.tools.tool_context import ToolContext

async def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Get the current weather for a city."""
    await asyncio.sleep(2)
    return {"city": city, "temperature": "72F"}

async def get_currency_rate(from_currency: str, to_currency: str, tool_context: ToolContext) -> dict:
    """Get the exchange rate between two currencies."""
    await asyncio.sleep(1.5)
    return {"from": from_currency, "to": to_currency, "rate": 1.2}

root_agent = Agent(
    model='gemini-2.0-flash',
    name='parallel_function_test_agent',
    description='Agent for testing parallel function calling.',
    instruction='You are a helpful assistant that can provide information about weather and currency rates. You should call multiple functions in parallel to provide faster responses.',
    tools=[
        get_weather,
        get_currency_rate,
    ],
)
```

With this agent, you can ask questions that trigger parallel tool calls:

*   "What's the weather in New York and London?" (2 parallel calls, ~2s total)
*   "What's the weather in Paris and the USD to EUR exchange rate?" (2 parallel calls, ~2s total)

## Performance Benefits

The performance benefits of parallel tool execution are significant. Consider the following example:

*   **Sequential-style request:** "First get the weather in New York, then get the weather in London, then get the weather in Tokyo."
    *   *Expected time: ~6 seconds (2s + 2s + 2s)*
*   **Parallel-style request:** "Get the weather in New York, London, and Tokyo."
    *   *Expected time: ~2 seconds (max of parallel 2s delays)*

The parallel version is **3x faster** due to concurrent execution.

By designing your tools to be asynchronous and non-blocking, you can build high-performance agents that provide a more responsive and engaging user experience.
