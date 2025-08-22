# Planners

ADK provides a planning framework that allows agents to create and execute plans to address complex user queries. This is particularly useful for tasks that require multiple steps or tools to be used in a sequence.

## BasePlanner

The `BasePlanner` is an abstract base class that defines the interface for all planners. It has two main methods:

-   `build_planning_instruction(self, readonly_context: ReadonlyContext, llm_request: LlmRequest) -> Optional[str]`: This method is responsible for creating the planning instruction that will be sent to the LLM.
-   `process_planning_response(self, callback_context: CallbackContext, response_parts: List[types.Part]) -> Optional[List[types.Part]]`: This method processes the LLM's response and extracts the plan.

## Built-in Planners

ADK comes with two built-in planners:

### `BuiltInPlanner`

The `BuiltInPlanner` uses the model's built-in thinking features to generate a plan. It is simple to use and can be configured with a `thinking_config`.

**Example:**

```python
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.genai import types

planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thought_token_limit=8192,
    )
)
```

### `PlanReActPlanner`

The `PlanReActPlanner` implements the ReAct (Reason and Act) pattern. It constrains the LLM to generate a plan, then execute actions and observe the results, and finally produce a final answer. This planner uses specific tags in the prompt to guide the LLM's output, such as `/*PLANNING*/`, `/*ACTION*/`, and `/*REASONING*/`.

## How to use Planners

To use a planner, you need to set the `planner` attribute of your `LlmAgent`:

```python
from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners.plan_re_act_planner import PlanReActPlanner

agent = LlmAgent(
    ...
    planner=PlanReActPlanner(),
    ...
)
```

## Creating Custom Planners

You can create your own custom planner by extending the `BasePlanner` and implementing the `build_planning_instruction` and `process_planning_response` methods. This allows you to define your own planning logic and prompt engineering techniques.
