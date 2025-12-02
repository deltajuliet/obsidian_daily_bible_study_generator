"""Reading segment model."""

from dataclasses import dataclass
from typing import Optional

from .book import Book


@dataclass
class ReadingSegment:
    """Represents a portion of a Bible book to be read."""

    book: Book
    start_chapter: int
    end_chapter: int
    verse_count: int
    word_count: int
    estimated_minutes: int

    def __post_init__(self) -> None:
        """Validate reading segment after initialization."""
        if self.start_chapter < 1 or self.start_chapter > self.book.chapters:
            raise ValueError(
                f"Invalid start_chapter {self.start_chapter} for {self.book.name} "
                f"(valid range: 1-{self.book.chapters})"
            )
        
        if self.end_chapter < 1 or self.end_chapter > self.book.chapters:
            raise ValueError(
                f"Invalid end_chapter {self.end_chapter} for {self.book.name} "
                f"(valid range: 1-{self.book.chapters})"
            )
        
        if self.start_chapter > self.end_chapter:
            raise ValueError(
                f"start_chapter ({self.start_chapter}) cannot be greater than "
                f"end_chapter ({self.end_chapter})"
            )

    @property
    def chapter_count(self) -> int:
        """Get the number of chapters in this segment."""
        return self.end_chapter - self.start_chapter + 1

    @property
    def chapter_range_str(self) -> str:
        """Get formatted chapter range string."""
        if self.start_chapter == self.end_chapter:
            return str(self.start_chapter)
        return f"{self.start_chapter}-{self.end_chapter}"

    def __str__(self) -> str:
        """String representation of the reading segment."""
        return f"{self.book.name} {self.chapter_range_str}"

    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering."""
        return {
            "book": self.book.name,
            "book_abbrev": self.book.abbreviation,
            "start_chapter": self.start_chapter,
            "end_chapter": self.end_chapter,
            "chapter_range": self.chapter_range_str,
            "verse_count": self.verse_count,
            "word_count": self.word_count,
            "estimated_minutes": self.estimated_minutes,
            "testament": self.book.testament.value,
            "genre": self.book.genre.value,
        }
