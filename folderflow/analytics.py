from dataclasses import dataclass

from .inventory import FileRecord


@dataclass(frozen=True)
class CategoryUsage:
    files: int
    bytes: int

    def to_dict(self) -> dict:
        return {"files": self.files, "bytes": self.bytes}


@dataclass(frozen=True)
class InventorySummary:
    total_files: int
    total_bytes: int
    by_category: dict[str, CategoryUsage]

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "total_bytes": self.total_bytes,
            "by_category": {
                category: usage.to_dict()
                for category, usage in self.by_category.items()
            },
        }


def summarize_inventory(records: list[FileRecord]) -> InventorySummary:
    counts: dict[str, int] = {}
    sizes: dict[str, int] = {}
    for record in records:
        counts[record.category] = counts.get(record.category, 0) + 1
        sizes[record.category] = sizes.get(record.category, 0) + record.size

    categories = {
        category: CategoryUsage(
            files=counts[category],
            bytes=sizes[category],
        )
        for category in sorted(counts)
    }
    return InventorySummary(
        total_files=len(records),
        total_bytes=sum(record.size for record in records),
        by_category=categories,
    )
