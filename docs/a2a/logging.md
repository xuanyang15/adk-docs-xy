# A2A Logging

The ADK provides detailed and structured logging for A2A (Agent-to-Agent) communication, which is invaluable for debugging and monitoring multi-agent systems. When you enable debug-level logging, the ADK will output rich information about A2A requests and responses.

## Enabling A2A Logging

To enable A2A logging, you can set the log level to `debug` when running your ADK server. For example:

```bash
adk api_server --a2a --port 8001 path/to/your/agent --log_level debug
```

## Understanding the Logs

The A2A logs are designed to be human-readable and provide a clear view of the communication between agents.

### A2A Request Logs

When an agent sends a message to another agent via A2A, a log entry similar to the following is generated:

```
A2A Send Message Request:
-----------------------------------------------------------
Message:
  ID: <message_id>
  Role: <role>
  Task ID: <task_id>
  Context ID: <context_id>
-----------------------------------------------------------
Message Parts:
Part 0: <part_content>
...
-----------------------------------------------------------
```

The request log includes:
- **Message**: Core details of the message, including its ID, role, task ID, and context ID.
- **Message Parts**: The content of each part of the message. For text parts, a snippet of the text is shown. For data parts, a summary of the data keys is provided.

### A2A Response Logs

When an agent receives a response from another agent, a log entry is generated that can represent either a `Task` or a `Message`:

```
A2A Response:
-----------------------------------------------------------
Type: SUCCESS
Result Type: <result_type>
-----------------------------------------------------------
Result Details:
...
-----------------------------------------------------------
Status Message:
...
-----------------------------------------------------------
History:
...
-----------------------------------------------------------
```

The response log includes:
- **Result Type**: The type of the result, which can be a `ClientEvent` (containing a `Task`) or a `Message`.
- **Result Details**: Detailed information about the result, such as task status, message content, and metadata.
- **Status Message**: If the response is a task update, this section contains the status message from the remote agent.
- **History**: The conversation history associated with the task.

By inspecting these logs, you can trace the flow of communication between your agents, understand the content of the messages being exchanged, and diagnose any issues that may arise.
