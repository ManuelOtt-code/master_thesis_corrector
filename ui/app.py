"""Streamlit web interface for Master Thesis Corrector."""
import sys
import os
import asyncio
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from master_thesis_corrector.utils.pdf_parser import parse_pdf_sections
from master_thesis_corrector.api.section import SectionAPI
from master_thesis_corrector.utils.reporter import generate_pdf_report

# Page Config
st.set_page_config(
    page_title="Thesis AI Corrector",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Master Thesis AI Corrector")
st.write(
    "Drag and drop your thesis PDF below. The AI will analyze structure, "
    "rigor, and tone."
)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    model = st.selectbox(
        "Model",
        [
            "gemini-2.5-pro",
            "gemini-1.5-pro-001",
            "gemini-1.5-flash-001",
        ],
        index=0,
        help="Vertex AI model names"
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
    st.info("Lower temperature = more focused responses")

# 1. Drag & Drop Widget
uploaded_file = st.file_uploader(
    "Upload your Thesis (PDF)",
    type="pdf",
    help="Select a PDF file containing your thesis"
)

if uploaded_file is not None:
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Display file info
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
    st.info(f"📄 File uploaded: {uploaded_file.name} ({file_size:.2f} MB)")

    # Button to trigger analysis
    if st.button("🚀 Analyze Thesis", type="primary", use_container_width=True):
        status_container = st.status("Starting Analysis...", expanded=True)

        try:
            # Step A: Parse
            status_container.write("📄 Parsing PDF sections...")
            with st.spinner("Analyzing document structure..."):
                sections = parse_pdf_sections(tmp_path)

            if not sections:
                st.error("❌ No sections detected in the PDF. Please check the file format.")
                status_container.update(
                    label="Parsing Failed",
                    state="error",
                    expanded=False
                )
            else:
                st.success(f"✅ Detected {len(sections)} sections")
                with st.expander("📋 View Detected Sections"):
                    for name, content in sections.items():
                        st.write(f"**{name}** ({len(content)} characters)")

                # Step B: Async Analysis
                status_container.write("🧠 Querying Gemini AI (this may take a few minutes)...")
                api = SectionAPI(model=model, temperature=temperature)

                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Run the async loop inside Streamlit
                # Use nest_asyncio to allow asyncio.run() in Streamlit
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    st.warning("nest_asyncio not installed. Installing...")
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "nest-asyncio"])
                    import nest_asyncio
                    nest_asyncio.apply()

                with st.spinner("Analyzing sections..."):
                    reviews = asyncio.run(api.review_thesis_async(sections))

                progress_bar.progress(1.0)
                status_text.success("✅ Analysis complete!")

                if not reviews:
                    st.error("❌ No reviews generated. Please try again.")
                    status_container.update(
                        label="Analysis Failed",
                        state="error",
                        expanded=False
                    )
                else:
                    status_container.write(f"✅ Analyzed {len(reviews)} sections successfully!")

                    # Step C: Report Generation
                    status_container.write("📝 Generating PDF Report...")
                    output_pdf_path = "Thesis_Feedback_Report.pdf"

                    with st.spinner("Creating report..."):
                        generate_pdf_report(
                            reviews,
                            uploaded_file.name,
                            output_pdf_path
                        )

                    status_container.update(
                        label="Analysis Complete!",
                        state="complete",
                        expanded=False
                    )

                    # Step D: Download Button
                    if os.path.exists(output_pdf_path):
                        with open(output_pdf_path, "rb") as file:
                            st.success("🎉 Your feedback report is ready!")
                            st.download_button(
                                label="📥 Download Feedback PDF",
                                data=file.read(),
                                file_name=f"AI_Feedback_{uploaded_file.name}",
                                mime="application/pdf",
                                use_container_width=True
                            )

                    # Optional: Preview results on screen
                    st.divider()
                    st.subheader("📊 Quick Preview")

                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    if reviews:
                        avg_clarity = sum(r.clarity_score for r in reviews) / len(reviews)
                        avg_logic = sum(r.logic_score for r in reviews) / len(reviews)
                        avg_rigor = sum(r.rigor_score for r in reviews) / len(reviews)

                        col1.metric("Average Clarity", f"{avg_clarity:.1f}/10")
                        col2.metric("Average Logic", f"{avg_logic:.1f}/10")
                        col3.metric("Average Rigor", f"{avg_rigor:.1f}/10")

                    # Detailed reviews
                    for review in reviews:
                        with st.expander(
                            f"📑 {review.section_name} "
                            f"(Clarity: {review.clarity_score}/10, "
                            f"Logic: {review.logic_score}/10, "
                            f"Rigor: {review.rigor_score}/10)"
                        ):
                            st.write("**Summary:**")
                            st.write(review.summary)

                            if review.critical_issues:
                                st.write("**Critical Issues:**")
                                for issue in review.critical_issues:
                                    st.error(f"⚠️ {issue}")

                            if review.line_by_line_edits:
                                st.write("**Suggested Edits:**")
                                for edit in review.line_by_line_edits[:5]:  # Show first 5
                                    st.write(f"- **{edit.category}**: {edit.original_text[:100]}...")
                                    st.write(f"  → {edit.suggested_revision[:100]}...")
                                    st.caption(f"Reason: {edit.reasoning}")

                                if len(review.line_by_line_edits) > 5:
                                    st.caption(
                                        f"... and {len(review.line_by_line_edits) - 5} more edits "
                                        "(see full report PDF)"
                                    )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
            status_container.update(
                label="Error Occurred",
                state="error",
                expanded=False
            )
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass  # Ignore cleanup errors

else:
    # Show instructions when no file is uploaded
    st.info("👆 Please upload a PDF file to get started")

    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Upload**: Drag and drop your thesis PDF
        2. **Parse**: The system automatically detects sections
        3. **Analyze**: AI reviews each section for:
           - Structure & Logic
           - Scientific Rigor
           - Academic Tone
        4. **Report**: Download a detailed PDF feedback report
        """)

    with st.expander("📋 What gets analyzed"):
        st.markdown("""
        - **Clarity Score**: Language clarity and readability (0-10)
        - **Logic Score**: Logical flow and structure (0-10)
        - **Rigor Score**: Scientific evidence and methodology (0-10)
        - **Critical Issues**: High-level structural or logical flaws
        - **Line-by-Line Edits**: Specific text corrections with reasoning
        """)

