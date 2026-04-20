from pathlib import Path

def ensure_dir(file_path: str, parents: bool = True) -> None:
    """Ensure that the directory for the given file path exists."""

    directory = Path(file_path)
    if not directory.exists():
        directory.mkdir(parents, exist_ok=True)

