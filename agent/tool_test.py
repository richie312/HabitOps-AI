import asyncio
import subprocess
from pathlib import Path

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)


# ============================================================
# Repository
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# Path handling
# ============================================================

def resolve_project_path(path: str) -> Path:
    target = (PROJECT_ROOT / path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        raise ValueError("Path is outside the repository.")

    return target


def resolve_app_path(path: str) -> Path:
    target = (PROJECT_ROOT / "HabitOpsMobile" / path).resolve()

    app_root = (PROJECT_ROOT / "HabitOpsMobile").resolve()

    if not target.is_relative_to(app_root):
        raise ValueError(
            "Write access is restricted to HabitOpsMobile."
        )

    return target


# ============================================================
# Tools
# ============================================================

@function_tool
def list_files(path: str = ".") -> str:
    """List files and directories in the repository."""

    print(f"\n[TOOL] list_files: {path}")

    target = resolve_project_path(path)

    if not target.exists():
        return f"Path does not exist: {path}"

    ignored = {
        ".git",
        "node_modules",
        ".gradle",
        "build",
        ".agent_backups",
    }

    results = []

    for item in sorted(target.iterdir()):
        if item.name in ignored:
            continue

        kind = "DIR" if item.is_dir() else "FILE"

        results.append(
            f"[{kind}] {item.relative_to(PROJECT_ROOT)}"
        )

    return "\n".join(results) or "(empty)"


@function_tool
def read_file(path: str) -> str:
    """Read a text file from the repository."""

    print(f"\n[TOOL] read_file: {path}")

    target = resolve_project_path(path)

    if not target.exists():
        return f"File does not exist: {path}"

    if not target.is_file():
        return f"Not a file: {path}"

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Unable to read UTF-8 file: {path}"


@function_tool
def write_file(path: str, content: str) -> str:
    """
    Write a file inside the application directory.

    Existing files are backed up before modification.
    """

    print(f"\n[TOOL] write_file: {path}")

    target = resolve_app_path(path)

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if target.exists():

        backup_root = (
            PROJECT_ROOT
            / "HabitOpsMobile"
            / ".agent_backups"
        )

        relative = target.relative_to(
            PROJECT_ROOT / "HabitOpsMobile"
        )

        backup = backup_root / relative

        backup.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup.write_bytes(
            target.read_bytes()
        )

        print(
            f"[BACKUP] "
            f"{target.relative_to(PROJECT_ROOT)}"
        )

    target.write_text(
        content,
        encoding="utf-8",
    )

    print(
        f"[WRITE] "
        f"{target.relative_to(PROJECT_ROOT)}"
    )

    return (
        f"Successfully written: "
        f"{target.relative_to(PROJECT_ROOT)}"
    )


@function_tool
def run_command(command: str) -> str:
    """
    Execute a development command inside HabitOpsMobile.

    Only development-oriented commands are allowed.
    """

    print("\n" + "=" * 60)
    print(f"[COMMAND] {command}")
    print("=" * 60)

    command_lower = command.lower().strip()

    blocked = [
        "rm -rf",
        "rmdir /s",
        "del /f",
        "format ",
        "shutdown",
        "restart-computer",
        "remove-item",
        "git reset --hard",
        "git clean -fd",
    ]

    for pattern in blocked:

        if pattern in command_lower:

            return (
                f"BLOCKED destructive command: {pattern}"
            )

    allowed = [
        "npm ",
        "npx ",
        "node ",
        "yarn ",
        ".\\gradlew ",
        "gradlew ",
        "powershell ",
    ]

    if not any(
        command_lower.startswith(prefix)
        for prefix in allowed
    ):

        return (
            "BLOCKED command. "
            "Only approved development commands "
            "may be executed."
        )

    app_root = PROJECT_ROOT / "HabitOpsMobile"

    try:

        process = subprocess.run(
            command,
            cwd=app_root,
            shell=True,
            capture_output=True,
            text=True,
            timeout=900,
        )

        output = ""

        if process.stdout:
            output += process.stdout

        if process.stderr:
            output += (
                "\n[STDERR]\n"
                + process.stderr
            )

        output += (
            f"\n[EXIT CODE] "
            f"{process.returncode}"
        )

        print(
            f"[COMMAND COMPLETE] "
            f"exit={process.returncode}"
        )

        return output[-25000:]

    except subprocess.TimeoutExpired:

        print("[COMMAND TIMEOUT]")

        return (
            "Command timed out after 900 seconds."
        )

    except Exception as exc:

        print(
            f"[COMMAND ERROR] {exc}"
        )

        return f"Command failed: {exc}"


# ============================================================
# Documentation
# ============================================================

def load_repository_context() -> str:

    documents = []

    readme = PROJECT_ROOT / "README.md"

    if readme.exists():
        documents.append(readme)

    docs = PROJECT_ROOT / "docs"

    if docs.exists():

        documents.extend(
            sorted(docs.glob("*.md"))
        )

    context = []

    for document in documents:

        relative = document.relative_to(
            PROJECT_ROOT
        )

        print(
            f"[DOC] Loading {relative}"
        )

        content = document.read_text(
            encoding="utf-8"
        )

        context.append(
            f"""
===== {relative} =====

{content}

===== END {relative} =====
"""
        )

    return "\n".join(context)


# ============================================================
# Model
# ============================================================

set_tracing_disabled(True)

ollama_client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

model = OpenAIChatCompletionsModel(
    model="qwen3:8b",
    openai_client=ollama_client,
)


# ============================================================
# Agent
# ============================================================

agent = Agent(
    name="HabitOps Agent",
    model=model,
    tools=[
        list_files,
        read_file,
        write_file,
        run_command,
    ],
)


# ============================================================
# Main
# ============================================================

async def main():

    print()
    print("=" * 70)
    print("HabitOps AI Agent")
    print("=" * 70)
    print()

    repository_context = (
        load_repository_context()
    )

    print()
    print("[AGENT] Repository context loaded.")
    print("[AGENT] Starting execution...")
    print()

    prompt = f"""
The following Markdown documents describe the repository
and the work currently required.

They are the source of truth.

{repository_context}

You are operating as a software engineering agent.

Your job is to inspect the actual repository and implement
the work described by the documentation.

Do not assume the current implementation is correct.

Follow this workflow:

PHASE 1 — UNDERSTAND

Read the relevant documentation.

Identify the current task and its acceptance criteria.

Do not invent requirements that are not present in the
documentation.

PHASE 2 — INSPECT

Inspect the existing application using the available tools.

Determine what already exists.

Do not assume that a file, directory, dependency, screen,
configuration, or feature exists merely because another
document or previous response says it exists.

PHASE 3 — PLAN

Determine the files and dependencies that actually need
to change.

Keep the implementation consistent with the existing
project structure.

PHASE 4 — IMPLEMENT

Use the file tools to make the actual changes.

Do not merely provide code in your response.

If dependencies are required, modify the application
configuration and use the command tool to install them.

PHASE 5 — VERIFY FILESYSTEM

After implementation, use the tools again.

Confirm that every important file or directory that you
claim to have created actually exists.

Read important generated files back from disk.

PHASE 6 — BUILD AND TEST

Run appropriate development commands.

If a command fails, inspect the error.

Fix the implementation.

Run the verification again.

PHASE 7 — FINAL VERIFICATION

Before reporting success, verify the actual filesystem
and command results.

Your final response must distinguish between:

VERIFIED
    Things confirmed using tools.

NOT VERIFIED
    Things you could not confirm.

FAILED
    Things that were attempted but failed.

Never claim successful implementation based only on your
intention or plan.

Do not proceed to unrelated future batches.

Do not modify files outside the permitted application
directory.

Do not modify the repository documentation unless the
documentation itself explicitly requires it.
"""

    result = await Runner.run(
        agent,
        prompt,
        max_turns=60,
    )

    print()
    print("=" * 70)
    print("AGENT FINISHED")
    print("=" * 70)
    print()

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())