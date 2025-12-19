from pathlib import Path
import textwrap

from tabulate import tabulate

from .mrkdwn_analysis import MarkdownAnalyzer



def format_beautiful_table(table_data, max_width=40, tablefmt='grid'):
    """
    Create beautifully formatted tables with proper text wrapping

    Args:
        table_data: Dictionary with 'header' and 'rows' keys
        max_width: Maximum width for each column
        tablefmt: Table format style
    """

    def wrap_text(text, width=max_width):
        """Wrap text to specified width"""
        if not isinstance(text, str):
            text = str(text)
        return '\n'.join(textwrap.wrap(text, width=width, break_long_words=True))

    # Wrap headers
    wrapped_headers = [wrap_text(header) for header in table_data['header']]

    # Wrap all cell content
    wrapped_rows = []
    for row in table_data['rows']:
        wrapped_row = [wrap_text(cell) for cell in row]
        wrapped_rows.append(wrapped_row)

    # Generate beautiful table
    return tabulate(
        wrapped_rows,
        headers=wrapped_headers,
        tablefmt=tablefmt,
        stralign='left'
    )


class MarkdownTool:
    """
    Encapsulates all markdown analysis operations for a single file.
    Validates once, creates analyzer once, reuses state across operations.
    """
    
    def __init__(self, conn, id):
        """
        Initialize with SQLite connection and ID, validate, and prepare analyzer.

        Args:
            conn: SQLite database connection
            id: Database ID for the markdown content

        Raises:
            ValueError: If content cannot be retrieved from database
        """
        self.conn = conn
        self.id = id
        self._analyzer: MarkdownAnalyzer | None = None
        self._content: str | None = None

        # Validate immediately
        self._validate()

    def _validate(self):
        """Validate database record existence and fetch content"""
        try:
            cursor = self.conn.cursor()
            # Query to fetch the text content for the given ID
            cursor.execute("SELECT text FROM search_results WHERE id = ?", (self.id,))
            result = cursor.fetchone()

            if result is None:
                raise ValueError(f"No content found for ID {self.id} in database")

            self._content = result[0]

            if not self._content or not isinstance(self._content, str):
                raise ValueError(f"Invalid content for ID {self.id}")

        except Exception as e:
            raise ValueError(f"Failed to fetch content from database: {e}")
    
    @property
    def analyzer(self):
        """Lazy load analyzer - create only when first needed"""
        if self._analyzer is None:
            self._analyzer = MarkdownAnalyzer.from_string(self._content)
        return self._analyzer
    
    def _safe_execute(self, operation):
        """
        Wrapper for safe tool execution with consistent error handling.
        
        Args:
            operation: Callable that performs the actual work
            
        Returns:
            Operation result or error message
        """
        try:
            return operation()
        except Exception as e:
            return f"Analysis failed: {str(e)}"
    
    # ============ TOOL METHODS ============
    
    def get_headers(self):
        """Extract all headers with line numbers"""
        def _op():
            headers = self.analyzer.identify_headers()
            header_list = headers.get('Header', [])
            return headers if header_list else "No headers found"
        
        return self._safe_execute(_op)
    
    def get_paragraphs(self):
        """Extract all paragraphs with line numbers"""
        def _op():
            result = {"Paragraph": []}
            for token in self.analyzer.tokens:
                if token.type == 'paragraph':
                    result["Paragraph"].append({
                        "line": token.line,
                        "content": token.content.strip()
                    })
            return result if result["Paragraph"] else "No paragraphs found"
        
        return self._safe_execute(_op)
    
    def get_links(self):
        """Extract HTTP/HTTPS links with line numbers"""
        def _op():
            links = self.analyzer.identify_links()
            filter_links = [
                x for x in links.get('Text link', []) 
                if x.get('url', '').lower().startswith('http')
            ]
            return filter_links if filter_links else "No HTTP links found"
        
        return self._safe_execute(_op)
    
    def get_code_blocks(self):
        """Extract all code blocks with line numbers"""
        def _op():
            code_blocks = self.analyzer.identify_code_blocks()
            code_list = code_blocks.get('Code block', [])
            return code_blocks if code_list else "No code blocks found"
        
        return self._safe_execute(_op)
    
    def get_tables_metadata(self):
        """Extract metadata of all tables - headers and line numbers"""
        def _op():
            tables_metadata = []
            table_index = 1
            
            for token in self.analyzer.tokens:
                if token.type == 'table':
                    headers = token.meta.get("header", [])
                    headers_str = ", ".join(headers)
                    
                    tables_metadata.append([
                        str(table_index),
                        str(token.line),
                        str(len(headers)),
                        str(len(token.meta.get("rows", []))),
                        headers_str
                    ])
                    table_index += 1
            
            if not tables_metadata:
                return "No tables found"
            
            table_data = {
                "header": ["Table #", "Line", "Columns", "Rows", "Headers Preview"],
                "rows": tables_metadata
            }
            return format_beautiful_table(table_data)
        
        return self._safe_execute(_op)
    
    def get_table_by_line(self, line_number: int):
        """
        Extract and format specific table at given line

        Args:
            line_number: The line number where the table is located
        """
        def _op():
            import re
            
            for token in self.analyzer.tokens:
                if token.type == 'table' and token.line == line_number:
                    headers = token.meta.get("header", [])
                    rows = token.meta.get("rows", [])
                    
                    # Clean markdown links from headers
                    clean_headers = [
                        re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', h).strip()
                        for h in headers
                    ]
                    
                    # Clean markdown links from cells
                    clean_rows = [
                        [re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cell).strip() 
                         for cell in row]
                        for row in rows
                    ]
                    
                    table_data = {
                        "header": clean_headers,
                        "rows": clean_rows
                    }
                    return format_beautiful_table(table_data, max_width=15, tablefmt='grid')
            
            return f"No table at line {line_number}"
        
        return self._safe_execute(_op)
    
    def get_header_by_line(self, line_number: int):
        """
        Extract content under specific header at given line

        Args:
            line_number: The line number where the header is located
        """
        def _op():
            headers = self.analyzer.identify_headers()
            header_list = headers.get('Header', [])
            
            # Find target header
            target_header = None
            for header in header_list:
                if header.get('line') == line_number:
                    target_header = header
                    break
            
            if not target_header:
                return f"No header at line {line_number}"
            
            # Get content lines
            content_lines = self._content.split('\n')
            target_level = target_header.get('level', 1)
            start_line = target_header.get('line', 1)
            
            # Find end line (next header of same or higher level)
            end_line = len(content_lines)
            for header in header_list:
                header_line = header.get('line', 1)
                header_level = header.get('level', 1)
                if header_line > start_line and header_level <= target_level:
                    end_line = header_line - 1
                    break
            
            # Extract section content (skip header itself)
            section_content = [
                content_lines[i].rstrip('\n')
                for i in range(start_line, min(end_line, len(content_lines)))
            ]
            
            section_text = '\n'.join(section_content).strip()
            
            return {
                "header": {
                    "line": start_line,
                    "level": target_level,
                    "text": target_header.get('text', '')
                },
                "content": section_text,
                "content_lines": f"{start_line + 1}-{min(end_line, len(content_lines))}",
                "word_count": len(section_text.split()) if section_text else 0
            }
        
        return self._safe_execute(_op)
    
    def get_intro(self):
        """Extract introduction/abstract/summary intelligently"""
        def _op():
            headers = self.analyzer.identify_headers()
            header_list = headers.get('Header', [])
            
            # Intro patterns for various document types
            intro_patterns = [
                'abstract', 'summary', 'executive summary',
                'introduction', 'intro', 'overview', 'about',
                'preface', 'foreword', 'background', 'context',
                'getting started', 'what is', 'description'
            ]
            
            # Strategy 1: Look for explicit intro header
            intro_header = None
            for header in header_list:
                header_text = header.get('text', '').lower().strip()
                if any(pattern in header_text for pattern in intro_patterns):
                    intro_header = header
                    break
            
            if intro_header:
                content_lines = self._content.split('\n')
                target_level = intro_header.get('level', 1)
                start_line = intro_header.get('line', 1)
                
                # Find end line
                end_line = len(content_lines)
                for header in header_list:
                    header_line = header.get('line', 1)
                    header_level = header.get('level', 1)
                    if header_line > start_line and header_level <= target_level:
                        end_line = header_line - 1
                        break
                
                section_content = [
                    content_lines[i]
                    for i in range(start_line, min(end_line, len(content_lines)))
                ]
                section_text = '\n'.join(section_content).strip()
                
                return {
                    "type": "explicit_header",
                    "header": {
                        "line": start_line,
                        "level": target_level,
                        "text": intro_header.get('text', '')
                    },
                    "content": section_text,
                    "content_lines": f"{start_line + 1}-{min(end_line, len(content_lines))}",
                    "word_count": len(section_text.split()) if section_text else 0
                }
            
            # Strategy 2: First paragraphs after title
            if not header_list:
                return "No structure found for intro extraction"
            
            first_header = header_list[0]
            title_line = first_header.get('line', 1)
            
            # Get paragraphs after title
            paragraphs = [
                {"line": token.line, "content": token.content.strip()}
                for token in self.analyzer.tokens
                if token.type == 'paragraph' and token.line > title_line
            ]
            
            if not paragraphs:
                return "No introductory content found"
            
            # Take first 2-3 paragraphs (max 300 words)
            intro_paragraphs = []
            word_count = 0
            for para in paragraphs:
                para_words = len(para['content'].split())
                if word_count + para_words > 300:
                    break
                intro_paragraphs.append(para)
                word_count += para_words
                if len(intro_paragraphs) >= 3:
                    break
            
            intro_content = '\n\n'.join(p['content'] for p in intro_paragraphs)
            start_line = intro_paragraphs[0]['line'] if intro_paragraphs else title_line + 1
            end_line = intro_paragraphs[-1]['line'] if intro_paragraphs else start_line
            
            return {
                "type": "inferred_paragraphs",
                "header": {
                    "line": title_line,
                    "level": first_header.get('level', 1),
                    "text": first_header.get('text', 'Document Title')
                },
                "content": intro_content,
                "content_lines": f"{start_line}-{end_line}",
                "word_count": word_count,
                "paragraphs_count": len(intro_paragraphs)
            }
        
        return self._safe_execute(_op)
    
    def get_lists(self):
        """Extract all lists with line numbers"""
        def _op():
            result = {"Ordered list": [], "Unordered list": []}
            
            for token in self.analyzer.tokens:
                if token.type == 'ordered_list':
                    result["Ordered list"].append({
                        "line": token.line,
                        "items": token.meta["items"]
                    })
                elif token.type == 'unordered_list':
                    result["Unordered list"].append({
                        "line": token.line,
                        "items": token.meta["items"]
                    })
            
            has_lists = result["Ordered list"] or result["Unordered list"]
            return result if has_lists else "No lists found"
        
        return self._safe_execute(_op)
    
    def get_overview(self):
        """Get complete eagle eye view of document structure"""
        def _op():
            # Get all components
            headers = self.analyzer.identify_headers()
            paragraphs = self.analyzer.identify_paragraphs()
            links = self.analyzer.identify_links()
            code_blocks = self.analyzer.identify_code_blocks()
            tables = self.analyzer.identify_tables()
            lists = self.analyzer.identify_lists()
            intro_result = self.get_intro()
            
            # Filter HTTP links
            http_links = [
                x for x in links.get('Text link', [])
                if x.get('url', '').lower().startswith('http')
            ]
            
            # Statistics
            paragraph_list = paragraphs.get('Paragraph', [])
            total_paragraphs = len(paragraph_list)
            word_count = sum(len(p.split()) for p in paragraph_list)
            
            # Build structure
            header_list = headers.get('Header', [])
            structure = [
                f"{'  ' * (h.get('level', 1) - 1)}H{h.get('level', 1)}: {h.get('text', '')} (line {h.get('line', 'N/A')})"
                for h in header_list
            ]
            
            # Code blocks summary
            code_block_summary = [
                f"{cb.get('language', 'unknown')} code block (lines {cb.get('start_line', 'N/A')}-{cb.get('end_line', 'N/A')})"
                for cb in code_blocks.get('Code block', [])
            ]
            
            # Tables summary
            table_summary = [
                f"Table at line {table.get('line', 'N/A')}"
                for table in tables.get('Table', [])
            ]
            
            # Process intro
            intro_info = {
                "found": isinstance(intro_result, dict),
                "type": intro_result.get('type', 'none') if isinstance(intro_result, dict) else 'none',
                "word_count": intro_result.get('word_count', 0) if isinstance(intro_result, dict) else 0,
                "content": intro_result.get('content', '') if isinstance(intro_result, dict) else 'No introduction found'
            }
            
            # Build overview data
            overview_data = {
                "document_title": header_list[0].get('text', 'Untitled') if header_list else 'Untitled',
                "introduction": intro_info,
                "complete_structure": structure,
                "all_headers": [h.get('text', '') for h in header_list],
                "code_blocks_detail": code_block_summary,
                "tables_detail": table_summary,
                "content_stats": {
                    "total_sections": len(header_list),
                    "paragraphs": total_paragraphs,
                    "estimated_words": word_count,
                    "code_blocks": len(code_blocks.get('Code block', [])),
                    "tables": len(tables.get('Table', [])),
                    "lists": len(lists.get('Ordered list', [])) + len(lists.get('Unordered list', [])),
                    "external_links": len(http_links)
                },
                "content_types_present": {
                    "has_code": len(code_blocks.get('Code block', [])) > 0,
                    "has_tables": len(tables.get('Table', [])) > 0,
                    "has_lists": len(lists.get('Ordered list', [])) + len(lists.get('Unordered list', [])) > 0,
                    "has_links": len(http_links) > 0,
                    "has_intro": intro_info['found']
                }
            }
            
            # Format as markdown
            ds = "\n".join(overview_data['complete_structure'])
            hl = "\n".join(f"- {h}" for h in overview_data['all_headers'])
            cb_detail = "\n".join(f"- {cb}" for cb in overview_data['code_blocks_detail']) if overview_data['code_blocks_detail'] else "None"
            table_detail = "\n".join(f"- {t}" for t in overview_data['tables_detail']) if overview_data['tables_detail'] else "None"
            
            markdown_overview = f"""# Document Overview: {overview_data['document_title']}

## Introduction/Abstract
- **Found**: {'Yes' if overview_data['introduction']['found'] else 'No'}
- **Type**: {overview_data['introduction']['type'].replace('_', ' ').title()}
- **Word Count**: {overview_data['introduction']['word_count']}

{overview_data['introduction']['content']}

## Document Structure
{ds}

## Content Statistics
- **Total Sections**: {overview_data['content_stats']['total_sections']}
- **Paragraphs**: {overview_data['content_stats']['paragraphs']}
- **Estimated Words**: {overview_data['content_stats']['estimated_words']}
- **Code Blocks**: {overview_data['content_stats']['code_blocks']}
- **Tables**: {overview_data['content_stats']['tables']}
- **Lists**: {overview_data['content_stats']['lists']}
- **External Links**: {overview_data['content_stats']['external_links']}

## Code Blocks Detail
{cb_detail}

## Tables Detail
{table_detail}

## Content Types Present
- **Has Introduction**: {'Yes' if overview_data['content_types_present']['has_intro'] else 'No'}
- **Has Code**: {'Yes' if overview_data['content_types_present']['has_code'] else 'No'}
- **Has Tables**: {'Yes' if overview_data['content_types_present']['has_tables'] else 'No'}
- **Has Lists**: {'Yes' if overview_data['content_types_present']['has_lists'] else 'No'}
- **Has External Links**: {'Yes' if overview_data['content_types_present']['has_links'] else 'No'}

## All Headers List
{hl}
"""
            return markdown_overview if header_list else "Empty document found"
        
        return self._safe_execute(_op)
    
    # ============ MCP INTEGRATION ============
    
    def get_tools(self):
        """
        Return list of tool methods for FastMCP registration.
        Each method is already bound to this instance.
        """
        return [
            self.get_headers,
            self.get_paragraphs,
            self.get_links,
            self.get_code_blocks,
            self.get_tables_metadata,
            self.get_table_by_line,
            self.get_header_by_line,
            self.get_intro,
            self.get_lists,
            self.get_overview,
        ]
    
    def get_tool_dict(self):
        """
        Return dict mapping tool names to methods.
        Useful for dynamic dispatch or CLI interfaces.
        """
        return {
            "get_headers": self.get_headers,
            "get_paragraphs": self.get_paragraphs,
            "get_links": self.get_links,
            "get_code_blocks": self.get_code_blocks,
            "get_tables_metadata": self.get_tables_metadata,
            "get_table_by_line": self.get_table_by_line,
            "get_header_by_line": self.get_header_by_line,
            "get_intro": self.get_intro,
            "get_lists": self.get_lists,
            "get_overview": self.get_overview,
        }