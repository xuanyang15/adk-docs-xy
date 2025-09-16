# ADK with Agent2Agent (A2A) Protocol

With Agent Development Kit (ADK), you can build complex multi-agent systems where different agents need to collaborate and interact using [Agent2Agent (A2A) Protocol](https://a2a-protocol.org/)! This section provides a comprehensive guide to building powerful multi-agent systems where agents can communicate and collaborate securely and efficiently.

Navigate through the guides below to learn about ADK's A2A capabilities:

  **[Introduction to A2A](./intro.md)**

  Start here to learn the fundamentals of A2A by building a multi-agent system with a root agent, a local sub-agent, and a remote A2A agent.

  **[A2A Quickstart (Exposing)](./quickstart-exposing.md)**

  This quickstart covers: **"I have an agent. How do I expose it so that other agents can use my agent via A2A?"**.

  **[A2A Quickstart (Consuming)](./quickstart-consuming.md)**

  This quickstart covers: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**.

  [**Official Website for Agent2Agent (A2A) Protocol**](https://a2a-protocol.org/)

  The official website for A2A Protocol.

## A2A Logging

ADK provides detailed, structured logging for A2A requests and responses to help with debugging and monitoring multi-agent interactions. When you enable logging in your ADK application, the A2A communications will be automatically logged with a clear and easy-to-read format.

The logs include:

*   **Request and Response Details:** Information about the message, such as message ID, role, task ID, and context ID.
*   **Message Parts:** The content of each part of the message, with a summary for large data parts.
*   **Metadata:** Any metadata associated with the message or task.
*   **Status Messages:** The status of the task, including state and any status messages.
*   **History:** A summary of the conversation history.

These structured logs make it easier to trace the flow of communication between agents and understand the state of each agent at different points in time.
