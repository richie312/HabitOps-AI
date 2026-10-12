import asyncio
from pathlib import Path

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@function_tool
def write_test_file(content: str) -> str:
    """Create the requested test file in HabitOpsMobile."""

    target = PROJECT_ROOT / "HabitOpsMobile" / "agent_test.txt"

    target.write_text(
        content,
        encoding="utf-8",
    )

    print(f"\n>>> ACTUAL WRITE: {target}")

    return f"Successfully created {target}"


set_tracing_disabled(True)

client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

model = OpenAIChatCompletionsModel(
    model="qwen3:8b",
    openai_client=client,
)

agent = Agent(
    name="Write Test Agent",
    model=model,
    tools=[write_test_file],
)


async def main():

    result = await Runner.run(
        agent,
        """
Use the write_test_file tool.

Create the test file with exactly this content:

Batch 01 agent write test

You must actually call the tool.
Do not merely describe what you would do.
""",
        max_turns=5,
    )

    print("\n=== FINAL ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())