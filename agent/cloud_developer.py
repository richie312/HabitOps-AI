import asyncio
import os
import subprocess
import sys
from pathlib import Path

from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, set_default_openai_client


# ------------------------------------------------------------
# Project configuration
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_ROOT = PROJECT_ROOT / "HabitOpsMobile"

CLOUD_MODEL = "gpt-5.6"


# ------------------------------------------------------------
# API key
# ------------------------------------------------------------

def get_openai_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")

    if key:
        return key

    try:
        key = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')",
            ],
            text=True,
        ).strip()
    except Exception:
        key = ""

    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY was not found in the environment."
        )

    return key


# ------------------------------------------------------------
# Tools
# ------------------------------------------------------------

@function_tool
def read_repository_file(path: str) -> str:
    """
    Read a text file from the HabitOps repository.

    Paths are relative to the repository root.
    """

    clean_path = Path(path)

    if clean_path.is_absolute():
        return "ERROR: Absolute paths are not allowed."

    target = (PROJECT_ROOT / clean_path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        return "ERROR: Path is outside the repository."

    if not target.exists():
        return f"ERROR: File does not exist: {path}"

    if not target.is_file():
        return f"ERROR: Not a file: {path}"

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"ERROR: File is not UTF-8 text: {path}"


@function_tool
def list_repository_files(path: str = ".") -> str:
    """
    List files and directories in a repository directory.

    Paths are relative to the repository root.
    """

    clean_path = Path(path)

    if clean_path.is_absolute():
        return "ERROR: Absolute paths are not allowed."

    target = (PROJECT_ROOT / clean_path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        return "ERROR: Path is outside the repository."

    if not target.exists():
        return f"ERROR: Directory does not exist: {path}"

    if not target.is_dir():
        return f"ERROR: Not a directory: {path}"

    entries = []

    for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        prefix = "[DIR] " if item.is_dir() else "[FILE] "
        entries.append(prefix + str(item.relative_to(PROJECT_ROOT)))

    return "\n".join(entries) if entries else "(empty directory)"



@function_tool
def write_app_file(path: str, content: str) -> str:
    """
    Write or modify an application/project file.

    Allowed project areas:
    - HabitOpsMobile/
    - backend/
    - infrastructure/
    - agent/
    - labs/

    Documentation files are read-only through this tool.
    """

    clean_path = Path(path)

    if clean_path.is_absolute():
        return "ERROR: Absolute paths are not allowed."

    target = (PROJECT_ROOT / clean_path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        return "ERROR: Path is outside the repository."

    allowed_roots = {
        "habitopsmobile",
        "backend",
        "infrastructure",
        "agent",
        "labs",
    }

    if not target.relative_to(PROJECT_ROOT).parts:
        return "ERROR: Invalid project path."

    root_name = target.relative_to(PROJECT_ROOT).parts[0].lower()

    if root_name not in allowed_roots:
        return (
            "ERROR: Writes are restricted to application/project "
            "directories. Documentation files are read-only."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"SUCCESS: Wrote {target.relative_to(PROJECT_ROOT)}"

@function_tool
def git_status_and_diff() -> str:
    """
    Return the current Git working-tree status and diff.
    """

    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    diff = subprocess.run(
        ["git", "diff"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    return (
        "GIT STATUS:\n"
        + status.stdout
        + "\n"
        + "GIT DIFF:\n"
        + diff.stdout
    )


# ------------------------------------------------------------
# Agent
# ------------------------------------------------------------

async def run_agent(spec_path: str):

    specification = Path(spec_path)

    if not specification.is_absolute():
        specification = (PROJECT_ROOT / specification).resolve()
    else:
        specification = specification.resolve()

    if not specification.is_relative_to(PROJECT_ROOT):
        raise RuntimeError(
            "Specification must be inside the HabitOps repository."
        )

    if not specification.exists():
        raise FileNotFoundError(
            f"Specification does not exist: {specification}"
        )

    relative_spec = specification.relative_to(PROJECT_ROOT)

    print("=" * 70)
    print("CLOUD DEVELOPMENT AGENT")
    print("=" * 70)
    print(f"Repository : {PROJECT_ROOT}")
    print(f"Specification: {relative_spec}")
    print(f"Model      : {CLOUD_MODEL}")
    print("=" * 70)

    api_key = get_openai_api_key()

    cloud_client = AsyncOpenAI(api_key=api_key)
    set_default_openai_client(cloud_client)

    agent = Agent(
        name="Cloud Development Agent",
        model=CLOUD_MODEL,
        instructions=f"""
You are the primary software development agent for the HabitOps AI
repository.

You have been given a batch specification:

{relative_spec}

Your job is to implement that specification in the repository.

IMPORTANT WORKFLOW:

1. Read the supplied batch specification completely.
2. Read any referenced previous batch specifications.
3. Inspect the existing repository and application before changing anything.
4. Inspect the current Git status and diff.
5. Determine what is already implemented.
6. Identify gaps between the existing implementation and the specification.
7. Create an implementation plan internally.
8. Modify the repository using the provided write tools.
9. Re-read important files after modifying them.
10. Inspect Git status and diff again.
11. Report exactly what was changed.

IMPORTANT RULES:

- The Markdown specification is the source of truth.
- Do not invent requirements.
- Do not assume a feature exists merely because a previous agent claimed it.
- Inspect the actual files.
- Do not introduce requirements from future batches.
- Respect the specification's explicit out-of-scope requirements.
- Keep the implementation consistent with the existing architecture.
- Prefer reusable components and strong TypeScript typing where applicable.
- Do not use `any` unless genuinely necessary.
- Do not modify files outside the intended project scope unless the
  specification explicitly requires it.
- Do not merely describe code. Actually implement the required changes.

VERIFICATION:

Before reporting completion, verify the important files by reading them
again and inspect the Git status/diff.

Your final response must contain:

1. IMPLEMENTATION STATUS
2. Files created
3. Files modified
4. Important changes
5. Verification performed
6. Remaining issues, if any

Do not claim that something was built, tested, or verified unless you
actually performed that action.
""",
        tools=[
    read_repository_file,
    list_repository_files,
    write_app_file,
    git_status_and_diff,
        ],
    )

    result = await Runner.run(
        agent,
        input=(
            f"Implement the batch specification located at "
            f"`{relative_spec}`. Begin by reading the specification "
            f"and inspecting the existing repository."
        ),
        max_turns=60,
    )

    print("\n")
    print("=" * 70)
    print("AGENT RESULT")
    print("=" * 70)
    print(result.final_output)
    print("=" * 70)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def main():

    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python agent/cloud_developer.py <specification-path>\n\n"
            "Example:\n"
            "  python agent/cloud_developer.py "
            "docs/batch-02-mobile-completion.md"
        )
        sys.exit(1)

    spec_path = sys.argv[1]

    asyncio.run(run_agent(spec_path))


if __name__ == "__main__":
    main()