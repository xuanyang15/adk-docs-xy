# Plugins

Plugins in ADK offer a modular way to extend the functionality of the `Runner`. They allow you to intercept and act on various events within the agent execution lifecycle.

## BasePlugin

`BasePlugin` is the abstract base class for all plugins. It defines a series of callback methods that you can implement to hook into different stages of the execution process, such as `before_run_callback`, `after_tool_callback`, etc.

## LoggingPlugin

ADK includes a `LoggingPlugin` that provides detailed logs of the agent's activities. This is incredibly useful for debugging and understanding how your agent is functioning.

**Example:**

```python
from google.adk.runners import Runner
from google.adk.plugins.logging_plugin import LoggingPlugin

runner = Runner(
    ...
    plugins=[LoggingPlugin()],
    ...
)
```

## Creating Custom Plugins

You can create your own plugins by inheriting from `BasePlugin` and implementing the desired callback methods. This is a powerful way to add custom features like:

*   **Monitoring:** Track agent performance and send metrics to a monitoring service.
*   **Caching:** Implement caching strategies for LLM calls or tool executions to improve performance and reduce costs.
*   **Request/Response-Body Modification:** Alter the requests and responses to and from the LLM or tools.

**Example of a custom plugin:**

```python
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

class ToolCounterPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="tool_counter")
        self.tool_count = 0

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: dict, tool_context: ToolContext
    ):
        self.tool_count += 1
        print(f"Tool call number: {self.tool_count}")
```

## Registering Plugins

To use a plugin, you pass a list of plugin instances to the `Runner`'s constructor:

```python
runner = Runner(
    ...
    plugins=[ToolCounterPlugin(), LoggingPlugin()],
    ...
)
```
Plugins are executed in the order they are registered.
