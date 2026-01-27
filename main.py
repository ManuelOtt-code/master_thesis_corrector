"""Main orchestrator for Master Thesis Corrector."""
import asyncio
import sys
from pathlib import Path

from master_thesis_corrector.api.section import SectionAPI
from master_thesis_corrector.utils.pdf_parser import parse_pdf_sections
from master_thesis_corrector.utils.reporter import generate_pdf_report
from master_thesis_corrector.schema.section import ThesisReviewResult


async def main(pdf_path: str, output_path: str = "Review_Report.pdf"):
    """
    Main execution flow: PDF -> Parse -> Async API Loop -> Generate Report.
    
    Args:
        pdf_path: Path to the thesis PDF file
        output_path: Path for the output PDF report
    """
    print("=" * 60)
    print("Master Thesis Corrector V2")
    print("=" * 60)
    print(f"📄 Processing: {pdf_path}\n")
    
    # Step 1: Parse PDF into sections
    print("Step 1: Parsing PDF and detecting sections...")
    try:
        sections = parse_pdf_sections(pdf_path)
        print(f"✅ Found {len(sections)} sections:")
        for name in sections.keys():
            content_preview = sections[name][:50].replace('\n', ' ')
            print(f"   - {name}: {len(sections[name])} chars ({content_preview}...)")
        print()
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return
    
    # Step 2: Initialize API
    print("Step 2: Initializing AI review API...")
    api = SectionAPI(model="gemini-2.5-pro", temperature=0.2)
    print("✅ API initialized\n")
    
    # Step 3: Process all sections concurrently
    print("Step 3: Reviewing sections (this may take a few minutes)...")
    try:
        reviews = await api.review_thesis_async(sections)
        print(f"✅ Completed review of {len(reviews)} sections\n")
    except Exception as e:
        print(f"❌ Error during review: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Generate PDF report
    print("Step 4: Generating PDF report...")
    try:
        filename = Path(pdf_path).name
        generate_pdf_report(reviews, filename, output_path)
        print(f"✅ Report saved to: {output_path}\n")
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print("=" * 60)
    print("Review Complete!")
    print("=" * 60)
    if reviews:
        avg_clarity = sum(r.clarity_score for r in reviews) / len(reviews)
        avg_logic = sum(r.logic_score for r in reviews) / len(reviews)
        avg_rigor = sum(r.rigor_score for r in reviews) / len(reviews)
        
        print(f"Average Scores:")
        print(f"  Clarity: {avg_clarity:.1f}/10")
        print(f"  Logic:   {avg_logic:.1f}/10")
        print(f"  Rigor:   {avg_rigor:.1f}/10")
        print(f"\n📊 Full report available at: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m master_thesis_corrector.main <path_to_pdf> [output_path]")
        print("\nExample:")
        print("  python -m master_thesis_corrector.main thesis.pdf")
        print("  python -m master_thesis_corrector.main thesis.pdf my_review.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "Review_Report.pdf"
    
    # Run async main
    asyncio.run(main(pdf_path, output_path))

