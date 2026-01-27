"""Smart PDF section parser using PyMuPDF."""
import fitz  # PyMuPDF
from typing import Dict, List, Tuple


def analyze_font_distribution(doc: fitz.Document) -> Tuple[float, float]:
    """
    Analyze font sizes in the document to determine body text size.
    
    Returns:
        Tuple of (most_common_size, threshold_for_headers)
    """
    font_sizes = []
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(span["size"])
    
    if not font_sizes:
        return 12.0, 14.0  # Default values
    
    # Find most common font size (body text)
    from collections import Counter
    size_counts = Counter(font_sizes)
    most_common_size = size_counts.most_common(1)[0][0]
    
    # Header threshold: 1.2x body size or > 14pt
    header_threshold = max(most_common_size * 1.2, 14.0)
    
    return most_common_size, header_threshold


def parse_pdf_sections(pdf_path: str) -> Dict[str, str]:
    """
    Parses a PDF and splits it into sections based on font size heuristics.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dict mapping section names to their content text
    """
    doc = fitz.open(pdf_path)
    
    # Analyze font distribution
    body_size, header_threshold = analyze_font_distribution(doc)
    
    sections: Dict[str, str] = {}
    current_section = "Preamble"
    current_text: List[str] = []
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                line_text_parts = []
                is_header = False
                max_font_size = 0
                
                for span in line["spans"]:
                    text = span["text"].strip()
                    font_size = span["size"]
                    
                    max_font_size = max(max_font_size, font_size)
                    line_text_parts.append(text)
                
                line_text = " ".join(line_text_parts).strip()
                
                if not line_text:
                    continue
                
                # HEURISTIC: Header detection
                # - Font size significantly larger than body
                # - Short line (< 100 chars) with large font
                # - Bold text
                is_header = (
                    (max_font_size > header_threshold and len(line_text) < 100) or
                    (max_font_size > body_size * 1.3 and len(line_text) < 150)
                )
                
                if is_header:
                    # Save previous section
                    if current_text:
                        sections[current_section] = "\n".join(current_text)
                    
                    # Start new section
                    current_section = line_text
                    current_text = []
                else:
                    # Add to current section
                    if line_text:
                        current_text.append(line_text)
    
    # Capture the last section
    if current_text:
        sections[current_section] = "\n".join(current_text)
    
    doc.close()
    
    # Clean up sections: remove very short ones (likely noise)
    cleaned_sections = {
        name: content 
        for name, content in sections.items() 
        if len(content.strip()) > 50
    }
    
    return cleaned_sections

