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
APP_ROOT = PROJECT_ROOT / "HabitOpsMobile"


@function_tool
def read_file(path: str) -> str:
    """Read a repository text file."""

    target = (PROJECT_ROOT / path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        return "ERROR: path outside repository"

    if not target.exists():
        return f"ERROR: file not found: {path}"

    print(f"\n>>> READ: {path}")

    return target.read_text(encoding="utf-8")


@function_tool
def write_app_file(path: str, content: str) -> str:
    """Write a file inside HabitOpsMobile."""

    clean_path = Path(path)

    # Normalize paths such as:
    # HabitOpsMobile/types/activity.ts
    # into:
    # types/activity.ts

    if (
        clean_path.parts
        and clean_path.parts[0].lower() == "habitopsmobile"
    ):
        clean_path = Path(*clean_path.parts[1:])

    target = (APP_ROOT / clean_path).resolve()

    if not target.is_relative_to(APP_ROOT):
        return "ERROR: write outside HabitOpsMobile"

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    relative = target.relative_to(APP_ROOT)

    print(
        f"\n>>> WRITE: HabitOpsMobile/{relative}"
    )

    return (
        f"Successfully wrote "
        f"HabitOpsMobile/{relative}"
    )


@function_tool
def list_app_files(path: str = ".") -> str:
    """List application files, excluding generated directories."""

    target = (APP_ROOT / path).resolve()

    if not target.is_relative_to(APP_ROOT):
        return "ERROR: path outside HabitOpsMobile"

    if not target.exists():
        return f"ERROR: path not found: {path}"

    ignored = {
        "node_modules",
        "android/build",
        "ios/build",
        ".gradle",
        ".agent_backups",
    }

    results = []

    for item in sorted(target.rglob("*")):

        if not item.is_file():
            continue

        relative = item.relative_to(APP_ROOT)

        if any(
            ignored_part in relative.parts
            for ignored_part in ignored
        ):
            continue

        results.append(str(relative))

    return "\n".join(results) or "(empty)"


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
    name="HabitOps Batch Step 1 Agent",
    model=model,
    tools=[
        read_file,
        write_app_file,
        list_app_files,
    ],
)


async def main():

    result = await Runner.run(
        agent,
        """
Read the repository documentation, especially:

docs/batch-01-react-native.md

Then inspect the existing HabitOpsMobile application.

Implement ONLY the TypeScript data/model layer required
by the Batch 01 specification.

Do not implement screens yet.

Do not install dependencies.

Do not modify Android configuration.

Do not modify iOS configuration.

Do not modify App.tsx.

Use the documentation as the source of truth for the
data models required by Batch 01.

Create the appropriate TypeScript model/type files inside
HabitOpsMobile.

After writing them:

1. List the application files.
2. Confirm the new files actually exist.
3. Read the newly created files back.
4. Report only what was actually verified.

Do not claim that anything exists unless you verified it
using the tools.
""",
        max_turns=15,
    )

    print("\n" + "=" * 60)
    print("FINAL")
    print("=" * 60)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())