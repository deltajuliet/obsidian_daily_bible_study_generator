"""Command-line interface for Bible study planner."""

import sys
from datetime import date, datetime
from pathlib import Path

import click

from .bible.data_manager import BibleDataManager, BibleScope
from .plans.canonical import CanonicalPlan
from .models.study_day import StudyDay


@click.group()
@click.version_option(version="1.0.0")
def main() -> None:
    """Bible Study Planner - Generate daily Bible reading plans for Obsidian."""
    pass


@main.command()
@click.option(
    "--start-date",
    type=str,
    default=None,
    help="Starting date for the reading plan (YYYY-MM-DD format)",
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
    year: int | None,
    scope: str,
    days: int | None,
    output: Path,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Generate a Bible reading plan."""
    
    # Resolve start date with validation
    try:
        resolved_start_date = _resolve_start_date(start_date, year)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    
    # Map scope string to BibleScope enum
    scope_map = {
        "complete": BibleScope.COMPLETE,
        "ot": BibleScope.OLD_TESTAMENT,
        "nt": BibleScope.NEW_TESTAMENT,
    }
    bible_scope = scope_map[scope.lower()]
    
    # Set default days based on scope if not specified
    if days is None:
        default_days = {
            BibleScope.COMPLETE: 365,
            BibleScope.OLD_TESTAMENT: 270,
            BibleScope.NEW_TESTAMENT: 90,
        }
        days = default_days[bible_scope]
    
    click.echo(f"📖 Bible Study Planner")
    click.echo(f"   Start Date: {resolved_start_date}")
    click.echo(f"   Scope: {scope.upper()}")
    click.echo(f"   Days: {days}")
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
        click.echo(f"   Avg Chapters/Day: {stats['chapters'] / days:.2f}")
        click.echo()
        
        # Generate reading plan
        if verbose:
            click.echo("Generating reading plan...")
        
        plan = CanonicalPlan(bible_data)
        schedule = plan.generate_schedule(resolved_start_date, days, bible_scope)
        
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
            
            # Generate files (simplified for now)
            files_created = 0
            for day in schedule:
                filename = f"{day.date.strftime('%Y-%m-%d')}-day-{day.day_number:03d}.md"
                filepath = output / filename
                
                # Generate simple markdown content
                content = _generate_simple_markdown(day)
                
                filepath.write_text(content, encoding="utf-8")
                files_created += 1
            
            click.echo(f"✅ Created {files_created} markdown files")
            click.echo(f"📁 Output directory: {output.absolute()}")
            click.echo()
            click.echo("🎉 Bible study plan generated successfully!")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            raise
        sys.exit(1)


def _generate_simple_markdown(day: StudyDay) -> str:
    """Generate simple markdown content for a study day.
    
    Args:
        day: StudyDay object
        
    Returns:
        Markdown content as string
    """
    # Build frontmatter
    segments = day.reading_segments
    tags = day.get_tags(["bible-study", "daily"])
    
    content = "---\n"
    content += f"date: {day.date.strftime('%Y-%m-%d')}\n"
    content += f"day: {day.day_number}\n"
    content += f"tags: {tags}\n"
    content += f"testament: {day.primary_testament}\n"
    content += f"genre: {day.primary_genre}\n"
    content += f"book: {day.primary_book}\n"
    
    # Handle chapters field
    if len(segments) == 1:
        content += f'chapters: "{segments[0].chapter_range_str}"\n'
    else:
        chapters_list = [seg.chapter_range_str for seg in segments]
        content += f'chapters: {chapters_list}\n'
    
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


if __name__ == "__main__":
    main()
