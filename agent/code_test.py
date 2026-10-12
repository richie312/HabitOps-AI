@function_tool
def write_app_file(path: str, content: str) -> str:
    """Write a file inside HabitOpsMobile."""

    # Accept either:
    #   App.tsx
    # or:
    #   HabitOpsMobile/App.tsx
    #
    # Internally everything is normalized to APP_ROOT.

    clean_path = Path(path)

    if clean_path.parts and clean_path.parts[0].lower() == "habitopsmobile":
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