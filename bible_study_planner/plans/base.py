"""Base reading plan strategy."""

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List

from ..bible.data_manager import BibleDataManager, BibleScope
from ..models.study_day import StudyDay


class ReadingPlanStrategy(ABC):
    """Abstract base class for reading plan strategies."""

    def __init__(self, bible_data: BibleDataManager):
        """Initialize the reading plan strategy.

        Args:
            bible_data: Bible data manager instance
        """
        self.bible_data = bible_data

    @abstractmethod
    def generate_schedule(
        self, year: int, days: int, scope: BibleScope
    ) -> List[StudyDay]:
        """Generate complete reading schedule.

        Args:
            year: Year for the reading plan
            days: Number of days in the plan
            scope: Bible scope (complete, old_testament, new_testament)

        Returns:
            List of StudyDay objects with reading assignments
        """
        pass

    def validate_schedule(self, schedule: List[StudyDay]) -> bool:
        """Validate generated schedule meets requirements.

        Args:
            schedule: List of study days to validate

        Returns:
            True if schedule is valid, False otherwise
        """
        if not schedule:
            return False

        # Check day numbering is sequential
        for i, day in enumerate(schedule, start=1):
            if day.day_number != i:
                return False

        # Check dates are sequential
        for i in range(len(schedule) - 1):
            expected_next_date = schedule[i].date + timedelta(days=1)
            if schedule[i + 1].date != expected_next_date:
                return False

        return True

    def _generate_dates(self, year: int, days: int) -> List[date]:
        """Generate sequential dates starting from January 1st.

        Args:
            year: Year to generate dates for
            days: Number of days to generate

        Returns:
            List of date objects
        """
        start_date = date(year, 1, 1)
        return [start_date + timedelta(days=i) for i in range(days)]
