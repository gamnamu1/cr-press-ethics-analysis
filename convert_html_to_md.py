#!/usr/bin/env python3
"""
Convert HTML evaluation criteria files to a single Markdown file
"""

import os
import re
from html.parser import HTMLParser

class CriteriaHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = []
        self.current_tag = None
        self.in_header = False
        self.in_title = False
        self.in_strong = False
        self.in_blockquote = False
        self.in_list = False
        self.list_level = 0
        self.small_text_level = 0

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

        if tag == 'h1':
            self.in_header = True
        elif tag == 'h3':
            pass  # Will handle in handle_data
        elif tag == 'strong':
            self.in_strong = True
        elif tag == 'blockquote':
            self.in_blockquote = True
        elif tag == 'ul':
            self.list_level += 1
            self.in_list = True
        elif tag == 'li':
            # Determine list style based on attrs
            style = dict(attrs).get('style', '')
            if 'circle' in style:
                prefix = '  - '  # Nested bullet
            else:
                prefix = '- '  # Top-level bullet

            # Add indentation based on list level
            indent = '  ' * (self.list_level - 1)
            self.content.append(f"{indent}{prefix}")
        elif tag == 'span':
            # Check for small text style
            style = dict(attrs).get('style', '')
            if 'font-size:0.8em' in style or 'opacity:0.8' in style:
                self.small_text_level += 1

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_header = False
            self.content.append('\n\n')
        elif tag == 'h3':
            self.content.append('\n\n')
        elif tag == 'strong':
            self.in_strong = False
        elif tag == 'blockquote':
            self.in_blockquote = False
            self.content.append('\n')
        elif tag == 'ul':
            self.list_level -= 1
            if self.list_level == 0:
                self.in_list = False
                self.content.append('\n')
        elif tag == 'li':
            self.content.append('\n')
        elif tag == 'span':
            if self.small_text_level > 0:
                self.small_text_level -= 1
        elif tag == 'p':
            if not self.in_blockquote:
                self.content.append('\n')

        self.current_tag = None

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        # Clean up the text
        data = data.replace('\n', ' ')
        data = re.sub(r'\s+', ' ', data)

        if self.in_header and self.current_tag == 'h1':
            # Main title - use ## for sections
            self.content.append(f"## {data}")
        elif self.current_tag == 'h3':
            # Subsection - use ###
            self.content.append(f"### {data}")
        elif self.in_strong:
            # Bold text
            self.content.append(f"**{data}**")
        elif self.in_blockquote:
            # Blockquote with indent
            lines = data.split('\n')
            for line in lines:
                if line.strip():
                    self.content.append(f"> {line.strip()}\n")
        elif self.small_text_level > 0:
            # Small text - mark with italics
            self.content.append(f" *({data})*")
        else:
            # Regular text
            if data:
                self.content.append(data)

    def get_content(self):
        return ''.join(self.content)

def parse_html_file(filepath):
    """Parse a single HTML file and return markdown content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = CriteriaHTMLParser()
    parser.feed(html_content)
    return parser.get_content()

def main():
    input_dir = 'existing-evaluation-criteria'
    output_file = 'existing-evaluation-criteria.md'

    # Get all HTML files in order
    html_files = [f'ch3_01_0{i}.html' for i in range(1, 9)]

    # Parse all files and combine
    all_content = []
    all_content.append("# 언론 보도 평가 기준 (기존 8항목)\n\n")
    all_content.append("> 기존 평가 기준 8개 항목을 통합한 문서입니다.\n\n")
    all_content.append("---\n\n")

    for filename in html_files:
        filepath = os.path.join(input_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}...")
            content = parse_html_file(filepath)
            all_content.append(content)
            all_content.append("\n---\n\n")  # Separator between sections

    # Write combined markdown
    final_content = ''.join(all_content)

    # Clean up extra whitespace
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"\n✓ Successfully created {output_file}")
    print(f"  Total sections processed: {len(html_files)}")

if __name__ == '__main__':
    main()
