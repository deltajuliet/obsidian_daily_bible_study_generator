# ADR-006: Custom Study Plans

**Status**: Proposed
**Date**: 2025-12-03
**Decision Makers**: Development Team
**Supersedes**: N/A
**Related to**: ADR-001 (Bible Study Planner Architecture)

---

## Context

The Bible Study Planner currently supports only canonical order reading (Genesis → Revelation) through the `CanonicalPlan` strategy. While this traditional approach is valuable, users have diverse study needs that require alternative reading orders and book selections.

### User Study Patterns

**Chronological Reading**:
- Read books in the order events occurred historically
- Example: Job before Genesis 12, Chronicles parallel with Kings
- Popular for understanding biblical narrative flow

**Thematic Studies**:
- Focus on specific topics or genres (e.g., "Wisdom Literature", "Paul's Prison Epistles")
- Read books grouped by theme rather than canonical order
- Example: Study all prophets addressing exile, or all gospels in parallel

**Custom Curricula**:
- Church reading plans spanning specific books
- Academic courses with curated selections
- Discipleship programs with intentional progression
- Personal study plans focusing on particular testaments, authors, or periods

### Current Limitations

The existing `CanonicalPlan` implementation hardcodes several assumptions:

```python
# canonical.py, lines 62-167
def _distribute_chapters(self, books: List[Book], days: int) -> List[StudyDay]:
    """Distribute chapters across days in canonical order."""
    # Iterates through books sequentially as provided by BibleDataManager
    # No way to reorder, skip, or repeat books
    # No configuration for custom selections
```

**Problems**:
1. **No Reordering**: Books must follow canonical sequence
2. **All-or-Nothing Scope**: Can only select Complete Bible, OT, or NT - no subsets
3. **No Custom Groupings**: Cannot group related books (e.g., Pentateuch, Major Prophets)
4. **Inflexible**: Adding new reading patterns requires code changes
5. **No Book Repetition**: Cannot revisit books or chapters in a single plan

### Use Cases

**Use Case 1: Chronological Bible in One Year**
```
Read Bible in historical order:
- Job (pre-patriarchal)
- Genesis 1-11 (primeval history)
- Genesis 12-50 (patriarchs)
- Job 32-37 (Elihu speeches)
- Exodus through Deuteronomy
- Joshua, Judges, Ruth
- 1-2 Samuel with Psalms interspersed
- etc.
```

**Use Case 2: Gospels + Acts Study (90 Days)**
```
Focus on Jesus' life and early church:
- Matthew (28 chapters)
- Mark (16 chapters)
- Luke (24 chapters)
- John (21 chapters)
- Acts (28 chapters)
Total: 117 chapters over 90 days
```

**Use Case 3: Wisdom Literature Deep Dive**
```
Study poetic and wisdom books:
- Job (42 chapters)
- Psalms (150 chapters)
- Proverbs (31 chapters)
- Ecclesiastes (12 chapters)
- Song of Solomon (8 chapters)
```

**Use Case 4: Paul's Letters in Chronological Order**
```
Read Paul's epistles by date written:
1. Galatians (AD 48-49)
2. 1 Thessalonians (AD 50-51)
3. 2 Thessalonians (AD 51-52)
4. 1 Corinthians (AD 53-55)
5. 2 Corinthians (AD 55-56)
6. Romans (AD 55-58)
7. Ephesians, Philippians, Colossians, Philemon (AD 60-62)
8. 1 Timothy, Titus (AD 62-64)
9. 2 Timothy (AD 67)
```

---

## Decision

We will implement a **custom study plan system** that allows users to specify arbitrary book orders, selections, and groupings through configuration files. This system will:

1. **Extend the Strategy Pattern**: Add `CustomPlan` strategy alongside existing `CanonicalPlan`
2. **Configuration-Driven**: Use YAML/JSON files to define book order and selections
3. **Reusable Plans**: Ship with common plans (chronological, thematic) and allow user-defined plans
4. **CLI Integration**: Add `--plan-file` option to specify custom plan configuration
5. **Backward Compatible**: Existing canonical, OT, NT scopes remain unchanged

### High-Level Approach

**Architecture**:
```
User → CLI (--plan-file custom.yaml)
         ↓
    Plan Configuration Loader
         ↓
    CustomPlan Strategy ← Plan Config (book order, selections)
         ↓
    Chapter Distribution Algorithm
         ↓
    StudyDay Generation
```

**Plan Configuration Format**:
```yaml
# plans/chronological_one_year.yaml
plan:
  name: "Chronological Bible Reading"
  description: "Read the Bible in the order events occurred"
  type: "custom"

books:
  - book: "Job"
    chapters: [1, 2, 3, 4, 5]  # First Job chapters (pre-patriarchal)

  - book: "Genesis"
    chapters: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

  - book: "Job"
    chapters: [6, 7, 8, 9, 10]  # Continue Job narrative

  - book: "Genesis"
    chapters: [12, 13, 14, 15, 16, 17, 18, 19, 20]

  # ... continue with all books in chronological order

distribution:
  target_chapters_per_day: 3.3
  allow_book_splitting: true  # Can split a book across multiple days
  balance_load: true          # Use smart distribution algorithm
```

---

## Proposed Changes

### 1. Custom Plan Configuration Schema

**File Format**: YAML (human-readable, supports comments)

**Full Schema**:
```yaml
# Plan metadata
plan:
  name: "My Custom Reading Plan"
  description: "Description of this plan's purpose"
  type: "custom"  # custom, chronological, thematic
  version: "1.0"
  author: "Your Name"

# Book selection and ordering
books:
  # Option 1: Simple book list (all chapters)
  - book: "Matthew"

  # Option 2: Specific chapter range
  - book: "Psalms"
    chapters: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  # Option 3: Chapter ranges (shorthand)
  - book: "Genesis"
    chapters: "1-11"  # Parsed as [1, 2, 3, ..., 11]

  # Option 4: Multiple ranges
  - book: "Isaiah"
    chapters: "1-12, 40-55"  # Selected chapters only

  # Option 5: All chapters (explicit)
  - book: "Romans"
    chapters: "all"  # or omit chapters field

# Distribution settings (optional)
distribution:
  target_chapters_per_day: 3.3   # Average chapters per day
  min_chapters_per_day: 1        # Minimum (for small books)
  max_chapters_per_day: 6        # Maximum (avoid overload)
  allow_book_splitting: true     # Can a single book span multiple days?
  small_book_threshold: 3        # Books with ≤ N chapters read together
  balance_load: true             # Use verse-based balancing algorithm

# Metadata (optional, for tagging/grouping)
metadata:
  tags: ["chronological", "one-year"]
  themes: ["narrative", "historical"]
  difficulty: "intermediate"
  recommended_pace: "daily"
```

**Simplified Format (Quick Plans)**:
```yaml
# Simple plan: just book order
plan:
  name: "Gospels Only"

books:
  - Matthew
  - Mark
  - Luke
  - John
```

### 2. CustomPlan Strategy Class

**New File**: `bible_study_planner/plans/custom.py`

```python
from pathlib import Path
from typing import List
from datetime import date

import yaml

from bible_study_planner.models.book import Book
from bible_study_planner.models.study_day import StudyDay
from bible_study_planner.plans.base import ReadingPlanStrategy
from bible_study_planner.bible.data_manager import BibleDataManager


class CustomPlan(ReadingPlanStrategy):
    """
    Custom reading plan strategy that reads book order from configuration file.

    Supports:
    - Arbitrary book ordering
    - Specific chapter selections
    - Book repetition (same book multiple times)
    - Flexible chapter ranges
    """

    def __init__(self, plan_config_path: Path):
        """
        Initialize with path to plan configuration YAML file.

        Args:
            plan_config_path: Path to YAML configuration file
        """
        self.config_path = plan_config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> dict:
        """Load and parse YAML configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Plan configuration not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config or "books" not in config:
            raise ValueError(f"Invalid plan config: missing 'books' section")

        return config

    def _validate_config(self) -> None:
        """Validate configuration structure."""
        # Check required fields
        if "plan" not in self.config or "name" not in self.config["plan"]:
            raise ValueError("Plan config must include 'plan.name'")

        # Validate book entries
        for idx, book_entry in enumerate(self.config["books"]):
            if isinstance(book_entry, str):
                continue  # Simple format: just book name

            if not isinstance(book_entry, dict) or "book" not in book_entry:
                raise ValueError(f"Invalid book entry at index {idx}")

    def generate_schedule(
        self,
        start_date: date,
        days: int,
        bible_data: BibleDataManager,
    ) -> List[StudyDay]:
        """
        Generate reading schedule based on custom plan configuration.

        Args:
            start_date: Starting date for the plan
            days: Number of days in the plan
            bible_data: Bible data manager for book metadata

        Returns:
            List of StudyDay objects
        """
        # Parse book selections from config
        book_selections = self._parse_book_selections(bible_data)

        # Get distribution settings
        dist_config = self.config.get("distribution", {})
        target_chapters = dist_config.get("target_chapters_per_day", None)
        balance_load = dist_config.get("balance_load", True)

        # Calculate target chapters if not specified
        if target_chapters is None:
            total_chapters = sum(len(chapters) for _, chapters in book_selections)
            target_chapters = total_chapters / days

        # Distribute chapters across days
        if balance_load:
            schedule = self._distribute_chapters_balanced(
                book_selections, days, start_date, dist_config
            )
        else:
            schedule = self._distribute_chapters_simple(
                book_selections, days, start_date, target_chapters
            )

        return schedule

    def _parse_book_selections(
        self, bible_data: BibleDataManager
    ) -> List[tuple[Book, List[int]]]:
        """
        Parse book entries from config into (Book, chapters) tuples.

        Returns:
            List of (Book object, list of chapter numbers)
        """
        selections = []
        all_books = bible_data.get_books(scope=None)  # Get all books
        book_lookup = {book.name: book for book in all_books}

        for entry in self.config["books"]:
            # Handle simple format (just book name string)
            if isinstance(entry, str):
                book_name = entry
                chapters = "all"
            else:
                book_name = entry["book"]
                chapters = entry.get("chapters", "all")

            # Look up book
            if book_name not in book_lookup:
                raise ValueError(f"Unknown book: {book_name}")

            book = book_lookup[book_name]

            # Parse chapter selection
            if chapters == "all" or chapters is None:
                chapter_list = list(range(1, book.chapters + 1))
            elif isinstance(chapters, list):
                chapter_list = chapters
            elif isinstance(chapters, str):
                chapter_list = self._parse_chapter_string(chapters)
            else:
                raise ValueError(f"Invalid chapters format for {book_name}")

            # Validate chapter numbers
            invalid_chapters = [c for c in chapter_list if c < 1 or c > book.chapters]
            if invalid_chapters:
                raise ValueError(
                    f"Invalid chapters for {book_name}: {invalid_chapters}. "
                    f"Valid range: 1-{book.chapters}"
                )

            selections.append((book, chapter_list))

        return selections

    def _parse_chapter_string(self, chapter_str: str) -> List[int]:
        """
        Parse chapter string like "1-11" or "1-5, 10-15" into list.

        Args:
            chapter_str: String like "1-11" or "1-5, 10-15"

        Returns:
            List of chapter numbers
        """
        chapters = []

        # Split by comma for multiple ranges
        ranges = chapter_str.split(",")

        for range_str in ranges:
            range_str = range_str.strip()

            if "-" in range_str:
                # Parse range "1-11"
                start, end = range_str.split("-")
                start, end = int(start.strip()), int(end.strip())
                chapters.extend(range(start, end + 1))
            else:
                # Single chapter
                chapters.append(int(range_str))

        return sorted(set(chapters))  # Remove duplicates and sort

    def _distribute_chapters_balanced(
        self,
        book_selections: List[tuple[Book, List[int]]],
        days: int,
        start_date: date,
        dist_config: dict,
    ) -> List[StudyDay]:
        """
        Distribute chapters with verse-based balancing (similar to CanonicalPlan).

        Uses smart distribution to balance reading load based on verse counts.
        """
        # Reuse the balanced distribution logic from CanonicalPlan
        # This would call the same algorithm but with custom book order
        from bible_study_planner.plans.canonical import CanonicalPlan

        # Create temporary CanonicalPlan instance to reuse distribution logic
        canonical = CanonicalPlan()

        # Flatten book selections into a simple book list for distribution
        # The CanonicalPlan algorithm works with any ordered book list
        schedule = canonical._distribute_chapters_from_selections(
            book_selections, days, start_date
        )

        return schedule

    def _distribute_chapters_simple(
        self,
        book_selections: List[tuple[Book, List[int]]],
        days: int,
        start_date: date,
        target_chapters: float,
    ) -> List[StudyDay]:
        """
        Simple distribution: divide chapters evenly across days.

        Does not use verse-based balancing.
        """
        from datetime import timedelta
        from bible_study_planner.models.reading_segment import ReadingSegment

        schedule = []
        current_day = 0
        current_date = start_date

        # Flatten all chapters with their books
        all_chapter_items = []
        for book, chapters in book_selections:
            for chapter in chapters:
                all_chapter_items.append((book, chapter))

        # Simple approach: distribute target_chapters per day
        idx = 0
        while current_day < days and idx < len(all_chapter_items):
            day_segments = []
            chapters_today = 0

            # Add chapters until we hit target
            while idx < len(all_chapter_items) and chapters_today < target_chapters:
                book, chapter = all_chapter_items[idx]

                # Create reading segment (single chapter)
                segment = ReadingSegment(
                    book=book,
                    start_chapter=chapter,
                    end_chapter=chapter,
                )
                day_segments.append(segment)

                chapters_today += 1
                idx += 1

            # Create study day
            study_day = StudyDay(
                date=current_date,
                day_number=current_day + 1,
                total_days=days,
                reading_segments=day_segments,
            )
            schedule.append(study_day)

            current_day += 1
            current_date += timedelta(days=1)

        return schedule

    def get_plan_name(self) -> str:
        """Return the plan name from configuration."""
        return self.config.get("plan", {}).get("name", "Custom Plan")

    def get_plan_description(self) -> str:
        """Return the plan description from configuration."""
        return self.config.get("plan", {}).get("description", "")
```

### 3. Pre-built Plan Library

**New Directory**: `plans/` (at repository root)

Ship with common reading plans:

```
plans/
  ├── README.md                          # Plan library documentation
  ├── chronological_one_year.yaml        # Bible in historical order (365 days)
  ├── chronological_90_days.yaml         # Accelerated chronological
  ├── gospels_acts.yaml                  # Jesus + Early Church (90 days)
  ├── wisdom_literature.yaml             # Job, Psalms, Proverbs, etc.
  ├── pauline_epistles_chronological.yaml # Paul's letters by date
  ├── prophets_thematic.yaml             # Prophets grouped by theme
  ├── new_testament_letters.yaml         # All NT letters
  └── pentateuch.yaml                    # First 5 books
```

**Example Plan** (`plans/chronological_one_year.yaml`):
```yaml
plan:
  name: "Chronological Bible Reading (One Year)"
  description: "Read the Bible in the order events occurred historically"
  type: "chronological"
  author: "Bible Study Planner"
  version: "1.0"

books:
  - book: "Job"
    chapters: "1-21"

  - book: "Genesis"
    chapters: "1-11"

  - book: "Job"
    chapters: "22-31"

  - book: "Genesis"
    chapters: "12-50"

  - book: "Job"
    chapters: "32-42"

  - book: "Exodus"
  - book: "Leviticus"
  - book: "Numbers"
  - book: "Deuteronomy"
  - book: "Joshua"
  - book: "Judges"
  - book: "Ruth"
  # ... continue with full chronological order ...

distribution:
  target_chapters_per_day: 3.3
  balance_load: true
```

### 4. CLI Updates

**Add New Options**:
```python
# cli.py

@click.option(
    "--plan-type",
    type=click.Choice(["canonical", "custom"], case_sensitive=False),
    default="canonical",
    help="Type of reading plan (default: canonical)",
)
@click.option(
    "--plan-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to custom plan YAML file (required when --plan-type=custom)",
)
@click.option(
    "--list-plans",
    is_flag=True,
    help="List available pre-built plans and exit",
)
def generate(
    # ... existing params ...
    plan_type: str,
    plan_file: Path | None,
    list_plans: bool,
) -> None:
    """Generate a Bible reading plan."""

    # Handle --list-plans flag
    if list_plans:
        _display_available_plans()
        return

    # Validate plan-type and plan-file combination
    if plan_type == "custom" and plan_file is None:
        raise click.UsageError(
            "--plan-file is required when using --plan-type=custom"
        )

    # ... existing code ...

    # Select plan strategy
    if plan_type == "canonical":
        plan_strategy = CanonicalPlan()
    else:  # custom
        plan_strategy = CustomPlan(plan_file)

    # ... rest of generation logic ...
```

**List Plans Command**:
```python
def _display_available_plans() -> None:
    """Display available pre-built plans."""
    plans_dir = Path(__file__).parent.parent / "plans"

    if not plans_dir.exists():
        click.echo("No pre-built plans found.")
        return

    click.echo("Available Pre-built Plans:\n")

    for plan_file in sorted(plans_dir.glob("*.yaml")):
        # Load plan to get metadata
        with open(plan_file, "r") as f:
            config = yaml.safe_load(f)

        plan_info = config.get("plan", {})
        name = plan_info.get("name", plan_file.stem)
        description = plan_info.get("description", "No description")

        click.echo(f"  {plan_file.name}")
        click.echo(f"    Name: {name}")
        click.echo(f"    Description: {description}")
        click.echo()

    click.echo(f"Use with: --plan-type custom --plan-file plans/<filename>")
```

---

## Design Considerations

### 1. Configuration vs. Code

**Decision**: Use YAML configuration files, not Python code

**Rationale**:
- **Accessibility**: Non-programmers can create plans
- **Shareability**: Plans are portable files, easy to share
- **Version Control**: YAML files work well in git
- **Safety**: No code execution risks
- **Validation**: Can validate YAML structure before execution

### 2. Chapter Selection Granularity

**Decision**: Support individual chapter selection, not verse ranges

**Rationale**:
- Current architecture works at chapter-level (StudyDay → ReadingSegment → Chapters)
- Verse-level would require significant refactoring
- Chapter-level is sufficient for most use cases
- Verse selection can be a future enhancement

### 3. Distribution Algorithm Reuse

**Decision**: Reuse CanonicalPlan's balanced distribution algorithm

**Rationale**:
- Algorithm is well-tested and proven
- Works with any ordered book list
- Verse-based balancing provides consistent reading times
- Avoids code duplication

**Implementation**:
```python
# Refactor CanonicalPlan to expose distribution method
class CanonicalPlan(ReadingPlanStrategy):
    def _distribute_chapters_from_selections(
        self,
        book_selections: List[tuple[Book, List[int]]],
        days: int,
        start_date: date
    ) -> List[StudyDay]:
        """
        Distribute chapters using balanced algorithm.

        Extracted from _distribute_chapters to allow reuse by CustomPlan.
        """
        # Existing balanced distribution logic...
```

### 4. Plan Library Management

**Decision**: Include common plans in repository, document custom creation

**Rationale**:
- Lowers barrier to entry (users can start with pre-built plans)
- Demonstrates configuration format
- Community can contribute plans via PRs
- Users can modify existing plans as starting point

### 5. Error Handling

**Decision**: Fail fast with clear error messages during config validation

**Validation Checks**:
- Plan file exists and is valid YAML
- All referenced books exist in Bible data
- Chapter ranges are valid for each book
- Total chapters can fit in specified days

**Error Messages**:
```bash
# Invalid book name
Error: Unknown book 'Jonha' in plan config
       Did you mean 'Jonah'?

# Invalid chapter range
Error: Invalid chapters for Philemon: [1, 2, 3, 4, 5]
       Philemon only has 1 chapter.

# Impossible distribution
Error: Plan contains 1,189 chapters but only 30 days specified.
       Minimum recommended: 240 days (5 chapters/day average)
```

---

## Implementation Plan

### Phase 1: Core Custom Plan Support (v1.5)

**Tasks**:
1. Create `CustomPlan` class in `plans/custom.py`
2. Implement YAML configuration loading and validation
3. Implement chapter string parsing (`"1-11"`, `"1-5, 10-15"`)
4. Refactor `CanonicalPlan` to expose distribution algorithm
5. Connect `CustomPlan` to distribution algorithm
6. Add `--plan-type` and `--plan-file` CLI options
7. Add `--list-plans` command
8. Unit tests for config parsing and validation
9. Integration test with sample custom plan

**Deliverables**:
- Working custom plan system
- Documentation for creating custom plans
- Basic error handling

### Phase 2: Pre-built Plan Library (v1.6)

**Tasks**:
1. Create `plans/` directory structure
2. Author pre-built plans:
   - Chronological Bible (365 days)
   - Chronological Bible (90 days)
   - Gospels + Acts
   - Wisdom Literature
   - Pauline Epistles (chronological)
3. Create plan library README with descriptions
4. Add validation script for all plans
5. Update user documentation with plan examples

**Deliverables**:
- 5-7 high-quality pre-built plans
- Plan creation guide
- Plan validation tooling

### Phase 3: Enhanced Features (v1.7+)

**Future Enhancements**:
1. **Plan Validation Command**: `bible-study-planner validate-plan <file>`
2. **Plan Statistics**: Show chapter count, estimated days before generation
3. **Plan Conversion**: Convert canonical scope to custom YAML
4. **Plan Merging**: Combine multiple plans
5. **Web UI**: Visual plan builder/editor
6. **Community Plans**: Repository of user-submitted plans

---

## Usage Examples

### Example 1: Using Pre-built Chronological Plan

```bash
# List available plans
bible-study-planner generate --list-plans

# Generate chronological reading plan
bible-study-planner generate \
  --start-date 2025-01-01 \
  --days 365 \
  --plan-type custom \
  --plan-file plans/chronological_one_year.yaml \
  --output "Bible2025-Chronological"
```

### Example 2: Gospels + Acts Study

```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --days 90 \
  --plan-type custom \
  --plan-file plans/gospels_acts.yaml \
  --plan-name "Gospels and Acts 2025"
```

### Example 3: Custom Plan (Psalms Every Week)

Create `my_custom_plan.yaml`:
```yaml
plan:
  name: "Weekly Psalm with NT Letters"
  description: "Read one Psalm each week alongside NT letters"

books:
  - book: "Psalms"
    chapters: [1]
  - book: "Romans"
    chapters: [1, 2, 3, 4, 5, 6, 7]

  - book: "Psalms"
    chapters: [2]
  - book: "Romans"
    chapters: [8, 9, 10, 11, 12, 13, 14, 15, 16]

  - book: "Psalms"
    chapters: [3]
  - book: "1 Corinthians"
    chapters: [1, 2, 3, 4, 5, 6, 7]

  # ... continue pattern ...

distribution:
  target_chapters_per_day: 3
  balance_load: true
```

Generate:
```bash
bible-study-planner generate \
  --start-date 2025-01-01 \
  --days 180 \
  --plan-type custom \
  --plan-file my_custom_plan.yaml \
  --output "CustomPlan2025"
```

### Example 4: Thematic Study - Exile and Return

Create `exile_and_return.yaml`:
```yaml
plan:
  name: "Exile and Return Study"
  description: "Study books addressing Israel's exile and restoration"

books:
  # Pre-exile warnings
  - book: "Isaiah"
    chapters: "1-39"
  - book: "Jeremiah"
    chapters: "1-29"

  # Exile
  - book: "Lamentations"
  - book: "Ezekiel"
  - book: "Daniel"

  # Post-exile hope
  - book: "Isaiah"
    chapters: "40-66"
  - book: "Jeremiah"
    chapters: "30-33"

  # Return and rebuilding
  - book: "Ezra"
  - book: "Nehemiah"
  - book: "Haggai"
  - book: "Zechariah"
  - book: "Malachi"

distribution:
  target_chapters_per_day: 3.5
  balance_load: true

metadata:
  themes: ["exile", "restoration", "hope", "judgment"]
  difficulty: "intermediate"
```

---

## Consequences

### Positive

1. **Flexibility**: Users can create any reading plan imaginable
2. **Reusability**: Plans are shareable files, not locked in code
3. **Accessibility**: Non-programmers can design plans using YAML
4. **Chronological Support**: Enables highly-requested chronological reading
5. **Thematic Studies**: Supports focused topic-based studies
6. **Educational**: Facilitates academic courses and discipleship programs
7. **Extensibility**: Easy to add new plan types without code changes
8. **Community**: Users can contribute plans to a shared library
9. **Backward Compatible**: Existing canonical functionality unchanged

### Negative

1. **Complexity**: Adds new configuration format to learn
2. **Validation Burden**: Must validate user-provided YAML files
3. **Error Messages**: Need clear errors for common config mistakes
4. **Documentation**: Requires comprehensive guides for plan creation
5. **Maintenance**: Pre-built plans need updates and community moderation
6. **Testing**: More test cases for various plan configurations

### Neutral

1. **Chapter-Level Granularity**: Limits flexibility but simplifies implementation
2. **YAML Format**: Some users prefer JSON or other formats
3. **File-Based**: Plans must be files, not inline CLI arguments

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Invalid YAML breaks generation | High | Comprehensive validation with clear error messages |
| Misspelled book names | Medium | Fuzzy matching suggestions ("Did you mean...?") |
| Impossible chapter distributions | Medium | Pre-validate total chapters vs. days before generation |
| Performance with complex plans | Low | Profile and optimize if needed; cache book lookups |
| Plan file not found | Medium | Check file existence before loading; suggest --list-plans |
| Version compatibility | Low | Include schema version in YAML; validate on load |

---

## Testing Strategy

### Unit Tests

1. **YAML Parsing**:
   - Valid YAML loads correctly
   - Invalid YAML raises clear errors
   - All supported chapter formats parse correctly

2. **Chapter String Parsing**:
   - `"1-11"` → `[1, 2, 3, ..., 11]`
   - `"1-5, 10-15"` → `[1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15]`
   - Invalid formats raise errors

3. **Book Selection Validation**:
   - Valid book names accepted
   - Invalid book names rejected with suggestions
   - Chapter ranges validated against book lengths

4. **Distribution Algorithm**:
   - CustomPlan produces valid StudyDay schedule
   - Chapter counts match configuration
   - Date ranges are correct

### Integration Tests

1. **Full Plan Generation**:
   - Generate plan with sample custom YAML
   - Verify all files created correctly
   - Check frontmatter and content

2. **Pre-built Plans**:
   - Each pre-built plan generates successfully
   - No missing books or invalid chapters
   - Distributions are balanced

3. **CLI Integration**:
   - `--plan-type custom --plan-file` works correctly
   - `--list-plans` displays available plans
   - Error handling for missing/invalid files

### Validation Tests

1. **Plan Consistency**:
   - All chapters referenced exist
   - No duplicate chapter assignments (unless intentional)
   - Total chapters can fit in specified days

2. **Pre-built Plan Quality**:
   - Chronological plan follows historical order
   - Thematic plans group related books
   - Distribution is reasonable (not 1 chapter/day then 20 chapter/day)

---

## Success Metrics

1. **Functionality**: Users can generate plans from custom YAML files
2. **Pre-built Plans**: Ship with 5+ high-quality plans
3. **Error Handling**: Clear, actionable error messages for config issues
4. **Documentation**: Comprehensive guide for creating custom plans
5. **Adoption**: Users create and share their own plans
6. **Community Contributions**: PRs with new plans submitted
7. **Feature Requests**: Requests for specific pre-built plans

---

## Future Enhancements

### Phase 4: Advanced Features (v2.0+)

1. **Verse-Level Granularity**: Support verse ranges within chapters
2. **Parallel Reading**: Read multiple books side-by-side
3. **Conditional Logic**: "If behind schedule, reduce chapters"
4. **Dependencies**: "Read Psalm 119 after Leviticus"
5. **Grouping**: Visual grouping in output (e.g., "Week 1: Creation")
6. **Plan Templates**: Parameterized plans (e.g., "N-day Gospels")
7. **Plan Inheritance**: Base one plan on another
8. **Interactive Builder**: Web UI for visual plan creation
9. **Import from Popular Plans**: Import plans from YouVersion, BibleGateway, etc.

---

## References

- [Chronological Bible Reading Plans](https://www.biblestudytools.com/bible-reading-plan/chronological.html)
- [Bible Reading Plan Examples](https://www.biblegateway.com/reading-plans/)
- [YAML Specification](https://yaml.org/spec/)
- ADR-001: Bible Study Planner Architecture (Strategy Pattern)
- [Obsidian YAML Frontmatter](https://help.obsidian.md/Editing+and+formatting/Properties)

---

## Approval

- [ ] Feature Specification Approved
- [ ] Implementation Plan Approved
- [ ] Pre-built Plan List Approved
- [ ] Documentation Requirements Approved
- [ ] Ready for Development

**Approved By**: _________________
**Date**: _________________

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-03 | 1.0 | Initial ADR for custom study plans | Development Team |
