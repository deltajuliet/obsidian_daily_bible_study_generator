# 📖 Bible Study Planner

A Python CLI tool that generates year-long daily Bible study plans as Markdown files for Obsidian. Supports complete Bible, New Testament, or Old Testament reading schedules with progress tracking, reading time estimates, and Dataview integration for statistics and visualization.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ Features

- 📅 **Flexible Reading Schedules**: Complete Bible (365 days), New Testament only (90-180 days), or Old Testament only (180-270 days)
- 📊 **Progress Dashboard**: Auto-generated dashboard with completion tracking, statistics, and streak monitoring
- 🎯 **Smart Chapter Distribution**: Balanced daily readings averaging 3-4 chapters with intelligent book grouping
- 📝 **Rich Metadata**: Full frontmatter support for Obsidian with testament, genre, estimated reading time, verse/word counts
- 🔍 **Dataview Integration**: Pre-built queries for progress tracking, statistics, and visualization
- 🎨 **Graph View Optimization**: Automatic tagging by testament, genre, and theme for visual organization
- 📖 **Multiple Reading Plans**: Canonical (book order), chronological (historical order), or custom plans
- 🛠️ **Customizable Templates**: Jinja2-based templates for complete control over note structure
- 📈 **Reading Statistics**: Track reading time, completion rates, and progress by testament/genre
- 🔗 **Smart Linking**: Automatic previous/next navigation and dashboard links

---

## 📋 Requirements

- Python 3.10 or higher
- [Obsidian](https://obsidian.md/) (for viewing generated notes)
- [Dataview Plugin](https://github.com/blacksmithgu/obsidian-dataview) (optional, for dashboard features)

---

## 🚀 Installation

### Via pip (when published)

```bash
pip install bible-study-planner
```

### From source

```bash
# Clone the repository
git clone https://github.com/yourusername/bible-study-planner.git
cd bible-study-planner

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

---

## 📖 Quick Start

### Generate a Complete Bible Reading Plan

```bash
bible-study-planner generate --year 2025
```

This creates 365 daily study files in `./bible-study/` folder.

### New Testament Only (90 days)

```bash
bible-study-planner generate --year 2025 --scope nt --days 90
```

### Old Testament Chronological Order

```bash
bible-study-planner generate --year 2025 --scope ot --plan chronological
```

### Custom Output Directory

```bash
bible-study-planner generate --year 2025 --output ~/Documents/Obsidian/BibleStudy
```

---

## 🎯 Usage Examples

### Basic Usage

```bash
# Complete Bible, canonical order, 365 days
bible-study-planner generate --year 2025

# Preview without generating files
bible-study-planner generate --year 2025 --dry-run

# With progress dashboard
bible-study-planner generate --year 2025 --progress-dashboard

# Verbose output
bible-study-planner generate --year 2025 -v
```

### Advanced Usage

```bash
# Custom configuration file
bible-study-planner generate --year 2025 --config my_config.yaml

# Custom template
bible-study-planner generate --year 2025 --template my_template.md.jinja2

# Force overwrite existing files
bible-study-planner generate --year 2025 --force

# Combine options
bible-study-planner generate \
    --year 2025 \
    --scope nt \
    --days 120 \
    --plan chronological \
    --output ~/Obsidian/NT-Study \
    --progress-dashboard \
    --config custom.yaml
```

---

## ⚙️ Configuration

### Command Line Options

```
Options:
  --year YEAR                   Target year [required]
  --scope [complete|nt|ot]      Bible scope [default: complete]
  --plan TYPE                   Reading plan type [default: canonical]
  --days INTEGER                Number of days (overrides scope default)
  --output DIR                  Output directory [default: ./bible-study]
  --config FILE                 Config file path
  --template FILE               Custom template file
  --dry-run                     Preview without generating files
  --progress-dashboard          Generate progress tracking dashboard
  --force                       Overwrite existing files
  -v, --verbose                 Verbose output
  -q, --quiet                   Minimal output
  --help                        Show help message
```

### Configuration File

Create a `config.yaml` file for persistent settings:

```yaml
# Basic Settings
year: 2025
scope: complete  # complete, nt, ot
plan_type: canonical
days: null  # null = auto-calculate

# Output Configuration
output:
  directory: "./bible-study"
  folder_structure: "monthly"  # flat, monthly, quarterly
  file_pattern: "{year}-{month:02d}-{day:02d}"

# Reading Plan Settings
reading:
  chapters_per_day_range: [3, 5]
  balance_load: true

# Template Configuration
template:
  name: "default"
  variables:
    translation: "ESV"
    include_reflection_questions: true

# Obsidian Integration
obsidian:
  tags:
    base: ["bible-study", "daily"]
    include_testament: true
    include_genre: true
  
  dataview:
    enable: true

# Progress Tracking
progress:
  enable_dashboard: true
  statistics:
    daily: true
    weekly: true
    monthly: true

# Reading Statistics
statistics:
  calculate_reading_time: true
  words_per_minute: 200
```

---

## 📄 Output Structure

### Generated Files

```
bible-study/
├── 00-Dashboard.md              # Progress tracking dashboard
├── 2025-01-01.md               # Day 1: Genesis 1-3
├── 2025-01-02.md               # Day 2: Genesis 4-7
├── 2025-01-03.md               # Day 3: Genesis 8-11
└── ...
```

### Daily Note Structure

```markdown
---
date: 2025-01-01
day: 1
tags: [bible-study, daily, genesis, old-testament, law]
testament: old
genre: law
book: Genesis
chapters: "1-3"
estimated_minutes: 12
verse_count: 78
word_count: 2350
status: pending
---

# Day 1: Monday, January 01, 2025

## 📖 Today's Reading

**Genesis 1-3**

- 📊 78 verses
- 📝 ~2,350 words
- ⏱️ 12 minutes

---

## 📝 Notes & Observations

*What did you notice in today's reading?*



---

## 💭 Reflection

### Key Themes


### Questions


### Personal Application


---

## 🙏 Prayer


---

## 📊 Metadata

**Testament**: Old  
**Genre**: Law  
**Progress**: Day 1 of 365 (0.3%)

---

[[2024-12-31|← Previous Day]] | [[00-Dashboard|Dashboard]] | [[2025-01-02|Next Day →]]
```

### Progress Dashboard

The dashboard provides:
- Overall completion percentage
- Monthly progress breakdown
- Testament-specific tracking
- Reading streaks
- Dataview-powered statistics
- Quick links to all study notes

---

## 🎨 Customization

### Custom Templates

Create your own study template using Jinja2:

```jinja2
---
date: {{ date.strftime('%Y-%m-%d') }}
day: {{ day_number }}
tags: {{ tags | tojson }}
---

# {{ reading.book }} {{ reading.start_chapter }}-{{ reading.end_chapter }}

## Reading

*{{ reading.estimated_minutes }} minutes*

## My Notes

## Prayer Points

---

[[{{ links.previous }}|Previous]] | [[{{ links.next }}|Next]]
```

Save as `my_template.md.jinja2` and use:

```bash
bible-study-planner generate --year 2025 --template my_template.md.jinja2
```

### Available Template Variables

- `date` - Current date object
- `day_number` - Day number (1-365)
- `reading` - Reading segment (book, chapters, verses, stats)
- `testament` - "old" or "new"
- `genre` - Book genre
- `tags` - List of tags
- `links` - Previous/next/dashboard links
- `progress_percentage` - Overall progress
- `total_days` - Total days in plan
- Custom variables from config

---

## 📊 Dataview Queries

### Track Completed Days

```dataview
TASK
FROM "bible-study"
WHERE status = "completed"
```

### Current Week Progress

```dataview
TABLE
  book + " " + chapters as "Reading",
  estimated_minutes + " min" as "Time",
  status as "Status"
FROM "bible-study"
WHERE date >= date(today) - dur(7 days)
SORT date ASC
```

### Statistics by Testament

```dataview
TABLE
  length(rows) as "Days",
  sum(rows.verse_count) as "Verses",
  round(sum(rows.estimated_minutes) / 60, 1) + " hours" as "Time"
FROM "bible-study"
GROUP BY testament
```

---

## 🎯 Reading Plan Types

### Canonical (Default)
Read the Bible in book order: Genesis → Revelation

**Best for**: First-time readers, traditional study

### Chronological
Read in historical/authorship order

**Best for**: Understanding biblical timeline, advanced readers

### Custom
Define your own reading order via JSON configuration

**Best for**: Thematic studies, specialized curricula

---

## 🏗️ Project Structure

```
bible-study-planner/
├── bible_study_planner/
│   ├── cli.py                  # Command-line interface
│   ├── config.py              # Configuration management
│   ├── bible/                 # Bible data & filtering
│   ├── plans/                 # Reading plan strategies
│   ├── rendering/             # Template rendering
│   └── output/                # File writing
├── data/
│   ├── bible_structure.json   # Bible metadata
│   └── bible_stats.json       # Statistics
├── templates/
│   ├── daily/                 # Daily note templates
│   └── dashboard/             # Dashboard templates
├── config/
│   └── default_config.yaml    # Default configuration
└── tests/
```

---

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/bible-study-planner.git
cd bible-study-planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=bible_study_planner

# Specific test file
pytest tests/test_bible_data.py
```

### Code Quality

```bash
# Format code
black bible_study_planner/

# Sort imports
isort bible_study_planner/

# Type checking
mypy bible_study_planner/

# Linting
flake8 bible_study_planner/
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Ideas

- New reading plan strategies
- Additional templates
- Translation data files
- Documentation improvements
- Bug fixes and optimizations
- Theme/genre expansions

---

## 📝 Roadmap

- [ ] PyPI package publication
- [ ] Multi-translation support
- [ ] Audio Bible links integration
- [ ] Memory verse system
- [ ] Commentary integration
- [ ] Mobile-optimized templates
- [ ] Group study features
- [ ] Reading history import
- [ ] Web UI for configuration

---

## 🐛 Known Issues

- Dashboard Dataview queries require Dataview plugin to be installed
- Very large custom day counts (>500 days) may have performance impact
- Word count estimates are approximate and vary by translation

---

## ❓ FAQ

### Can I use this with Bible translations other than ESV?

Currently, the tool uses ESV data. Multi-translation support is planned for a future release.

### Do I need Obsidian to use this?

The tool generates standard Markdown files that work in any text editor, but features like Dataview queries and graph visualization require Obsidian.

### Can I modify the generated files?

Absolutely! The files are yours to customize. Just be careful not to re-run the generator with `--force` or your changes will be overwritten.

### How do I mark a day as completed?

Change the `status: pending` field in the frontmatter to `status: completed`, or check the task in the dashboard.

### Can I start mid-year?

Yes! The tool will generate 365 consecutive days starting from January 1st of your specified year. You can begin reading on any date you choose.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Bible data sourced from public domain resources
- Inspired by various Bible reading plans (Robert Murray M'Cheyne, etc.)
- Built for the Obsidian community
- Thanks to all contributors and beta testers

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/bible-study-planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bible-study-planner/discussions)
- **Email**: your.email@example.com

---

## ⭐ Show Your Support

If this project helped your Bible study journey, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 📖 Sharing with others
- ☕ [Buying me a coffee](https://buymeacoffee.com/yourusername)

---

**Made with ❤️ for daily Bible study**
