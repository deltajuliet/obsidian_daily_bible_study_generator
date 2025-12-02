"""Bible data management."""

import json
import math
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from ..models.book import Book, Genre, Testament


class BibleScope(Enum):
    """Bible scope enumeration."""

    COMPLETE = "complete"
    OLD_TESTAMENT = "old_testament"
    NEW_TESTAMENT = "new_testament"


class BibleDataManager:
    """Manages Bible structure data and provides access to book information."""

    def __init__(self, data_dir: Optional[Path] = None, words_per_minute: int = 200):
        """Initialize the Bible data manager.

        Args:
            data_dir: Directory containing Bible data files. If None, uses default location.
            words_per_minute: Reading speed for time estimation (default: 200)
        """
        if data_dir is None:
            # Default to data directory in project root
            data_dir = Path(__file__).parent.parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.words_per_minute = words_per_minute
        self._books: Dict[str, Book] = {}
        self._load_bible_data()

    def _load_bible_data(self) -> None:
        """Load Bible structure data from JSON files."""
        # Load Old Testament books
        ot_file = self.data_dir / "old_testament_books.json"
        if not ot_file.exists():
            raise FileNotFoundError(f"Old Testament data file not found: {ot_file}")

        with open(ot_file, "r", encoding="utf-8") as f:
            ot_data = json.load(f)

        # Load New Testament books
        nt_file = self.data_dir / "new_testament_books.json"
        if not nt_file.exists():
            raise FileNotFoundError(f"New Testament data file not found: {nt_file}")

        with open(nt_file, "r", encoding="utf-8") as f:
            nt_data = json.load(f)

        # Parse and store books
        for book_data in ot_data + nt_data:
            book = Book(
                name=book_data["name"],
                abbreviation=book_data["abbreviation"],
                testament=Testament(book_data["testament"]),
                genre=Genre(book_data["genre"]),
                chapters=book_data["chapters"],
                chapter_verses=book_data["chapter_verses"],
                total_verses=book_data["total_verses"],
                total_words=book_data["total_words"],
                author=book_data.get("author"),
                themes=book_data.get("themes"),
            )
            self._books[book.name] = book

    def get_book(self, name: str) -> Book:
        """Get a book by name.

        Args:
            name: Book name

        Returns:
            Book object

        Raises:
            KeyError: If book not found
        """
        if name not in self._books:
            raise KeyError(f"Book not found: {name}")
        return self._books[name]

    def get_books(self, scope: BibleScope = BibleScope.COMPLETE) -> List[Book]:
        """Get all books for the specified scope in canonical order.

        Args:
            scope: Bible scope (complete, old_testament, new_testament)

        Returns:
            List of Book objects
        """
        all_books = list(self._books.values())

        if scope == BibleScope.OLD_TESTAMENT:
            return [b for b in all_books if b.testament == Testament.OLD]
        elif scope == BibleScope.NEW_TESTAMENT:
            return [b for b in all_books if b.testament == Testament.NEW]
        else:  # COMPLETE
            return all_books

    def get_chapter_count(self, scope: BibleScope = BibleScope.COMPLETE) -> int:
        """Get total chapter count for the specified scope.

        Args:
            scope: Bible scope

        Returns:
            Total number of chapters
        """
        books = self.get_books(scope)
        return sum(book.chapters for book in books)

    def get_verse_count(self, scope: BibleScope = BibleScope.COMPLETE) -> int:
        """Get total verse count for the specified scope.

        Args:
            scope: Bible scope

        Returns:
            Total number of verses
        """
        books = self.get_books(scope)
        return sum(book.total_verses for book in books)

    def get_word_count(self, scope: BibleScope = BibleScope.COMPLETE) -> int:
        """Get total word count for the specified scope.

        Args:
            scope: Bible scope

        Returns:
            Total number of words
        """
        books = self.get_books(scope)
        return sum(book.total_words for book in books)

    def calculate_reading_time(
        self, book_name: str, start_chapter: int, end_chapter: int
    ) -> int:
        """Calculate estimated reading time in minutes.

        Args:
            book_name: Name of the book
            start_chapter: Starting chapter (1-indexed)
            end_chapter: Ending chapter (1-indexed, inclusive)

        Returns:
            Estimated reading time in minutes
        """
        book = self.get_book(book_name)
        word_count = book.get_word_count_in_range(start_chapter, end_chapter)
        return math.ceil(word_count / self.words_per_minute)

    def get_books_by_testament(self, testament: Testament) -> List[Book]:
        """Get all books from a specific testament.

        Args:
            testament: Testament enum value

        Returns:
            List of Book objects
        """
        return [book for book in self._books.values() if book.testament == testament]

    def get_books_by_genre(self, genre: Genre) -> List[Book]:
        """Get all books from a specific genre.

        Args:
            genre: Genre enum value

        Returns:
            List of Book objects
        """
        return [book for book in self._books.values() if book.genre == genre]

    def get_scope_statistics(self, scope: BibleScope) -> Dict[str, any]:
        """Get statistics for a specific scope.

        Args:
            scope: Bible scope

        Returns:
            Dictionary with statistics
        """
        books = self.get_books(scope)
        total_chapters = sum(book.chapters for book in books)
        total_verses = sum(book.total_verses for book in books)
        total_words = sum(book.total_words for book in books)
        estimated_hours = round(total_words / self.words_per_minute / 60, 1)

        return {
            "scope": scope.value,
            "books": len(books),
            "chapters": total_chapters,
            "verses": total_verses,
            "words": total_words,
            "estimated_hours": estimated_hours,
            "average_chapters_per_day_365": round(total_chapters / 365, 2),
        }

    def get_all_book_names(self, scope: BibleScope = BibleScope.COMPLETE) -> List[str]:
        """Get list of all book names for the specified scope.

        Args:
            scope: Bible scope

        Returns:
            List of book names
        """
        books = self.get_books(scope)
        return [book.name for book in books]
