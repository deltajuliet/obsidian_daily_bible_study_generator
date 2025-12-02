"""Book model and related enums."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Testament(Enum):
    """Testament enumeration."""

    OLD = "old"
    NEW = "new"


class Genre(Enum):
    """Bible book genre enumeration."""

    LAW = "law"
    HISTORY = "history"
    WISDOM = "wisdom"
    MAJOR_PROPHETS = "major_prophets"
    MINOR_PROPHETS = "minor_prophets"
    GOSPELS = "gospels"
    ACTS = "acts"
    EPISTLES = "epistles"
    APOCALYPTIC = "apocalyptic"


@dataclass
class Book:
    """Represents a book of the Bible with metadata."""

    name: str
    abbreviation: str
    testament: Testament
    genre: Genre
    chapters: int
    chapter_verses: List[int]  # Verses per chapter
    total_verses: int
    total_words: int
    author: Optional[str] = None
    themes: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Validate book data after initialization."""
        if len(self.chapter_verses) != self.chapters:
            raise ValueError(
                f"Book {self.name}: chapter_verses length ({len(self.chapter_verses)}) "
                f"does not match chapters count ({self.chapters})"
            )
        
        calculated_verses = sum(self.chapter_verses)
        if calculated_verses != self.total_verses:
            raise ValueError(
                f"Book {self.name}: sum of chapter_verses ({calculated_verses}) "
                f"does not match total_verses ({self.total_verses})"
            )

    def get_verses_in_range(self, start_chapter: int, end_chapter: int) -> int:
        """Calculate total verses in a chapter range.
        
        Args:
            start_chapter: Starting chapter (1-indexed)
            end_chapter: Ending chapter (1-indexed, inclusive)
            
        Returns:
            Total number of verses in the range
        """
        if start_chapter < 1 or end_chapter > self.chapters:
            raise ValueError(
                f"Invalid chapter range for {self.name}: {start_chapter}-{end_chapter}"
            )
        if start_chapter > end_chapter:
            raise ValueError(
                f"Start chapter ({start_chapter}) cannot be greater than end chapter ({end_chapter})"
            )
        
        # Convert to 0-indexed for list access
        return sum(self.chapter_verses[start_chapter - 1 : end_chapter])

    def get_word_count_in_range(self, start_chapter: int, end_chapter: int) -> int:
        """Estimate word count for a chapter range.
        
        Args:
            start_chapter: Starting chapter (1-indexed)
            end_chapter: Ending chapter (1-indexed, inclusive)
            
        Returns:
            Estimated word count for the range
        """
        verses = self.get_verses_in_range(start_chapter, end_chapter)
        words_per_verse = self.total_words / self.total_verses
        return int(verses * words_per_verse)
