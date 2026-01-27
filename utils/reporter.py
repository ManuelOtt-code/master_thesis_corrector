"""PDF report generator for thesis reviews."""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List

from master_thesis_corrector.schema.section import SectionReview, ThesisReviewResult


def generate_pdf_report(
    reviews: List[SectionReview], 
    filename: str = "thesis.pdf",
    output_filename: str = "Review_Report.pdf"
):
    """
    Generate a professional PDF report from section reviews.
    
    Args:
        reviews: List of SectionReview objects
        filename: Original thesis filename
        output_filename: Output PDF filename
    """
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6,
        spaceBefore=6
    )

    # Title Page
    story.append(Paragraph("Master Thesis AI Review", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"<b>Document:</b> {filename}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"<b>Total Sections Reviewed:</b> {len(reviews)}", 
        styles['Normal']
    ))
    
    # Calculate average scores
    if reviews:
        avg_clarity = sum(r.clarity_score for r in reviews) / len(reviews)
        avg_logic = sum(r.logic_score for r in reviews) / len(reviews)
        avg_rigor = sum(r.rigor_score for r in reviews) / len(reviews)
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"<b>Overall Scores:</b><br/>"
            f"Clarity: {avg_clarity:.1f}/10 | "
            f"Logic: {avg_logic:.1f}/10 | "
            f"Rigor: {avg_rigor:.1f}/10",
            styles['Normal']
        ))
    
    story.append(PageBreak())

    # Process each section
    for idx, review in enumerate(reviews, 1):
        # Section Header
        story.append(Paragraph(
            f"Section {idx}: {review.section_name}", 
            heading1_style
        ))
        
        # Score Summary Table
        score_data = [
            ["Metric", "Score", "Visual"],
            ["Clarity", f"{review.clarity_score}/10", _create_score_bar(review.clarity_score)],
            ["Logic", f"{review.logic_score}/10", _create_score_bar(review.logic_score)],
            ["Rigor", f"{review.rigor_score}/10", _create_score_bar(review.rigor_score)],
        ]
        
        score_table = Table(score_data, colWidths=[1.5*inch, 1*inch, 3*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        story.append(Paragraph("<b>Summary:</b>", heading2_style))
        story.append(Paragraph(review.summary, styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Critical Issues
        if review.critical_issues:
            story.append(Paragraph("<b>Critical Issues:</b>", heading2_style))
            for issue in review.critical_issues:
                story.append(Paragraph(f"• {issue}", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Line-by-Line Edits - Format as individual cards instead of table
        if review.line_by_line_edits:
            story.append(Paragraph("<b>Suggested Edits:</b>", heading2_style))
            story.append(Spacer(1, 0.1*inch))
            
            for idx, edit in enumerate(review.line_by_line_edits, 1):
                # Create a card-like format for each edit
                edit_style = ParagraphStyle(
                    'EditCard',
                    parent=styles['Normal'],
                    fontSize=9,
                    leftIndent=0.2*inch,
                    spaceAfter=0.15*inch,
                    borderColor=colors.HexColor('#e0e0e0'),
                    borderWidth=1,
                    borderPadding=8,
                    backColor=colors.HexColor('#fafafa')
                )
                
                # Edit number and category badge
                category_colors = {
                    'Grammar': colors.HexColor('#3498db'),
                    'Clarity': colors.HexColor('#2ecc71'),
                    'Tone': colors.HexColor('#e74c3c'),
                    'Citation': colors.HexColor('#f39c12')
                }
                category_color = category_colors.get(edit.category, colors.grey)
                
                edit_header = f"<b>Edit #{idx}</b> | <font color='{category_color.hexval()}'><b>{edit.category}</b></font>"
                story.append(Paragraph(edit_header, edit_style))
                
                # Original text (with strikethrough effect using red)
                original_para = Paragraph(
                    f"<b>Original:</b> <font color='#c0392b'>{edit.original_text}</font>",
                    ParagraphStyle('OriginalText', parent=styles['Normal'], fontSize=9, leftIndent=0.3*inch)
                )
                story.append(original_para)
                story.append(Spacer(1, 0.05*inch))
                
                # Suggested revision (with green highlight effect)
                suggestion_para = Paragraph(
                    f"<b>Suggested:</b> <font color='#27ae60'>{edit.suggested_revision}</font>",
                    ParagraphStyle('SuggestionText', parent=styles['Normal'], fontSize=9, leftIndent=0.3*inch)
                )
                story.append(suggestion_para)
                story.append(Spacer(1, 0.05*inch))
                
                # Reasoning
                reason_para = Paragraph(
                    f"<i>Reason:</i> {edit.reasoning}",
                    ParagraphStyle('ReasonText', parent=styles['Normal'], fontSize=8, leftIndent=0.3*inch, textColor=colors.HexColor('#7f8c8d'))
                )
                story.append(reason_para)
                story.append(Spacer(1, 0.15*inch))
        
        # Add page break between sections (except last)
        if idx < len(reviews):
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF report generated: {output_filename}")


def _create_score_bar(score: int, max_score: int = 10) -> str:
    """Create a simple text-based score bar."""
    filled = "█" * score
    empty = "░" * (max_score - score)
    return f"{filled}{empty}"


def generate_pdf_report_from_result(result: ThesisReviewResult, output_filename: str = "Review_Report.pdf"):
    """
    Generate PDF report from a ThesisReviewResult object.
    
    Args:
        result: ThesisReviewResult object
        output_filename: Output PDF filename
    """
    generate_pdf_report(result.reviews, result.filename, output_filename)

