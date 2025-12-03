"""Command-line interface for Bible study planner."""

import sys
from datetime import date, datetime
from pathlib import Path

import click

from .bible.data_manager import BibleDataManager, BibleScope
from .plans.canonical import CanonicalPlan
from .models.study_day import StudyDay


@click.group()
@click.version_option(version="1.3.0")
def main() -> None:
    """Bible Study Planner - Generate daily Bible reading plans for Obsidian.

    Create structured, customizable Bible reading schedules as Markdown files
    optimized for the Obsidian note-taking application. Features include:

    • Multiple scopes (Complete Bible, Old Testament, New Testament)
    • Flexible start dates and date ranges
    • Rich metadata and Dataview integration
    • Multiple concurrent plans with unique IDs
    • Automatic time estimates and progress tracking

    Examples:

      # Start reading today (365-day complete Bible plan)
      bible-study-planner generate

      # New Testament in 90 days starting today
      bible-study-planner generate --scope nt --days 90

      # Custom date range (Q1 2025)
      bible-study-planner generate --start-date 2025-01-01 --end-date 2025-03-31

    For more help on a specific command, use:
      bible-study-planner COMMAND --help
    """
    pass


@main.command()
@click.option(
    "--start-date",
    type=str,
    default=None,
    help="Starting date for the reading plan (YYYY-MM-DD format)",
)
@click.option(
    "--end-date",
    type=str,
    default=None,
    help="Ending date for the reading plan (YYYY-MM-DD format). Auto-calculates days.",
)
@click.option(
    "--year",
    type=int,
    default=None,
    help="[DEPRECATED] Use --start-date instead. Target year (defaults to Jan 1)",
)
@click.option(
    "--scope",
    type=click.Choice(["complete", "ot", "nt"], case_sensitive=False),
    default="complete",
    help="Bible scope: complete, ot (Old Testament), or nt (New Testament)",
    show_default=True,
)
@click.option(
    "--days",
    type=int,
    default=None,
    help="Number of days (default: 365 for complete, 270 for OT, 90 for NT)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="./bible-study",
    help="Output directory for generated files",
    show_default=True,
)
@click.option(
    "--plan-name",
    type=str,
    default=None,
    help="Human-readable plan name (auto-generated if not provided)",
)
@click.option(
    "--plan-id",
    type=str,
    default=None,
    help="Unique plan identifier (auto-generated if not provided)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview the plan without generating files",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Verbose output",
)
def generate(
    start_date: str | None,
    end_date: str | None,
    year: int | None,
    scope: str,
    days: int | None,
    output: Path,
    plan_name: str | None,
    plan_id: str | None,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Generate a Bible reading plan with rich metadata for Obsidian.

    Creates daily study notes with frontmatter, reading segments, and a dashboard
    index file with embedded Dataview queries for progress tracking.

    \b
    COMMON EXAMPLES:
      Start reading the complete Bible today (365 days):
        $ bible-study-planner generate

      New Testament in 90 days:
        $ bible-study-planner generate --scope nt --days 90

      Specify a date range (automatically calculates days):
        $ bible-study-planner generate --start-date 2025-01-01 --end-date 2025-12-31

      Old Testament starting on a specific date:
        $ bible-study-planner generate --start-date 2025-06-15 --scope ot

      Preview before generating:
        $ bible-study-planner generate --scope nt --dry-run

      Create multiple concurrent plans:
        $ bible-study-planner generate --plan-name "Personal 2025" --plan-id "personal-2025"
        $ bible-study-planner generate --plan-name "Family NT" --plan-id "family-nt" --scope nt

      Custom output directory:
        $ bible-study-planner generate --output ~/Documents/Obsidian/BibleStudy

    \b
    OUTPUT:
      Generates two types of files:
      1. Plan Index: _plan-index-{plan-id}.md with progress dashboard
      2. Daily Notes: {date}-day-{num}.md with readings and reflection prompts

    \b
    SCOPES:
      complete - Full Bible (66 books, 1,189 chapters, ~365 days default)
      ot       - Old Testament (39 books, 929 chapters, ~270 days default)
      nt       - New Testament (27 books, 260 chapters, ~90 days default)

    \b
    DATE OPTIONS:
      --start-date  Starting date (default: today)
      --end-date    Ending date (auto-calculates number of days)
      --days        Explicit day count (overridden by --end-date)

    If neither --end-date nor --days is specified, uses scope-based defaults.
    """
    
    # Map scope string to BibleScope enum (needed for day resolution)
    scope_map = {
        "complete": BibleScope.COMPLETE,
        "ot": BibleScope.OLD_TESTAMENT,
        "nt": BibleScope.NEW_TESTAMENT,
    }
    bible_scope = scope_map[scope.lower()]
    
    # Resolve start date with validation
    try:
        resolved_start_date = _resolve_start_date(start_date, year)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    
    # Resolve days (considering end_date)
    try:
        resolved_days = _resolve_days(resolved_start_date, end_date, days, bible_scope)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    
    # Generate plan name and ID
    resolved_plan_name = _generate_plan_name(plan_name, scope, resolved_start_date)
    resolved_plan_id = _generate_plan_id(plan_id, scope, resolved_start_date)
    
    click.echo(f"📖 Bible Study Planner")
    click.echo(f"   Plan Name: {resolved_plan_name}")
    click.echo(f"   Plan ID: {resolved_plan_id}")
    click.echo(f"   Start Date: {resolved_start_date}")
    click.echo(f"   Scope: {scope.upper()}")
    click.echo(f"   Days: {resolved_days}")
    click.echo(f"   Output: {output}")
    click.echo()
    
    try:
        # Initialize Bible data manager
        if verbose:
            click.echo("Loading Bible data...")
        bible_data = BibleDataManager()
        
        # Get scope statistics
        stats = bible_data.get_scope_statistics(bible_scope)
        click.echo(f"📊 Scope Statistics:")
        click.echo(f"   Books: {stats['books']}")
        click.echo(f"   Chapters: {stats['chapters']}")
        click.echo(f"   Verses: {stats['verses']}")
        click.echo(f"   Est. Hours: {stats['estimated_hours']}h")
        click.echo(f"   Avg Chapters/Day: {stats['chapters'] / resolved_days:.2f}")
        click.echo()
        
        # Generate reading plan
        if verbose:
            click.echo("Generating reading plan...")
        
        plan = CanonicalPlan(bible_data)
        schedule = plan.generate_schedule(resolved_start_date, resolved_days, bible_scope)
        
        # Validate schedule
        if not plan.validate_schedule(schedule):
            click.echo("❌ Error: Generated schedule failed validation", err=True)
            sys.exit(1)
        
        click.echo(f"✅ Generated {len(schedule)} study days")
        click.echo()
        
        if dry_run:
            click.echo("🔍 Dry Run - Preview of first 5 days:")
            click.echo()
            for day in schedule[:5]:
                click.echo(f"Day {day.day_number} ({day.date}):")
                for segment in day.reading_segments:
                    click.echo(f"  • {segment}")
                click.echo(f"  📊 {day.total_chapters} chapters, {day.total_verses} verses, ~{day.total_minutes} min")
                click.echo()
            click.echo(f"... and {len(schedule) - 5} more days")
            click.echo()
            click.echo("✨ To generate files, remove the --dry-run flag")
        else:
            # Create output directory
            output.mkdir(parents=True, exist_ok=True)
            
            if verbose:
                click.echo(f"Writing files to {output}...")
            
            # Generate plan index file
            if verbose:
                click.echo("Generating plan index...")
            
            plan_index_content = _generate_plan_index(
                plan_name=resolved_plan_name,
                plan_id=resolved_plan_id,
                scope=scope,
                start_date=resolved_start_date,
                end_date=schedule[-1].date if schedule else resolved_start_date,
                total_days=resolved_days,
                stats=stats
            )
            
            # Write plan index to parent directory
            plan_index_filename = f"_plan-index-{resolved_plan_id}.md"
            plan_index_path = output.parent / plan_index_filename
            plan_index_path.write_text(plan_index_content, encoding="utf-8")
            
            # Generate daily note files
            files_created = 0
            for day in schedule:
                filename = f"{day.date.strftime('%Y-%m-%d')}-day-{day.day_number:03d}.md"
                filepath = output / filename
                
                # Generate markdown content with plan_id
                content = _generate_simple_markdown(day, resolved_plan_id)
                
                filepath.write_text(content, encoding="utf-8")
                files_created += 1
            
            click.echo(f"✅ Created {files_created} markdown files")
            click.echo(f"✅ Created plan index: {plan_index_path.name}")
            click.echo(f"📁 Output directory: {output.absolute()}")
            click.echo()
            click.echo("🎉 Bible study plan generated successfully!")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            raise
        sys.exit(1)


def _generate_simple_markdown(day: StudyDay, plan_id: str) -> str:
    """Generate simple markdown content for a study day.
    
    Args:
        day: StudyDay object
        plan_id: Unique plan identifier
        
    Returns:
        Markdown content as string
    """
    # Build frontmatter
    segments = day.reading_segments
    tags = day.get_tags(["bible-study", "daily"])
    all_books = day.get_all_books()
    
    content = "---\n"
    content += f"date: {day.date.strftime('%Y-%m-%d')}\n"
    content += f"day: {day.day_number}\n"
    content += f"plan_id: {plan_id}\n"
    content += f"tags: {tags}\n"
    content += f"testament: {day.primary_testament}\n"
    content += f"genre: {day.primary_genre}\n"
    content += f"books: {all_books}\n"
    
    # Handle chapters field - use structured format for multi-book days
    if len(segments) == 1:
        content += f'chapters: "{segments[0].chapter_range_str}"\n'
    else:
        content += "chapters:\n"
        for chapter_info in day.get_structured_chapters():
            content += f"  - book: {chapter_info['book']}\n"
            content += f"    range: \"{chapter_info['range']}\"\n"
    
    content += f"estimated_minutes: {day.total_minutes}\n"
    content += f"verse_count: {day.total_verses}\n"
    content += f"word_count: {day.total_words}\n"
    content += "status: pending\n"
    content += "---\n\n"
    
    # Build body
    content += f"# Day {day.day_number}: {day.date.strftime('%A, %B %d, %Y')}\n\n"
    
    content += "## 📖 Today's Reading\n\n"
    for segment in segments:
        content += f"**{segment.book.name} {segment.chapter_range_str}**\n\n"
    
    content += f"- 📊 {day.total_verses} verses\n"
    content += f"- 📝 ~{day.total_words} words\n"
    content += f"- ⏱️ {day.total_minutes} minutes\n\n"
    
    content += "---\n\n"
    content += "## 📝 Notes & Observations\n\n"
    content += "*What did you notice in today's reading?*\n\n"
    content += "\n\n"
    
    content += "---\n\n"
    content += "## 💭 Reflection\n\n"
    content += "### Key Themes\n\n\n"
    content += "### Questions\n\n\n"
    content += "### Personal Application\n\n\n"
    
    content += "---\n\n"
    content += "## 🙏 Prayer\n\n\n"
    
    content += "---\n\n"
    content += "## 📊 Metadata\n\n"
    content += f"**Testament**: {day.primary_testament.title()}  \n"
    content += f"**Genre**: {day.primary_genre.replace('_', ' ').title()}  \n"
    content += f"**Progress**: Day {day.day_number} of {day.total_days} ({day.progress_percentage}%)\n"
    
    return content


def _resolve_start_date(start_date_str: str | None, year: int | None) -> date:
    """Resolve the start date from user input with validation.
    
    Args:
        start_date_str: Start date string in YYYY-MM-DD format (optional)
        year: Year for backward compatibility (optional)
        
    Returns:
        Resolved date object
        
    Raises:
        ValueError: If date is invalid or out of acceptable range
    """
    # Case 1: --start-date provided
    if start_date_str:
        if year:
            click.echo("⚠️  Warning: Both --start-date and --year provided. Using --start-date.")
        
        try:
            parsed_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid date format: '{start_date_str}'. Expected YYYY-MM-DD format."
            )
        
        # Validate date is not too far in the past or future
        _validate_date_range(parsed_date)
        
        return parsed_date
    
    # Case 2: --year provided (backward compatibility)
    if year:
        click.echo("⚠️  Note: --year is deprecated. Use --start-date for more flexibility.")
        parsed_date = date(year, 1, 1)
        _validate_date_range(parsed_date)
        return parsed_date
    
    # Case 3: Neither provided - default to today
    return date.today()


def _validate_date_range(check_date: date) -> None:
    """Validate that date is within acceptable range.
    
    Args:
        check_date: Date to validate
        
    Raises:
        ValueError: If date is out of acceptable range
    """
    min_date = date(1900, 1, 1)
    max_date = date.today().replace(year=date.today().year + 10)
    
    if check_date < min_date:
        raise ValueError(
            f"Start date cannot be before {min_date.strftime('%Y-%m-%d')}"
        )
    
    if check_date > max_date:
        raise ValueError(
            f"Start date cannot be more than 10 years in the future "
            f"(max: {max_date.strftime('%Y-%m-%d')})"
        )


def _generate_plan_name(custom_name: str | None, scope: str, start_date: date) -> str:
    """Generate a human-readable plan name.
    
    Args:
        custom_name: Custom plan name if provided
        scope: Bible scope (complete, ot, nt)
        start_date: Plan start date
        
    Returns:
        Generated or custom plan name
    """
    if custom_name:
        return custom_name
    
    # Auto-generate based on scope and year
    scope_names = {
        "complete": "Complete Bible",
        "ot": "Old Testament",
        "nt": "New Testament"
    }
    
    scope_label = scope_names.get(scope.lower(), "Bible")
    year = start_date.year
    
    return f"{scope_label} {year}"


def _generate_plan_id(custom_id: str | None, scope: str, start_date: date) -> str:
    """Generate a unique plan identifier.
    
    Args:
        custom_id: Custom plan ID if provided
        scope: Bible scope (complete, ot, nt)
        start_date: Plan start date
        
    Returns:
        Generated or custom plan ID (lowercase, hyphenated)
    """
    if custom_id:
        # Sanitize custom ID
        return custom_id.lower().replace(" ", "-").replace("_", "-")
    
    # Auto-generate: {scope}-{year}-canonical
    year = start_date.year
    return f"{scope.lower()}-{year}-canonical"


def _generate_plan_index(
    plan_name: str,
    plan_id: str,
    scope: str,
    start_date: date,
    end_date: date,
    total_days: int,
    stats: dict
) -> str:
    """Generate plan index file with DataView queries.
    
    Args:
        plan_name: Human-readable plan name
        plan_id: Unique plan identifier
        scope: Bible scope (complete, ot, nt)
        start_date: Plan start date
        end_date: Plan end date
        total_days: Total days in plan
        stats: Scope statistics dictionary
        
    Returns:
        Markdown content for plan index file
    """
    created_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    scope_display = {
        "complete": "Complete Bible (66 books)",
        "ot": "Old Testament",
        "nt": "New Testament"
    }.get(scope.lower(), scope.upper())
    
    content = f"""---
type: bible-study-plan-index
plan_id: {plan_id}
plan_name: "{plan_name}"
plan_strategy: canonical
plan_scope: {scope.lower()}
plan_start_date: {start_date.strftime('%Y-%m-%d')}
plan_end_date: {end_date.strftime('%Y-%m-%d')}
plan_total_days: {total_days}
plan_created: {created_timestamp}
plan_status: active
tags: [bible-study, plan-index, {start_date.year}]
---

# 📖 {plan_name}

**Reading Plan Index & Dashboard**

## Plan Details

| Property | Value |
|----------|-------|
| **Plan ID** | `{plan_id}` |
| **Strategy** | Canonical (Book Order) |
| **Scope** | {scope_display} |
| **Duration** | {total_days} days |
| **Start Date** | {start_date.strftime('%B %d, %Y')} |
| **End Date** | {end_date.strftime('%B %d, %Y')} |
| **Status** | Active |
| **Created** | {datetime.now().strftime('%Y-%m-%d')} |

## 📊 Progress Dashboard

### Overall Progress

```dataview
TABLE WITHOUT ID
  length(rows) as "Days Completed",
  ({total_days} - length(rows)) as "Days Remaining",
  round((length(rows) / {total_days}) * 100, 1) + "%" as "Progress",
  sum(rows.verse_count) as "Verses Read",
  round(sum(rows.estimated_minutes) / 60, 1) + "h" as "Time Invested"
FROM ""
WHERE plan_id = "{plan_id}" AND status = "completed"
GROUP BY "Progress Summary"
```

### Upcoming Readings

```dataview
TABLE WITHOUT ID
  file.link as "Day",
  date as "Date",
  books as "Books",
  verse_count as "Verses"
WHERE plan_id = "{plan_id}" AND status = "pending"
SORT date ASC
LIMIT 7
```

### Reading Pace (Last 7 Days)

```dataview
TABLE WITHOUT ID
  file.link as "Day",
  books as "Books",
  verse_count as "Verses",
  estimated_minutes + " min" as "Time",
  status as "Status"
WHERE plan_id = "{plan_id}"
  AND date >= date(today) - dur(7 days)
  AND date <= date(today)
SORT date DESC
LIMIT 7
```

### Books Completed

```dataview
TABLE WITHOUT ID
  book as "Book",
  length(rows.file) as "Days",
  sum(rows.verse_count) as "Verses"
WHERE plan_id = "{plan_id}" AND status = "completed"
FLATTEN books as book
GROUP BY book
SORT book ASC
```

### Testament Progress

```dataview
TABLE WITHOUT ID
  testament as "Testament",
  length(rows.file) as "Days Completed",
  sum(rows.verse_count) as "Verses Read",
  round(sum(rows.estimated_minutes) / 60, 1) + "h" as "Time"
WHERE plan_id = "{plan_id}" AND status = "completed"
GROUP BY testament
```

### Missed Days

```dataview
LIST
WHERE plan_id = "{plan_id}" 
  AND status = "pending" 
  AND date < date(today)
SORT date ASC
```

## 📚 All Readings

```dataview
TABLE
  day as "Day #",
  date as "Date",
  books as "Books",
  verse_count as "Verses",
  status as "Status"
WHERE plan_id = "{plan_id}"
SORT date ASC
```

## 📈 Plan Statistics

- **Total Books**: {stats['books']}
- **Total Chapters**: {stats['chapters']}
- **Total Verses**: {stats['verses']}
- **Estimated Hours**: {stats['estimated_hours']}h
- **Avg Chapters/Day**: {stats['chapters'] / total_days:.1f}

## Notes

*Use this space to track overall plan insights, goals, or modifications*

---

**Generated by**: Bible Study Planner v1.3
"""
    
    return content


def _resolve_days(
    start_date: date,
    end_date_str: str | None,
    days: int | None,
    scope: BibleScope,
) -> int:
    """Resolve the number of days for the plan.
    
    Args:
        start_date: Resolved start date
        end_date_str: Optional end date string
        days: Optional explicit days count
        scope: Bible scope for default days
        
    Returns:
        Number of days for the plan
        
    Raises:
        ValueError: If dates are invalid or conflicting
    """
    # Case 1: --end-date provided
    if end_date_str:
        if days:
            click.echo(
                "⚠️  Warning: Both --end-date and --days provided. "
                "Using --end-date (ignoring --days)."
            )
        
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid end date format: '{end_date_str}'. "
                "Expected YYYY-MM-DD format."
            )
        
        # Validate end date
        _validate_date_range(end_date)
        
        # Calculate days (inclusive)
        calculated_days = (end_date - start_date).days + 1
        
        if calculated_days < 1:
            raise ValueError(
                f"End date ({end_date}) must be after start date ({start_date})"
            )
        
        if calculated_days > 3650:  # ~10 years
            raise ValueError(
                f"Date range too long ({calculated_days} days). "
                f"Maximum is 3650 days (~10 years)"
            )
        
        # Warn for extreme durations
        if calculated_days < 7:
            click.echo(
                f"⚠️  Note: Short duration ({calculated_days} days) may result in "
                "heavy daily reading load."
            )
        
        return calculated_days
    
    # Case 2: --days provided
    if days:
        return days
    
    # Case 3: Use scope defaults
    default_days = {
        BibleScope.COMPLETE: 365,
        BibleScope.OLD_TESTAMENT: 270,
        BibleScope.NEW_TESTAMENT: 90,
    }
    return default_days[scope]


if __name__ == "__main__":
    main()
