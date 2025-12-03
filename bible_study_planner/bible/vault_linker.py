"""Generate Obsidian wikilinks to BibleGateway-to-Obsidian chapter files."""

from pathlib import Path
from typing import List, Optional


class VaultBibleLinker:
    """Generate wikilinks to BibleGateway-to-Obsidian chapter files.
    
    This class handles linking from daily reading notes to Bible chapter files
    created by the BibleGateway-to-Obsidian script, which uses a standardized
    structure: {path}/{number} - {BookName}/{BookName} {chapter}.md
    """
    
    # Standard Bible book order (1-66)
    BOOK_NUMBERS = {
        # Old Testament
        "Genesis": 1,
        "Exodus": 2,
        "Leviticus": 3,
        "Numbers": 4,
        "Deuteronomy": 5,
        "Joshua": 6,
        "Judges": 7,
        "Ruth": 8,
        "1 Samuel": 9,
        "2 Samuel": 10,
        "1 Kings": 11,
        "2 Kings": 12,
        "1 Chronicles": 13,
        "2 Chronicles": 14,
        "Ezra": 15,
        "Nehemiah": 16,
        "Esther": 17,
        "Job": 18,
        "Psalms": 19,
        "Proverbs": 20,
        "Ecclesiastes": 21,
        "Song of Solomon": 22,
        "Isaiah": 23,
        "Jeremiah": 24,
        "Lamentations": 25,
        "Ezekiel": 26,
        "Daniel": 27,
        "Hosea": 28,
        "Joel": 29,
        "Amos": 30,
        "Obadiah": 31,
        "Jonah": 32,
        "Micah": 33,
        "Nahum": 34,
        "Habakkuk": 35,
        "Zephaniah": 36,
        "Haggai": 37,
        "Zechariah": 38,
        "Malachi": 39,
        # New Testament
        "Matthew": 40,
        "Mark": 41,
        "Luke": 42,
        "John": 43,
        "Acts": 44,
        "Romans": 45,
        "1 Corinthians": 46,
        "2 Corinthians": 47,
        "Galatians": 48,
        "Ephesians": 49,
        "Philippians": 50,
        "Colossians": 51,
        "1 Thessalonians": 52,
        "2 Thessalonians": 53,
        "1 Timothy": 54,
        "2 Timothy": 55,
        "Titus": 56,
        "Philemon": 57,
        "Hebrews": 58,
        "James": 59,
        "1 Peter": 60,
        "2 Peter": 61,
        "1 John": 62,
        "2 John": 63,
        "3 John": 64,
        "Jude": 65,
        "Revelation": 66,
    }
    
    def __init__(self, vault_folder: str, format_style: str = "expanded"):
        """Initialize with Scripture folder path and format style.
        
        Args:
            vault_folder: Path to Scripture folder including translation
                         (e.g., "Scripture", "Bible/ESV", "Bible/NIV")
            format_style: Link format (expanded, inline, hybrid)
        """
        self.vault_folder = vault_folder.replace("\\", "/").strip("/")
        self.format_style = format_style
    
    def validate_path(self, output_dir: Path) -> bool:
        """Check if Scripture folder exists relative to output.
        
        Args:
            output_dir: Output directory for reading plan files
            
        Returns:
            True if Scripture folder exists, False otherwise
        """
        # Try both relative to output and absolute
        paths_to_check = [
            output_dir.parent / self.vault_folder,
            Path(self.vault_folder)
        ]
        return any(p.exists() and p.is_dir() for p in paths_to_check)
    
    def generate_chapter_links(
        self, 
        book_name: str, 
        start_chapter: int, 
        end_chapter: int
    ) -> List[str]:
        """Generate list of wikilinks for chapter range.
        
        Args:
            book_name: Book name (e.g., "Genesis")
            start_chapter: Starting chapter number
            end_chapter: Ending chapter number
            
        Returns:
            List of wikilinks for each chapter, or empty list if book unknown
        """
        book_num = self.BOOK_NUMBERS.get(book_name)
        if not book_num:
            return []  # Unknown book
        
        book_num_str = f"{book_num:02d}"
        folder_name = f"{book_num_str} - {book_name}"
        
        links = []
        for chapter in range(start_chapter, end_chapter + 1):
            file_path = f"{self.vault_folder}/{folder_name}/{book_name} {chapter}"
            link = f"[[{file_path}|{book_name} {chapter}]]"
            links.append(link)
        
        return links
    
    def format_links(
        self, 
        links: List[str], 
        book_name: str, 
        start_chapter: int, 
        end_chapter: int
    ) -> str:
        """Format links according to style.
        
        Args:
            links: List of generated wikilinks
            book_name: Book name for display
            start_chapter: Starting chapter
            end_chapter: Ending chapter
            
        Returns:
            Formatted markdown string
        """
        if not links:
            # Fallback to plain text
            if end_chapter > start_chapter:
                return f"**{book_name} {start_chapter}-{end_chapter}**"
            return f"**{book_name} {start_chapter}**"
        
        if self.format_style == "expanded":
            # One link per line
            return "\n".join(f"**{link}**" for link in links)
        
        elif self.format_style == "inline":
            # Compact format
            if end_chapter > start_chapter:
                # Extract paths and create chapter-only links
                chapter_nums = []
                for i, link in enumerate(links, start_chapter):
                    # Extract path from [[path|display]]
                    path = link.split("[[")[1].split("|")[0]
                    chapter_nums.append(f"[[{path}|{i}]]")
                return f"**{book_name} {start_chapter}-{end_chapter}** ({', '.join(chapter_nums)})"
            return f"**{links[0]}**"
        
        elif self.format_style == "hybrid":
            # Bullet list format
            if end_chapter > start_chapter:
                range_str = f"**{book_name} {start_chapter}-{end_chapter}**\n"
            else:
                range_str = f"**{book_name} {start_chapter}**\n"
            bullet_links = "\n".join(f"- {link}" for link in links)
            return range_str + bullet_links
        
        # Default to expanded
        return "\n".join(f"**{link}**" for link in links)
    
    def get_frontmatter_links(self, links: List[str]) -> List[str]:
        """Extract link paths for frontmatter.
        
        Args:
            links: Generated wikilinks
            
        Returns:
            List of link paths without brackets
        """
        paths = []
        for link in links:
            # Extract path from [[path|display]]
            if "[[" in link and "]]" in link:
                path = link.split("[[")[1].split("|")[0]
                paths.append(path)
        return paths
