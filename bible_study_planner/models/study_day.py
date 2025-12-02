"""Study day model."""

from dataclasses import dataclass, field
from datetime import date
from typing import List

from .reading_segment import ReadingSegment


@dataclass
class StudyDay:
    """Represents a single day in the reading plan."""

    date: date
    day_number: int
    reading_segments: List[ReadingSegment]
    total_days: int

    def __post_init__(self) -> None:
        """Validate study day after initialization."""
        if self.day_number < 1 or self.day_number > self.total_days:
            raise ValueError(
                f"Invalid day_number {self.day_number} (valid range: 1-{self.total_days})"
            )
        
        if not self.reading_segments:
            raise ValueError("StudyDay must have at least one reading segment")

    @property
    def total_verses(self) -> int:
        """Total verses to read on this day."""
        return sum(segment.verse_count for segment in self.reading_segments)

    @property
    def total_words(self) -> int:
        """Total words to read on this day."""
        return sum(segment.word_count for segment in self.reading_segments)

    @property
    def total_minutes(self) -> int:
        """Total estimated reading time in minutes."""
        return sum(segment.estimated_minutes for segment in self.reading_segments)

    @property
    def total_chapters(self) -> int:
        """Total chapters to read on this day."""
        return sum(segment.chapter_count for segment in self.reading_segments)

    @property
    def progress_percentage(self) -> float:
        """Progress percentage through the plan."""
        return round((self.day_number / self.total_days) * 100, 1)

    @property
    def primary_book(self) -> str:
        """Get the name of the primary (first) book for this day."""
        return self.reading_segments[0].book.name

    @property
    def primary_testament(self) -> str:
        """Get the testament of the primary reading."""
        return self.reading_segments[0].book.testament.value

    @property
    def primary_genre(self) -> str:
        """Get the genre of the primary reading."""
        return self.reading_segments[0].book.genre.value

    def get_all_books(self) -> List[str]:
        """Get list of all book names for this day."""
        return [segment.book.name for segment in self.reading_segments]

    def get_tags(self, base_tags: List[str], include_testament: bool = True, 
                 include_genre: bool = True, include_book: bool = False) -> List[str]:
        """Generate tags for this study day.
        
        Args:
            base_tags: Base tags to include (e.g., ["bible-study", "daily"])
            include_testament: Include testament tag
            include_genre: Include genre tag
            include_book: Include book name tag(s)
            
        Returns:
            List of tags for Obsidian frontmatter
        """
        tags = base_tags.copy()
        
        if include_testament:
            tags.append(self.primary_testament)
        
        if include_genre:
            tags.append(self.primary_genre.replace("_", "-"))
        
        if include_book:
            for book_name in self.get_all_books():
                tags.append(book_name.lower().replace(" ", "-"))
        
        return tags

    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering."""
        return {
            "date": self.date,
            "day_number": self.day_number,
            "total_days": self.total_days,
            "progress_percentage": self.progress_percentage,
            "reading_segments": [segment.to_dict() for segment in self.reading_segments],
            "total_verses": self.total_verses,
            "total_words": self.total_words,
            "total_minutes": self.total_minutes,
            "total_chapters": self.total_chapters,
            "primary_book": self.primary_book,
            "primary_testament": self.primary_testament,
            "primary_genre": self.primary_genre,
            "all_books": self.get_all_books(),
        }
