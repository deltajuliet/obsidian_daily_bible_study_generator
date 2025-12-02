"""Canonical reading plan - reads Bible in book order."""

from datetime import date
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
        self, start_date: date, days: int, scope: BibleScope
    ) -> List[StudyDay]:
        """Generate canonical reading schedule.

        Args:
            start_date: Starting date for the reading plan
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
        
        # Adjust total_days to match actual days used
        actual_days = len(reading_assignments)
        
        # Generate dates for actual days
        dates = self._generate_dates(start_date, actual_days)
        
        # Create StudyDay objects
        schedule = []
        for day_num, (day_date, segments) in enumerate(zip(dates, reading_assignments), start=1):
            study_day = StudyDay(
                date=day_date,
                day_number=day_num,
                reading_segments=segments,
                total_days=actual_days,
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
        # Create all segments first
        all_segments: List[ReadingSegment] = []
        
        for book in books:
            current_chapter = 1
            
            while current_chapter <= book.chapters:
                # Determine chapters to read in this segment
                # Use target as a guide, but be flexible
                chapters_to_assign = min(
                    max(1, round(target_chapters_per_day)),
                    book.chapters - current_chapter + 1
                )
                
                # Don't split very small books
                if book.chapters <= 3 and current_chapter == 1:
                    chapters_to_assign = book.chapters
                
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
                
                all_segments.append(segment)
                current_chapter = end_chapter + 1
        
        # Now distribute segments across days
        # Try to balance the load evenly
        assignments: List[List[ReadingSegment]] = [[] for _ in range(days)]
        
        current_day = 0
        for segment in all_segments:
            if current_day >= days:
                # If we've run out of days, add to the last day
                current_day = days - 1
            
            assignments[current_day].append(segment)
            
            # Move to next day after adding segment
            # This ensures segments are spread across all days
            current_day += 1
        
        # Remove any empty days at the end
        assignments = [day for day in assignments if day]
        
        return assignments
