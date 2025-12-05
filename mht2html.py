import re
import quopri
import base64
from email.parser import BytesParser
from email.policy import default
from io import BytesIO


def mht_to_html(mht_bytes: bytes) -> bytes:
    """
    Convert MHT format byte stream to HTML format byte stream.
    
    Args:
        mht_bytes: MHT format byte stream
        
    Returns:
        HTML format byte stream
        
    Raises:
        ValueError: If MHT format is invalid
    """
    try:
        # Parse MIME message
        msg = BytesParser(policy=default).parse(BytesIO(mht_bytes))
        
        # Find the HTML part
        html_part = None
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    html_part = part
                    break
        else:
            # Single part message, check if it's HTML
            if msg.get_content_type() == 'text/html':
                html_part = msg
        
        if not html_part:
            raise ValueError("No HTML part found in MHT file")
        
        # Get HTML content with proper decoding
        html_content = html_part.get_content()
        
        # Simplify HTML: remove unnecessary elements
        simplified_html = simplify_html(html_content)
        
        # Ensure proper encoding
        return simplified_html.encode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Error converting MHT to HTML: {str(e)}")


def simplify_html(html: str) -> str:
    """
    Simplify HTML by removing unnecessary elements while preserving structure and text.
    
    Args:
        html: Original HTML content
        
    Returns:
        Simplified HTML content
    """
    # Remove XML declarations
    html = re.sub(r'<\?xml.*?\?>', '', html, flags=re.DOTALL)
    
    # Remove comments including conditional comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove <style> tags and their content
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    
    # Remove <script> tags and their content
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    
    # Remove <link> tags (CSS links)
    html = re.sub(r'<link.*?>', '', html, flags=re.DOTALL)
    
    # Remove all meta tags except for charset
    html = re.sub(r'<meta(?!.*?charset).*?>', '', html, flags=re.DOTALL)
    
    # Remove all xmlns attributes from html tag
    html = re.sub(r'xmlns:\w+="[^"]*"', '', html)
    html = re.sub(r'xmlns="[^"]*"', '', html)
    
    # Remove all span tags and their attributes, keeping only the content
    # This is a key simplification - remove all formatting spans
    html = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html, flags=re.DOTALL)
    
    # Fix body tag with -CN suffix
    html = re.sub(r'<body-CN', '<body', html)
    html = re.sub(r'<body\s*-CN', '<body', html)
    
    # Remove all style attributes from all tags
    html = re.sub(r'\s*style="[^"]*"', '', html)
    
    # Remove all class attributes from all tags
    html = re.sub(r'\s*class="[^"]*"', '', html)
    
    # Remove all id attributes from all tags
    html = re.sub(r'\s*id="[^"]*"', '', html)
    
    # Remove all mso-* attributes from all tags
    html = re.sub(r'\s*mso-\w+="[^"]*"', '', html)
    
    # Remove all style-related attributes from td tags
    html = re.sub(r'<td[^>]*?>', '<td>', html)
    
    # Remove all style attributes from tr tags
    html = re.sub(r'<tr[^>]*?>', '<tr>', html)
    
    # Simplify table structure - only keep border attribute
    html = re.sub(r'<table[^>]*?border="?1"?[^>]*>', '<table border=1>', html, flags=re.DOTALL)
    
    # Remove all style attributes from p tags
    html = re.sub(r'<p[^>]*?>', '<p>', html)
    
    # Remove all style attributes from div tags
    html = re.sub(r'<div[^>]*?>', '<div>', html)
    
    # Remove all <o:p> tags and their content
    html = re.sub(r'<o:p>.*?</o:p>', '', html, flags=re.DOTALL)
    
    # Fix any broken tags
    html = fix_broken_tags(html)
    
    # Remove excess whitespace between tags
    html = re.sub(r'>\s+<', '><', html)
    
    # Ensure proper HTML structure
    simplified = ensure_html_structure(html)
    
    # Ensure proper charset
    simplified = re.sub(r'<meta.*?charset.*?>', '<meta charset="utf-8">', simplified, flags=re.DOTALL)
    
    # Collapse multiple whitespace characters into single space
    simplified = re.sub(r'\s+', ' ', simplified)
    
    # Remove whitespace at the beginning and end of tags
    simplified = re.sub(r'\s+>', '>', simplified)
    simplified = re.sub(r'<\s+', '<', simplified)
    
    # Decode HTML entities to plain text
    simplified = decode_html_entities(simplified)
    
    return simplified


def fix_broken_tags(html: str) -> str:
    """
    Fix common broken HTML tags.
    
    Args:
        html: HTML content with potential broken tags
        
    Returns:
        HTML content with fixed tags
    """
    # Fix self-closing tags if needed
    html = re.sub(r'<(img|br|hr)([^>]*?)/?>', r'<\1\2>', html)
    
    # Remove any trailing whitespace between tags
    html = re.sub(r'>\s+<', '><', html)
    
    return html


def decode_html_entities(html: str) -> str:
    """
    Decode HTML entities, especially &#XXXX format, to plain text.
    
    Args:
        html: HTML content with entities
        
    Returns:
        HTML content with entities decoded
    """
    # Decode numeric entities like &#1234;
    def decode_numeric_entity(match):
        code = int(match.group(1))
        return chr(code)
    
    html = re.sub(r'&#(\d+);', decode_numeric_entity, html)
    
    # Decode hex entities like &#xABCD;
    def decode_hex_entity(match):
        code = int(match.group(1), 16)
        return chr(code)
    
    html = re.sub(r'&#x([0-9a-fA-F]+);', decode_hex_entity, html)
    
    # Decode common named entities
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace("&apos;", "'")
    
    return html


def ensure_html_structure(html: str) -> str:
    """
    Ensure the HTML has a proper basic structure.
    
    Args:
        html: HTML content
        
    Returns:
        HTML content with proper structure
    """
    # Check if html tag exists
    if not re.search(r'<html', html, flags=re.IGNORECASE):
        html = f'<html>{html}</html>'
    
    # Check if head tag exists
    if not re.search(r'<head', html, flags=re.IGNORECASE):
        # Insert head with charset meta tag if not present
        if '<html>' in html:
            html = html.replace('<html>', '<html><head><meta charset="utf-8"></head>')
        elif '<html ' in html:
            # Find the end of html opening tag
            html = re.sub(r'(<html[^>]*?>)', r'\1<head><meta charset="utf-8"></head>', html, count=1)
    
    # Check if body tag exists
    if not re.search(r'<body', html, flags=re.IGNORECASE):
        # If no head, insert body after html
        if '<html>' in html and '</html>' in html:
            body_content = html.split('<html>')[1].split('</html>')[0]
            if '<head' not in body_content:
                html = f'<html><head><meta charset="utf-8"></head><body>{body_content}</body></html>'
    
    return html