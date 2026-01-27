"""Test script to see exactly what prompt is sent to the model."""
import sys
from pathlib import Path

# Add parent directory to path so we can import master_thesis_corrector
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from master_thesis_corrector.utils.pdf_parser import parse_pdf_sections
from master_thesis_corrector.api.section import SectionAPI
from master_thesis_corrector.prompts.section import section_prompt


def test_model_input(pdf_path: str, section_name: str = None):
    """
    Test what exactly gets sent to the model for a given section.
    
    Args:
        pdf_path: Path to the PDF file
        section_name: Name of the section to test (if None, uses first section)
    """
    print("=" * 80)
    print("MODEL INPUT TEST")
    print("=" * 80)
    print(f"\n📄 PDF: {pdf_path}\n")
    
    try:
        # Parse PDF
        sections = parse_pdf_sections(pdf_path)
        
        if not sections:
            print("❌ No sections found in PDF")
            return
        
        # Select section to test
        if section_name is None:
            section_name = list(sections.keys())[0]
        
        if section_name not in sections:
            print(f"❌ Section '{section_name}' not found")
            print(f"Available sections: {list(sections.keys())}")
            return
        
        section_text = sections[section_name]
        
        print(f"✅ Testing section: {section_name}")
        print(f"📏 Section text length: {len(section_text)} characters\n")
        
        # Show the actual section text
        print("=" * 80)
        print("SECTION TEXT (what the model receives):")
        print("=" * 80)
        print(section_text)
        print("=" * 80)
        
        # Show the prompt template
        print("\n" + "=" * 80)
        print("PROMPT TEMPLATE:")
        print("=" * 80)
        print("System Prompt:")
        print("-" * 80)
        print(section_prompt.system_prompt)
        print("-" * 80)
        
        print("\nInput Template:")
        print("-" * 80)
        print(section_prompt.inputs)
        print("-" * 80)
        
        # Show the formatted prompt that would be sent
        print("\n" + "=" * 80)
        print("FORMATTED PROMPT (what actually gets sent to the model):")
        print("=" * 80)
        
        # Format the prompt
        inputs = {"text": section_text}
        formatted_prompt = section_prompt.make_inputs(inputs)
        
        print("\n[System Instruction - sent separately]")
        print(section_prompt.system_prompt)
        print("\n[User Prompt - with actual section text]")
        print("-" * 80)
        print(formatted_prompt)
        print("-" * 80)
        print("=" * 80)
        
        # Also show a comparison
        print("\n" + "=" * 80)
        print("COMPARISON: Template vs Actual")
        print("=" * 80)
        print("\nTemplate (before formatting):")
        print("-" * 80)
        print(section_prompt.inputs)
        print("-" * 80)
        print("\nActual (after formatting with section text):")
        print("-" * 80)
        print(formatted_prompt)
        print("-" * 80)
        
        # Show statistics
        print("\n" + "=" * 80)
        print("STATISTICS:")
        print("=" * 80)
        print(f"Section text length: {len(section_text)} characters")
        print(f"Section text word count: {len(section_text.split())} words")
        print(f"System prompt length: {len(section_prompt.system_prompt)} characters")
        print(f"Formatted prompt length: {len(formatted_prompt)} characters")
        print(f"Total input length: {len(section_prompt.system_prompt) + len(formatted_prompt)} characters")
        
        # Check for potential issues
        print("\n" + "=" * 80)
        print("POTENTIAL ISSUES:")
        print("=" * 80)
        
        issues = []
        if len(section_text) < 100:
            issues.append("⚠️  Section text is very short (< 100 chars) - might not have enough context")
        if len(section_text) > 10000:
            issues.append("⚠️  Section text is very long (> 10k chars) - might get truncated")
        if "Table" in section_text and "M =" not in section_text:
            issues.append("⚠️  Section mentions 'Table' but no statistical data found - model might hallucinate")
        if "Figure" in section_text:
            issues.append("ℹ️  Section mentions 'Figure' - model cannot see figures")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ No obvious issues detected")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_model_input.py <path_to_pdf> [section_name]")
        print("\nExample:")
        print("  python test_model_input.py thesis.pdf")
        print("  python test_model_input.py thesis.pdf 'Introduction'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    section_name = sys.argv[2] if len(sys.argv) > 2 else None
    test_model_input(pdf_path, section_name)

