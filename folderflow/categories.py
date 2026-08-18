from pathlib import Path
from typing import Mapping


DEFAULT_CATEGORIES: dict[str, frozenset[str]] = {
    "Documents": frozenset({".doc", ".docx", ".md", ".pdf", ".rtf", ".txt"}),
    "Images": frozenset({".gif", ".heic", ".jpeg", ".jpg", ".png", ".svg", ".webp"}),
    "Audio": frozenset({".aac", ".flac", ".m4a", ".mp3", ".ogg", ".wav"}),
    "Video": frozenset({".avi", ".mkv", ".mov", ".mp4", ".webm"}),
    "Archives": frozenset({".7z", ".gz", ".rar", ".tar", ".zip"}),
    "Code": frozenset({".css", ".html", ".java", ".js", ".json", ".py", ".sql", ".ts"}),
    "Spreadsheets": frozenset({".csv", ".ods", ".xls", ".xlsx"}),
}


def classify_file(
    path: Path,
    categories: Mapping[str, frozenset[str]] = DEFAULT_CATEGORIES,
) -> str:
    extension = path.suffix.casefold()
    for category, extensions in categories.items():
        if extension in extensions:
            return category
    return "Other"
