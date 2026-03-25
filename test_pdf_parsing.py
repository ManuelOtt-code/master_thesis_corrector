"""Test script to inspect PDF parsing and see what text is actually extracted."""
import sys
from pathlib import Path

# Add parent directory to path so we can import master_thesis_corrector
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from master_thesis_corrector.utils.pdf_parser import parse_pdf_sections


def test_pdf_parsing(pdf_path: str):
    """
    Test PDF parsing and display what sections are detected and their content.
    
    Args:
        pdf_path: Path to the PDF file to test
    """
    print("=" * 80)
    print("PDF PARSING TEST")
    print("=" * 80)
    print(f"\n📄 Testing PDF: {pdf_path}\n")
    
    try:
        # Parse the PDF
        sections = parse_pdf_sections(pdf_path)
        
        print(f"✅ Successfully parsed PDF")
        print(f"📊 Found {len(sections)} sections\n")
        print("=" * 80)
        
        # Display each section
        for idx, (section_name, section_text) in enumerate(sections.items(), 1):
            print(f"\n{'='*80}")
            print(f"SECTION {idx}: {section_name}")
            print(f"{'='*80}")
            print(f"📏 Length: {len(section_text)} characters")
            print(f"📄 Number of lines: {len(section_text.splitlines())}")
            print(f"\n{'─'*80}")
            print("CONTENT PREVIEW (first 500 characters):")
            print(f"{'─'*80}")
            print(section_text[:500])
            if len(section_text) > 500:
                print(f"\n... (truncated, {len(section_text) - 500} more characters)")
            
            print(f"\n{'─'*80}")
            print("FULL CONTENT:")
            print(f"{'─'*80}")
            print(section_text)
            print(f"\n{'='*80}\n")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total sections: {len(sections)}")
        print(f"Total characters: {sum(len(text) for text in sections.values())}")
        print(f"\nSection names:")
        for name in sections.keys():
            print(f"  - {name}")
        
        # Show what would be sent to the model (first section as example)
        if sections:
            first_section_name = list(sections.keys())[0]
            first_section_text = sections[first_section_name]
            
            print(f"\n{'='*80}")
            print("EXAMPLE: What gets sent to the model")
            print("=" * 80)
            print(f"Section Name: {first_section_name}")
            print(f"Text Length: {len(first_section_text)} characters")
            print(f"\nFull text that would be sent:")
            print(f"{'─'*80}")
            print(first_section_text)
            print(f"{'─'*80}")
        
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_parsing.py <path_to_pdf>")
        print("\nExample:")
        print("  python test_pdf_parsing.py thesis.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_pdf_parsing(pdf_path)

