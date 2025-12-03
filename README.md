# Obsidian Daily Bible Study Generator

A Python-based tool that generates daily Bible study plans as Markdown files optimized for the Obsidian note-taking application. Create structured, customizable reading schedules with rich metadata for tracking progress and integrating with Obsidian's ecosystem.

## Features

- 📖 **Multiple Scopes**: Generate plans for the complete Bible, Old Testament only, or New Testament only
- 📅 **Flexible Start Date**: Start your plan on any date (default: today) - no need to wait for January 1st
- 🗓️ **Date Range Support**: Specify start and end dates, or use number of days
- 📊 **Rich Metadata**: Each daily note includes frontmatter with tags, reading statistics, and Dataview-compatible fields
- 📈 **Plan Index Dashboard**: Auto-generated index file with embedded Dataview queries for progress tracking
- 🎯 **Multiple Concurrent Plans**: Create and manage multiple reading plans simultaneously with unique plan IDs
- ⏱️ **Time Estimates**: Automatic calculation of estimated reading time based on word count
- 🔖 **Obsidian Optimized**: Designed specifically for Obsidian with proper formatting and linking support
- 📚 **Enhanced Book Tracking**: Support for multi-book days with structured metadata

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/deltajuliet/obsidian_daily_bible_study_generator.git
cd obsidian_daily_bible_study_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package (development mode):
```bash
pip install -e .
```

## Usage

### Basic Usage

Generate a complete Bible reading plan starting today:

```bash
bible-study-planner generate
```

Or run directly as a Python module:

```bash
python -m bible_study_planner generate
```

### Command Options

```bash
bible-study-planner generate [OPTIONS]
```

**Options:**

- `--start-date DATE` - Starting date for the reading plan in YYYY-MM-DD format (default: today)
- `--end-date DATE` - Ending date for the reading plan in YYYY-MM-DD format (auto-calculates days)
- `--year INTEGER` - **[DEPRECATED]** Target year (use `--start-date` instead)
- `--scope [complete|ot|nt]` - Bible scope to use:
  - `complete` - Full Bible (66 books, 1,189 chapters)
  - `ot` - Old Testament only (39 books, 929 chapters)
  - `nt` - New Testament only (27 books, 260 chapters)
- `--days INTEGER` - Number of days in the plan (ignored if `--end-date` provided)
- `--output PATH` - Output directory for generated files (default: `./bible-study`)
- `--plan-name TEXT` - Human-readable plan name (auto-generated if not provided)
- `--plan-id TEXT` - Unique plan identifier (auto-generated if not provided)
- `--dry-run` - Preview the plan without generating files
- `-v, --verbose` - Enable verbose output
- `--help` - Show help message

### Examples

**Start reading today (complete Bible in 365 days):**
```bash
bible-study-planner generate
```

**Start on a specific date:**
```bash
bible-study-planner generate --start-date 2025-03-15 --scope nt --days 90
```

**Specify date range (automatically calculates days):**
```bash
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-03-31 --scope nt
# Creates a 90-day plan for Q1 2025
```

**Plan until end of year:**
```bash
bible-study-planner generate --end-date 2025-12-31 --scope complete
# Starts today and runs until December 31st
```

**Create multiple concurrent plans:**
```bash
# Personal complete Bible plan
bible-study-planner generate --plan-name "Personal 2025" --plan-id "personal-2025" --scope complete

# Family devotional plan
bible-study-planner generate --plan-name "Family NT Study" --plan-id "family-nt-2025" --scope nt --output ./family-devotional
```

**New Testament in 90 days starting today:**
```bash
bible-study-planner generate --scope nt --days 90
```

**Old Testament starting on your birthday:**
```bash
bible-study-planner generate --start-date 2025-06-15 --scope ot
```

**Custom output directory:**
```bash
bible-study-planner generate --output ~/Documents/Obsidian/BibleStudy
```

**Preview without generating files:**
```bash
bible-study-planner generate --scope nt --dry-run
```

**Legacy format (still supported, but deprecated):**
```bash
bible-study-planner generate --year 2025 --scope nt
```

## Generated Files

### Plan Index File

Each plan generates a master index file (`_plan-index-{plan-id}.md`) in the parent directory containing:

**Plan Index Frontmatter:**
```yaml
---
type: bible-study-plan-index
plan_id: complete-2025-canonical
plan_name: "Complete Bible 2025"
plan_strategy: canonical
plan_scope: complete
plan_start_date: 2025-01-01
plan_end_date: 2025-12-31
plan_total_days: 365
plan_created: 2025-12-02T14:41:55
plan_status: active
tags: [bible-study, plan-index, 2025]
---
```

**Plan Index Content:**
- Plan details table
- Live progress dashboard with embedded Dataview queries:
  - Overall progress percentage
  - Days completed vs. remaining
  - Reading pace (last 7 days)
  - Books and testaments completed
  - Upcoming readings
  - Missed days
- Complete reading list with links to all daily notes
- Plan statistics (books, chapters, verses, estimated hours)

### Daily Note Format

Each daily note includes:

#### Single-Book Day Frontmatter
```yaml
---
date: 2025-01-01
day: 1
plan_id: complete-2025-canonical
tags: [bible-study, daily, old, law]
testament: old
genre: law
books: [Genesis]
chapters: "1-3"
estimated_minutes: 12
verse_count: 80
word_count: 2000
status: pending
---
```

#### Multi-Book Day Frontmatter
```yaml
---
date: 2025-03-17
day: 76
plan_id: nt-2025-canonical
tags: [bible-study, daily, new, gospels]
testament: new
genre: gospels
books: [Luke, John, Acts]
chapters:
  - book: Luke
    range: "1-24"
  - book: John
    range: "1-21"
  - book: Acts
    range: "1-28"
estimated_minutes: 722
verse_count: 6208
word_count: 141695
status: pending
---
```

#### Content Sections

1. **Today's Reading** - Book and chapter information with statistics
2. **Notes & Observations** - Space for personal notes
3. **Reflection** - Guided reflection with key themes, questions, and application
4. **Prayer** - Space for prayer notes
5. **Metadata** - Progress tracking and testament/genre information

## Obsidian Integration

The generated files are fully compatible with Obsidian and include:

- **Plan Index Dashboard** - Central hub with live progress tracking via Dataview queries
- **Frontmatter metadata** for Dataview queries
- **Unique Plan IDs** - Easily manage multiple concurrent reading plans
- **Tags** for organization and filtering
- **Progress tracking** with status field (pending/in-progress/completed)
- **Reading statistics** for planning and motivation
- **Multi-book support** with structured chapter information

### Plan Index Dashboard

Open the `_plan-index-{plan-id}.md` file in your Obsidian vault to see:

- **Progress percentage** and completion stats
- **Books completed** across the plan
- **Testament progress** breakdown
- **Upcoming readings** for the next 7 days
- **Missed days** that need attention
- **Reading pace** for the last 7 days

All queries update automatically as you mark daily notes as completed!

### Custom Dataview Queries

**Find all notes for a specific plan:**
```dataview
TABLE day, date, books, status
FROM "bible-study"
WHERE plan_id = "complete-2025-canonical"
SORT date ASC
```

**List completed readings:**
```dataview
TABLE books, chapters, estimated_minutes
FROM "bible-study"
WHERE status = "completed"
SORT date ASC
```

**Show progress by testament:**
```dataview
TABLE length(rows) as "Days", sum(rows.verse_count) as "Verses"
FROM "bible-study"
GROUP BY testament
```

**Find all days reading a specific book:**
```dataview
TABLE day, date, status
FROM "bible-study"
WHERE contains(books, "Romans")
SORT date ASC
```

**Compare multiple plans:**
```dataview
TABLE 
  plan_id as "Plan",
  length(rows) as "Total Days",
  length(filter(rows, (r) => r.status = "completed")) as "Completed",
  sum(rows.verse_count) as "Total Verses"
FROM "bible-study"
GROUP BY plan_id
```

## Project Structure

```
obsidian_daily_bible_study_generator/
├── bible_study_planner/     # Main package
│   ├── models/              # Data models
│   ├── bible/               # Bible data management
│   ├── plans/               # Reading plan strategies
│   ├── cli.py              # Command-line interface
│   └── __main__.py         # Entry point
├── data/                    # Bible structure data
│   ├── bible_metadata.json
│   ├── old_testament_books.json
│   └── new_testament_books.json
├── ADRs/                    # Architecture Decision Records
│   ├── ADR-001-bible-study-planner-architecture.md
│   ├── ADR-002-flexible-start-date.md
│   ├── ADR-003-end-date-option.md
│   └── ADR-004-enhanced-dataview-properties.md
├── test-output/            # Folder for testing file outputs
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

### Generated Output Structure

```
Bible-Study/
├── _plan-index-complete-2025-canonical.md    # Plan dashboard
├── 2025-complete/                             # Daily notes folder
│   ├── 2025-01-01-day-001.md
│   ├── 2025-01-02-day-002.md
│   └── ...
├── _plan-index-family-nt-2025.md             # Another plan
└── family-devotional/                         # Another plan's notes
    ├── 2025-03-01-day-001.md
    └── ...
```

## Bible Data

The tool includes complete Bible structure data with:

- **All 66 books** (39 OT, 27 NT)
- **Chapter and verse counts** for accurate distribution
- **Word counts** for reading time estimates
- **Genre classification** (Law, History, Wisdom, Prophets, Gospels, Epistles, Apocalyptic)
- **Testament designation** for filtering and organization

## Development

### Running Tests

Use the `./test-output` folder for all output testing

```bash
pytest
```

### Code Formatting

```bash
black bible_study_planner/
```

### Type Checking

```bash
mypy bible_study_planner/
```

## Architecture

This project follows a modular architecture with:

- **Strategy Pattern** for different reading plan types (canonical, chronological, etc.)
- **Data Models** for type-safe Bible structure representation
- **Separation of Concerns** between data management, plan generation, and output

See [ADR-001](ADRs/ADR-001-bible-study-planner-architecture.md) for detailed architectural decisions.

## Roadmap

### Current Features (v1.3)
- ✅ Canonical reading plan (book order)
- ✅ Multiple scope support (complete/OT/NT)
- ✅ Flexible start dates (start any day, not just Jan 1)
- ✅ End date option (specify date ranges)
- ✅ Plan index with dashboard (live progress tracking)
- ✅ Multiple concurrent plans (unique plan IDs)
- ✅ Enhanced metadata (books array, structured chapters)
- ✅ Markdown generation with frontmatter
- ✅ Reading time estimates
- ✅ CLI interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**deltajuliet**

## Acknowledgments

- Bible structure data based on standard Bible organization
- Word count estimates based on ESV translation
- Designed for use with [Obsidian](https://obsidian.md/) note-taking app
- Compatible with [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) plugin

## Support

For issues, questions, or suggestions, please [open an issue](https://github.com/deltajuliet/obsidian_daily_bible_study_generator/issues) on GitHub.

---

*May this tool help you engage deeply with Scripture and grow in your faith journey! 📖✨*
