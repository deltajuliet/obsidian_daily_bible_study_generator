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
        # Calculate total verses and target per day
        total_verses = sum(book.total_verses for book in books)
        target_verses_per_day = total_verses / days
        
        # Build assignments day by day, maintaining canonical order
        assignments: List[List[ReadingSegment]] = []
        current_day_segments: List[ReadingSegment] = []
        current_day_verses = 0
        total_verses_assigned = 0
        
        # Track position in Bible
        book_index = 0
        chapter_index = 1
        
        while book_index < len(books):
            book = books[book_index]
            
            # Determine how many chapters to read in this segment
            # Start with a single chapter
            start_chapter = chapter_index
            end_chapter = start_chapter
            
            # Calculate verses for this chapter
            segment_verses = book.get_verses_in_range(start_chapter, end_chapter)
            
            # Try to extend the segment if we haven't reached target yet
            # and there are more chapters in this book
            while (end_chapter < book.chapters and 
                   current_day_verses + segment_verses < target_verses_per_day):
                # Check if adding the next chapter would overshoot too much
                next_chapter_verses = book.get_verses_in_range(end_chapter + 1, end_chapter + 1)
                potential_total = current_day_verses + segment_verses + next_chapter_verses
                
                # Add next chapter if it doesn't overshoot too badly
                # or if we're still under target
                if potential_total <= target_verses_per_day * 1.2:  # Allow 20% overshoot
                    end_chapter += 1
                    segment_verses = book.get_verses_in_range(start_chapter, end_chapter)
                else:
                    break
            
            # For very small books (3 chapters or less), read entire book
            if book.chapters <= 3 and start_chapter == 1:
                end_chapter = book.chapters
                segment_verses = book.get_verses_in_range(start_chapter, end_chapter)
            
            # Create the segment
            verse_count = book.get_verses_in_range(start_chapter, end_chapter)
            word_count = book.get_word_count_in_range(start_chapter, end_chapter)
            estimated_minutes = self.bible_data.calculate_reading_time(
                book.name, start_chapter, end_chapter
            )
            
            segment = ReadingSegment(
                book=book,
                start_chapter=start_chapter,
                end_chapter=end_chapter,
                verse_count=verse_count,
                word_count=word_count,
                estimated_minutes=estimated_minutes,
            )
            
            # Add segment to current day
            current_day_segments.append(segment)
            current_day_verses += verse_count
            
            # Move to next position
            if end_chapter >= book.chapters:
                # Finished this book, move to next
                book_index += 1
                chapter_index = 1
            else:
                # More chapters in this book
                chapter_index = end_chapter + 1
            
            # Check if we should move to the next day
            days_completed = len(assignments)
            days_remaining = days - days_completed - 1  # -1 for current day being built
            verses_remaining = total_verses - total_verses_assigned - current_day_verses
            
            if days_remaining > 0:
                # Calculate ideal verses for current day based on remaining content
                ideal_verses_for_today = verses_remaining / (days_remaining + 1)  # +1 includes current day
                
                # Move to next day if current day has met or slightly exceeded ideal
                # Use a small tolerance (5%) to avoid being too strict
                if current_day_verses >= ideal_verses_for_today * 0.95:
                    assignments.append(current_day_segments)
                    total_verses_assigned += current_day_verses
                    current_day_segments = []
                    current_day_verses = 0
            elif days_remaining == 0 and book_index < len(books):
                # This is the last day, keep adding everything remaining
                pass
        
        # Add the last day's segments
        if current_day_segments:
            assignments.append(current_day_segments)
        
        return assignments
