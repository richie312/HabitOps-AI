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
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "HabitOpsMobile"


# ============================================================
# PATH SAFETY
# ============================================================

def resolve_project_path(path: str) -> Path:
    target = (PROJECT_ROOT / path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        raise ValueError("Path is outside the project.")

    return target


def resolve_app_path(path: str) -> Path:
    target = (APP_ROOT / path).resolve()

    if not target.is_relative_to(APP_ROOT):
        raise ValueError(
            "Write access is restricted to HabitOpsMobile."
        )

    return target


# ============================================================
# FILE TOOLS
# ============================================================

@function_tool
def list_files(path: str = ".") -> str:
    """List files and directories in the repository."""

    print(f"[TOOL] list_files({path})")

    target = resolve_project_path(path)

    if not target.exists():
        return f"Path not found: {path}"

    ignored = {
        ".git",
        "node_modules",
        ".gradle",
        "build",
        ".agent_backups",
    }

    entries = []

    for item in sorted(target.iterdir()):
        if item.name in ignored:
            continue

        kind = "DIR" if item.is_dir() else "FILE"

        entries.append(
            f"[{kind}] {item.relative_to(PROJECT_ROOT)}"
        )

    if not entries:
        return "(empty)"

    return "\n".join(entries)


@function_tool
def read_file(path: str) -> str:
    """Read a text file from the repository."""

    print(f"[TOOL] read_file({path})")

    target = resolve_project_path(path)

    if not target.exists():
        return f"File not found: {path}"

    if not target.is_file():
        return f"Not a file: {path}"

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Unable to read as UTF-8 text: {path}"


@function_tool
def write_file(path: str, content: str) -> str:
    """Write a text file. Writes are restricted to HabitOpsMobile."""

    print(f"[TOOL] write_file({path})")

    target = resolve_app_path(path)

    target.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Backup existing file
    # --------------------------------------------------------

    if target.exists():

        backup_root = APP_ROOT / ".agent_backups"

        relative = target.relative_to(APP_ROOT)

        backup_path = backup_root / relative

        backup_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_path.write_bytes(
            target.read_bytes()
        )

        print(
            f"[BACKUP] {target.relative_to(PROJECT_ROOT)}"
        )

    # --------------------------------------------------------
    # Write new content
    # --------------------------------------------------------

    target.write_text(
        content,
        encoding="utf-8",
    )

    print(
        f"[WRITE] {target.relative_to(PROJECT_ROOT)}"
    )

    return (
        f"Written successfully: "
        f"{target.relative_to(PROJECT_ROOT)}"
    )


# ============================================================
# COMMAND TOOL
# ============================================================

@function_tool
def run_command(command: str) -> str:
    """
    Run a safe development command inside HabitOpsMobile.

    Commands are intentionally restricted to development,
    testing, linting and build operations.
    """

    print(f"\n[COMMAND] {command}")
    print(
        f"[WORKDIR] {APP_ROOT}"
    )

    command_lower = command.lower().strip()

    blocked_patterns = [
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

    for pattern in blocked_patterns:
        if pattern in command_lower:
            return (
                f"BLOCKED: destructive command detected: "
                f"{pattern}"
            )

    allowed_prefixes = [
        "npm ",
        "npx ",
        "node ",
        "yarn ",
        "gradlew ",
        ".\\gradlew ",
        "powershell ",
    ]

    if not any(
        command_lower.startswith(prefix)
        for prefix in allowed_prefixes
    ):
        return (
            "BLOCKED: command is not in the allowed "
            "development command set."
        )

    try:

        process = subprocess.run(
            command,
            cwd=APP_ROOT,
            shell=True,
            capture_output=True,
            text=True,
            timeout=900,
        )

        output = ""

        if process.stdout:
            output += process.stdout

        if process.stderr:
            output += "\n[STDERR]\n"
            output += process.stderr

        output += (
            f"\n\n[EXIT CODE] {process.returncode}"
        )

        print(
            f"[COMMAND COMPLETE] exit={process.returncode}"
        )

        return output[-20000:]

    except subprocess.TimeoutExpired:

        print("[COMMAND TIMEOUT]")

        return (
            "COMMAND TIMED OUT after 900 seconds."
        )

    except Exception as exc:

        print(
            f"[COMMAND ERROR] {exc}"
        )

        return (
            f"COMMAND ERROR: {exc}"
        )


# ============================================================
# DOCUMENTATION LOADER
# ============================================================

def load_repository_context() -> str:

    files = []

    readme = PROJECT_ROOT / "README.md"

    if readme.exists():
        files.append(readme)

    docs = PROJECT_ROOT / "docs"

    if docs.exists():
        files.extend(
            sorted(docs.glob("*.md"))
        )

    context_parts = []

    for file in files:

        relative = file.relative_to(
            PROJECT_ROOT
        )

        print(
            f"[DOC] Loading {relative}"
        )

        content = file.read_text(
            encoding="utf-8"
        )

        context_parts.append(
            f"""
===== {relative} =====

{content}

===== END {relative} =====
"""
        )

    return "\n".join(context_parts)


# ============================================================
# MODEL
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
# AGENT
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
# MAIN
# ============================================================

async def main():

    print()
    print("=" * 70)
    print("HabitOps AI Agent")
    print("=" * 70)
    print()

    print(
        f"[PROJECT] {PROJECT_ROOT}"
    )

    print(
        f"[APP] {APP_ROOT}"
    )

    print()
    print(
        "[PHASE] Loading repository documentation..."
    )

    repository_context = (
        load_repository_context()
    )

    print()
    print(
        "[PHASE] Starting agent..."
    )
    print()

    prompt = f"""
{repository_context}

Use the repository documentation above as the
authoritative source of truth.

Inspect the existing repository and application before
making changes.

Implement the work required by the documentation.

Use the available tools to make the actual changes.

Do not merely describe code.

After making changes:

1. Inspect the resulting filesystem.
2. Read important changed files.
3. Install required dependencies if necessary.
4. Run appropriate tests, linting, or build commands.
5. If verification fails, diagnose the failure.
6. Correct the implementation.
7. Verify again.
8. Only report success when the filesystem and command
   results provide evidence that the implementation works.

Do not claim that a file, directory, dependency,
navigation system, screen, or feature exists unless
you have verified it using the available tools.

Do not modify files outside the permitted application
area.

At the end, provide a concise factual summary of:
- files actually created or modified
- dependencies actually installed
- commands actually executed
- verification results
- any remaining problems
"""

    result = await Runner.run(
        agent,
        prompt,
        max_turns=50,
    )

    print()
    print("=" * 70)
    print("AGENT FINISHED")
    print("=" * 70)
    print()

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())