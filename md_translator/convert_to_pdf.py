#!/usr/bin/env python3
"""
Markdown to PDF Converter using pypandoc and Chrome Headless

This script converts Markdown files to PDF in two steps:
1. Markdown → HTML (using pypandoc)
2. HTML → PDF (using Google Chrome headless)

Usage:
  python3 convert_to_pdf.py myfile.md
  python3 convert_to_pdf.py file1.md output.pdf
  python3 convert_to_pdf.py file1.md output.pdf custom_style.css
"""

import subprocess
import os
import sys
import platform
import re
from pathlib import Path


# ============================================================================
# DEPENDENCIES MANAGEMENT
# ============================================================================

def install_dependency(package_name):
    """Install a pip package if not already installed."""
    try:
        print(f"\nTrying to install {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package_name}", file=sys.stderr)
        return False


def import_pypandoc():
    """Import pypandoc library, auto-install if missing."""
    try:
        import pypandoc
        return pypandoc
    except ImportError:
        print("pypandoc not found. Attempting to install...", file=sys.stderr)
        if install_dependency("pypandoc"):
            import pypandoc
            return pypandoc
        else:
            print("Please install pypandoc manually: pip install pypandoc", file=sys.stderr)
            return None


# ============================================================================
# CSS FIXING/CONVERSION
# ============================================================================

def extract_background_color(css_content):
    """
    Extract background color from CSS content.
    
    Looks for:
    1. --bg-color or similar CSS variables
    2. Background color in html/body rules
    
    Args:
        css_content: CSS file content as string
    
    Returns:
        str: Hex color value or None
    """
    # Look for CSS variables like --bg-color: #363B40
    var_match = re.search(r'--bg-color\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})', css_content)
    if var_match:
        return var_match.group(1)
    
    # Look for background in html/body rules
    # Pattern: background: #363B40; or background: var(--bg-color);
    bg_match = re.search(r'(?:html|body)\s*{[^}]*background\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})', css_content, re.DOTALL)
    if bg_match:
        return bg_match.group(1)
    
    return None


def patch_css(file_path, output_path, bg_color=None):
    """
    Fix CSS file for PDF printing by adding/prepending print styles.
    
    Args:
        file_path: Path to original CSS file
        output_path: Path to output fixed CSS file
        bg_color: Background color for printing (auto-detect if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Auto-detect background color if not provided
        if bg_color is None:
            detected_color = extract_background_color(css_content)
            bg_color = detected_color if detected_color else "#f3f2ee"
            if detected_color:
                print(f"  Auto-detected background color: {bg_color}")
        
        # Define print patch with custom background color
        print_patch = f"""/* Print styling for PDF conversion */
@page {{
    margin: 15mm;
    background-color: {bg_color} !important;
}}

html, body {{
    background-color: {bg_color} !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

"""
        
        # Prepend print patch (CSS cascade: later rules override earlier ones)
        new_css = print_patch + css_content
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_css)
        
        print(f"✓ CSS fixed and saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠ Error fixing CSS: {e}", file=sys.stderr)
        return False


def fix_css_for_printing(css_file):
    """
    Fix CSS file for PDF printing with auto-detected colors.
    
    Args:
        css_file: Path to CSS file to fix
    
    Returns:
        str: Path to fixed CSS file
    """
    try:
        # Check if already fixed (has print styles)
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        if '@page' in css_content and 'print-color-adjust' in css_content:
            print(f"✓ CSS already has print styles: {css_file}")
            return css_file
        
        # Generate fixed filename
        css_path = Path(css_file)
        fixed_css_file = css_path.parent / f"{css_path.stem}_fixed.css"
        
        # Apply patch (auto-detect colors)
        if patch_css(css_file, str(fixed_css_file)):
            return str(fixed_css_file)
        else:
            return css_file
        
    except Exception as e:
        print(f"⚠ Error processing CSS: {e}", file=sys.stderr)
        return css_file


# ============================================================================
# MARKDOWN TO HTML CONVERSION
# ============================================================================

def convert_markdown_to_html(input_file, output_file, css_file=None):
    """
    Convert Markdown to HTML using pypandoc.
    
    Args:
        input_file: Path to markdown file
        output_file: Path to output HTML file
        css_file: Path to CSS stylesheet (default: style_fixed.css)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Converting {input_file} to HTML (pypandoc)...")
        
        # Use default CSS if not provided
        if css_file is None:
            css_file = "style_fixed.css"
        
        # Check if CSS file exists
        if not os.path.exists(css_file):
            print(f"⚠ CSS file not found: {css_file}, proceeding without CSS", file=sys.stderr)
            css_path = None
        else:
            css_path = css_file
        
        pypandoc = import_pypandoc()
        if pypandoc is None:
            return False
        
        # Convert markdown to HTML
        extra_args = [
            '--standalone',
            '--mathjax',
        ]
        
        # Add CSS file if it exists
        if css_path:
            extra_args.append(f'--css={css_path}')
        
        html_content = pypandoc.convert_file(
            input_file,
            'html',
            format='markdown+hard_line_breaks',
            extra_args=extra_args
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML generated: {output_file}")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Error during conversion: {e}", file=sys.stderr)
        print(f"  Make sure Pandoc is installed: https://pandoc.org/installing.html", file=sys.stderr)
        return False


# ============================================================================
# HTML TO PDF CONVERSION
# ============================================================================

def get_chrome_path():
    """
    Find Google Chrome executable path based on OS.
    
    Returns:
        str: Path to Chrome executable, or None if not found
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return path if os.path.exists(path) else None
    
    elif system == "Linux":
        paths = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]
    
    elif system == "Windows":
        paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]
    else:
        return None
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None


def convert_html_to_pdf(input_html, output_pdf):
    """
    Convert HTML to PDF using Chrome headless mode.
    
    Args:
        input_html: Path to HTML file
        output_pdf: Path to output PDF file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Converting {input_html} to PDF...")
        
        chrome_path = get_chrome_path()
        if not chrome_path:
            system = platform.system()
            print(f"✗ Google Chrome not found on {system}", file=sys.stderr)
            print("\n📦 Installation instructions:", file=sys.stderr)
            
            if system == "Darwin":
                print("  macOS: brew install --cask google-chrome", file=sys.stderr)
            elif system == "Linux":
                print("  Linux: sudo apt-get install google-chrome-stable", file=sys.stderr)
            elif system == "Windows":
                print("  Windows: choco install googlechrome", file=sys.stderr)
            
            return False
        
        # Prepare file paths
        html_absolute = os.path.abspath(input_html)
        pdf_absolute = os.path.abspath(output_pdf)
        
        # Chrome headless command
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=10000",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={pdf_absolute}",
            html_absolute
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ PDF generated: {output_pdf}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during Chrome conversion:", file=sys.stderr)
        if e.stderr:
            print(f"  {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return False


# ============================================================================
# MAIN CONVERSION PIPELINE
# ============================================================================

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        tuple: (input_markdown, css_file)
    """
    if len(sys.argv) < 2:
        print(f"✗ Missing markdown file argument", file=sys.stderr)
        print(f"\nUsage:", file=sys.stderr)
        print(f"  python3 {sys.argv[0]} file.md", file=sys.stderr)
        print(f"  python3 {sys.argv[0]} file.md custom_style.css", file=sys.stderr)
        sys.exit(1)
    
    input_markdown = sys.argv[1]
    css_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    return input_markdown, css_file


def validate_files(input_markdown):
    """
    Validate that input markdown file exists.
    
    Returns:
        bool: True if file exists, False otherwise
    """
    if not os.path.exists(input_markdown):
        print(f"✗ Input file not found: {input_markdown}", file=sys.stderr)
        print(f"\nUsage:", file=sys.stderr)
        print(f"  python3 {sys.argv[0]} myfile.md output.pdf", file=sys.stderr)
        print(f"  python3 {sys.argv[0]} myfile.md output.pdf custom_style.css", file=sys.stderr)
        return False
    
    return True


def main():
    """Main conversion pipeline."""
    # Parse arguments
    input_markdown, css_file = parse_arguments()
    
    # Generate output PDF name from input markdown
    output_pdf = Path(input_markdown).stem + ".pdf"
    
    # Validate files
    if not validate_files(input_markdown):
        return 1
    
    # Determine CSS file to use
    # If no CSS provided, use default.css
    if not css_file:
        css_file = "default.css"
    
    # Validate CSS file exists
    if not os.path.exists(css_file):
        print(f"✗ CSS file not found: {css_file}", file=sys.stderr)
        return 1
    
    # Decide if we need to create a temporary fixed version
    # Only create temp file if it's NOT the default CSS (to avoid redundant processing)
    if css_file != "default.css":
        print(f"Fixing CSS for PDF printing: {css_file}")
        
        # Create temporary fixed version
        temp_fixed_css = "_temp_fixed.css"
        if not patch_css(css_file, temp_fixed_css):
            return 1
        
        css_to_use = temp_fixed_css
        should_cleanup_css = True
    else:
        # default.css already has print styles, use it directly
        css_to_use = css_file
        should_cleanup_css = False
    
    # Print header
    print("=" * 60)
    display_css = css_file if css_file else "default.css"
    print(f"Markdown → HTML → PDF Conversion Pipeline (CSS: {display_css})")
    print("=" * 60)
    
    try:
        # Conversion step 1: Markdown to HTML
        temp_html = "temp.html"
        if not convert_markdown_to_html(input_markdown, temp_html, css_to_use):
            return 1
        
        # Conversion step 2: HTML to PDF
        if not convert_html_to_pdf(temp_html, output_pdf):
            return 1
        
        # Print footer
        print("=" * 60)
        print("✓ Conversion completed successfully!")
        print("=" * 60)
        
        return 0
        
    finally:
        # Cleanup temporary files
        # 1. Delete temporary CSS if needed
        if should_cleanup_css and os.path.exists(temp_fixed_css):
            try:
                os.remove(temp_fixed_css)
            except Exception as e:
                print(f"⚠ Could not delete temporary CSS file: {e}", file=sys.stderr)
        
        # 2. Delete temporary HTML file
        if os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except Exception as e:
                print(f"⚠ Could not delete temporary HTML file: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
