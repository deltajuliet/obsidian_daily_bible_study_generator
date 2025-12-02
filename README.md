# Obsidian Daily Bible Study Generator

A Python-based tool that generates daily Bible study plans as Markdown files optimized for the Obsidian note-taking application. Create structured, customizable reading schedules with rich metadata for tracking progress and integrating with Obsidian's ecosystem.

## Features

- 📖 **Multiple Scopes**: Generate plans for the complete Bible, Old Testament only, or New Testament only
- 📅 **Flexible Duration**: Customize the number of days (default: 365 for complete Bible, 270 for OT, 90 for NT)
- 📊 **Rich Metadata**: Each daily note includes frontmatter with tags, reading statistics, and Dataview-compatible fields
- 🎯 **Progress Tracking**: Track your reading progress with built-in metadata fields
- ⏱️ **Time Estimates**: Automatic calculation of estimated reading time based on word count
- 🔖 **Obsidian Optimized**: Designed specifically for Obsidian with proper formatting and linking support

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

**Specify date range (e.g., first quarter of 2025):**
```bash
bible-study-planner generate --start-date 2025-01-01 --end-date 2025-03-31 --scope nt
```

**Plan until end of year:**
```bash
bible-study-planner generate --end-date 2025-12-31 --scope complete
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

## Generated File Format

Each daily note includes:

### Frontmatter (YAML)
```yaml
---
date: 2025-01-01
day: 1
tags: [bible-study, daily, old, law]
testament: old
genre: law
book: Genesis
chapters: "1-3"
estimated_minutes: 12
verse_count: 80
word_count: 2000
status: pending
---
```

### Content Sections

1. **Today's Reading** - Book and chapter information with statistics
2. **Notes & Observations** - Space for personal notes
3. **Reflection** - Guided reflection with key themes, questions, and application
4. **Prayer** - Space for prayer notes
5. **Metadata** - Progress tracking and testament/genre information

## Obsidian Integration

The generated files are fully compatible with Obsidian and include:

- **Frontmatter metadata** for Dataview queries
- **Tags** for organization and filtering
- **Progress tracking** with status field (pending/in-progress/completed)
- **Reading statistics** for planning and motivation

### Example Dataview Queries

List all completed readings:
```dataview
TABLE book, chapters, estimated_minutes
FROM "bible-study"
WHERE status = "completed"
SORT date ASC
```

Show progress by testament:
```dataview
TABLE length(rows) as "Days", sum(rows.verse_count) as "Verses"
FROM "bible-study"
GROUP BY testament
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
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
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

### Current Features (v1.0)
- ✅ Canonical reading plan (book order)
- ✅ Multiple scope support (complete/OT/NT)
- ✅ Markdown generation with frontmatter
- ✅ Reading time estimates
- ✅ CLI interface

### Planned Features
- 🔄 Chronological reading plan
- 🔄 Custom reading plans
- 🔄 Progress dashboard generation
- 🔄 Template customization
- 🔄 Multiple folder structures
- 🔄 Book index generation

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
