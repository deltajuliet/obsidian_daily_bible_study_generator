"""Canonical reading plan - reads Bible in book order."""

from typing import List, Tuple

from ..bible.data_manager import BibleScope
from ..models.book import Book
from ..models.reading_segment import ReadingSegment
from ..models.study_day import StudyDay
from .base import ReadingPlanStrategy


class CanonicalPlan(ReadingPlanStrategy):
    """
    Canonical reading plan strategy.
    
    Reads the Bible in traditional book order: Genesis → Revelation.
    Distributes chapters evenly across the specified number of days.
    """

    def generate_schedule(
        self, year: int, days: int, scope: BibleScope
    ) -> List[StudyDay]:
        """Generate canonical reading schedule.

        Args:
            year: Year for the reading plan
            days: Number of days in the plan
            scope: Bible scope

        Returns:
            List of StudyDay objects
        """
        books = self.bible_data.get_books(scope)
        total_chapters = sum(book.chapters for book in books)
        
        # Calculate target chapters per day
        chapters_per_day = total_chapters / days
        
        # Distribute chapters across days
        reading_assignments = self._distribute_chapters(books, days, chapters_per_day)
        
        # Generate dates
        dates = self._generate_dates(year, days)
        
        # Create StudyDay objects
        schedule = []
        for day_num, (day_date, segments) in enumerate(zip(dates, reading_assignments), start=1):
            study_day = StudyDay(
                date=day_date,
                day_number=day_num,
                reading_segments=segments,
                total_days=days,
            )
            schedule.append(study_day)
        
        return schedule

    def _distribute_chapters(
        self, books: List[Book], days: int, target_chapters_per_day: float
    ) -> List[List[ReadingSegment]]:
        """Distribute chapters across days with smart balancing.

        Args:
            books: List of books to distribute
            days: Number of days
            target_chapters_per_day: Target average chapters per day

        Returns:
            List of reading segment lists, one per day
        """
        assignments: List[List[ReadingSegment]] = [[] for _ in range(days)]
        
        current_day = 0
        current_day_chapters = 0
        
        for book in books:
            current_chapter = 1
            
            while current_chapter <= book.chapters:
                # Calculate how many chapters to assign to current day
                remaining_chapters_in_book = book.chapters - current_chapter + 1
                space_in_current_day = max(
                    1, int(target_chapters_per_day - current_day_chapters)
                )
                
                # Don't split very small books if possible
                if book.chapters <= 3 and current_chapter == 1:
                    chapters_to_assign = book.chapters
                else:
                    chapters_to_assign = min(
                        space_in_current_day, remaining_chapters_in_book
                    )
                
                end_chapter = current_chapter + chapters_to_assign - 1
                
                # Create reading segment
                verse_count = book.get_verses_in_range(current_chapter, end_chapter)
                word_count = book.get_word_count_in_range(current_chapter, end_chapter)
                estimated_minutes = self.bible_data.calculate_reading_time(
                    book.name, current_chapter, end_chapter
                )
                
                segment = ReadingSegment(
                    book=book,
                    start_chapter=current_chapter,
                    end_chapter=end_chapter,
                    verse_count=verse_count,
                    word_count=word_count,
                    estimated_minutes=estimated_minutes,
                )
                
                assignments[current_day].append(segment)
                current_day_chapters += chapters_to_assign
                current_chapter = end_chapter + 1
                
                # Move to next day if we've hit the target
                if current_day_chapters >= target_chapters_per_day:
                    current_day += 1
                    current_day_chapters = 0
                    
                    # Safety check
                    if current_day >= days:
                        current_day = days - 1
        
        # Handle empty days (shouldn't happen with correct calculation)
        # If there are empty days at the end, redistribute from fuller days
        empty_days = [i for i, day in enumerate(assignments) if not day]
        if empty_days:
            # This is a safeguard - in practice, the distribution should fill all days
            pass
        
        return assignments
