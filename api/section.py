"""Section API using Vertex AI."""
import json
import asyncio
from typing import Optional, List, Dict

from master_thesis_corrector.api.base import GoogleAPIBase
from master_thesis_corrector.prompts.section import section_prompt
from master_thesis_corrector.schema.section import SectionReview

from dotenv import load_dotenv

load_dotenv()


class SectionAPI(GoogleAPIBase):
    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        temperature: Optional[float] = 0.2
    ):
        super().__init__(model, temperature, section_prompt)

    async def _process_single_section(
        self,
        section_name: str,
        section_text: str
    ) -> SectionReview:
        """
        Helper to call Vertex AI for one section asynchronously.

        Args:
            section_name: Name of the section
            section_text: Content of the section

        Returns:
            SectionReview object with feedback
        """
        # Construct inputs for the prompt template
        inputs = {"text": section_text}

        # For now, disable structured output and parse JSON manually
        # Vertex AI seems to have issues with complex schemas
        # We'll request JSON format and parse it ourselves
        try:
            # Make async API call without schema (just request JSON format)
            # The prompt will instruct the model to return JSON
            response_text = await self.call_api_async(
                inputs,
                return_text=True,
                response_schema=None  # Disable structured output for now
            )

            # Parse the response into SectionReview
            # With structured output, it should be valid JSON
            try:
                # Try to extract JSON if wrapped in markdown code blocks
                import re
                json_match = re.search(
                    r'```(?:json)?\s*(\{.*?\})\s*```',
                    response_text,
                    re.DOTALL
                )
                if json_match:
                    response_text = json_match.group(1)
                else:
                    # Try to find JSON object in the text (might not be in code blocks)
                    json_match = re.search(
                        r'\{.*\}',
                        response_text,
                        re.DOTALL
                    )
                    if json_match:
                        response_text = json_match.group(0)

                # Parse JSON response
                # Handle potential truncation by trying to fix incomplete JSON
                try:
                    response_dict = json.loads(response_text)
                except json.JSONDecodeError as json_err:
                    # Try to fix common truncation issues
                    print(f"JSON parse error: {json_err}")
                    print(f"Response text (first 500 chars): {response_text[:500]}")
                    
                    # Try to fix incomplete strings in JSON
                    fixed_text = self._fix_truncated_json(response_text)
                    try:
                        response_dict = json.loads(fixed_text)
                    except json.JSONDecodeError:
                        # If still fails, raise original error
                        raise json_err
                
                # Normalize category values before validation
                response_dict = self._normalize_categories(response_dict)
                result = SectionReview.model_validate(response_dict)

            except (json.JSONDecodeError, ValueError) as e:
                # If JSON parsing fails, try fallback parser
                print(
                    f"Warning: JSON parsing failed for "
                    f"{section_name}, using fallback parser: {e}"
                )
                result = self._parse_text_response(response_text, section_name)

        except Exception as e:
            print(
                f"Error processing section {section_name}: {e}. "
                "Please try again"
            )
            # Create a minimal review as fallback
            result = SectionReview(
                section_name=section_name,
                clarity_score=5,
                logic_score=5,
                rigor_score=5,
                summary=f"Error parsing response: {str(e)}",
                critical_issues=[],
                line_by_line_edits=[]
            )

        # Ensure section name is set
        result.section_name = section_name
        return result

    def _parse_text_response(self, text: str, section_name: str) -> SectionReview:
        """
        Fallback parser for text responses (when JSON parsing fails).
        This attempts to extract structured information from free-form text.
        """
        import re

        # Try to extract scores
        clarity_match = re.search(r'[Cc]larity[:\s]+(\d+)', text)
        logic_match = re.search(r'[Ll]ogic[:\s]+(\d+)', text)
        rigor_match = re.search(r'[Rr]igor[:\s]+(\d+)', text)

        clarity_score = int(clarity_match.group(1)) if clarity_match else 5
        logic_score = int(logic_match.group(1)) if logic_match else 5
        rigor_score = int(rigor_match.group(1)) if rigor_match else 5

        # Extract summary (first paragraph or section)
        summary_match = re.search(
            r'[Ss]ummary[:\s]+(.*?)(?:\n\n|$)',
            text,
            re.DOTALL
        )
        summary = (
            summary_match.group(1).strip()
            if summary_match
            else text[:200]
        )

        return SectionReview(
            section_name=section_name,
            clarity_score=clarity_score,
            logic_score=logic_score,
            rigor_score=rigor_score,
            summary=summary,
            critical_issues=[],
            line_by_line_edits=[]
        )

    async def review_thesis_async(
        self,
        parsed_sections: Dict[str, str]
    ) -> List[SectionReview]:
        """
        Main entry point for concurrent processing of all sections.

        Args:
            parsed_sections: Dictionary mapping section names to their content

        Returns:
            List of SectionReview objects, one per section
        """
        tasks = []
        for name, text in parsed_sections.items():
            if len(text.strip()) < 50:
                continue  # Skip empty/noise sections
            tasks.append(self._process_single_section(name, text))

        print(f"🚀 Analyzing {len(tasks)} sections concurrently...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                section_name = list(parsed_sections.keys())[i]
                print(f"❌ Error processing section '{section_name}': {result}")
                # Create error review
                error_review = SectionReview(
                    section_name=section_name,
                    clarity_score=0,
                    logic_score=0,
                    rigor_score=0,
                    summary=f"Error during processing: {str(result)}",
                    critical_issues=["Processing error occurred"],
                    line_by_line_edits=[]
                )
                valid_results.append(error_review)
            else:
                valid_results.append(result)

        return valid_results

    def _clean_schema_for_vertex_ai(self, schema: Dict) -> Dict:
        """
        Clean Pydantic JSON schema to be compatible with Vertex AI.

        Vertex AI doesn't support $defs (definitions), so we need to:
        1. Remove $defs
        2. Inline any $ref references if needed
        """
        import copy

        cleaned = copy.deepcopy(schema)

        # Remove $defs if present
        if "$defs" in cleaned:
            defs = cleaned.pop("$defs")

            # Try to inline simple $ref references
            def inline_refs(obj):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref_path = obj["$ref"]
                        if ref_path.startswith("#/$defs/"):
                            def_name = ref_path.split("/")[-1]
                            if def_name in defs:
                                # Replace $ref with the actual definition
                                return inline_refs(defs[def_name])
                    else:
                        # Recursively process nested objects
                        return {
                            k: inline_refs(v) for k, v in obj.items()
                        }
                elif isinstance(obj, list):
                    return [inline_refs(item) for item in obj]
                return obj

            cleaned = inline_refs(cleaned)

        return cleaned

    def _normalize_categories(self, data: Dict) -> Dict:
        """
        Normalize category values in line_by_line_edits to match schema.
        
        Maps invalid categories to valid ones:
        - 'Rigor' -> 'Clarity' (content-related)
        - 'Precision' -> 'Clarity' (language precision)
        - Other invalid -> 'Clarity' (default)
        """
        if "line_by_line_edits" in data and isinstance(
            data["line_by_line_edits"], list
        ):
            valid_categories = {"Grammar", "Clarity", "Tone", "Citation"}
            category_mapping = {
                "Rigor": "Clarity",
                "Precision": "Clarity",
                "Style": "Tone",
                "Format": "Grammar",
            }

            for edit in data["line_by_line_edits"]:
                if isinstance(edit, dict) and "category" in edit:
                    category = edit["category"]
                    if category not in valid_categories:
                        # Map to valid category
                        edit["category"] = category_mapping.get(
                            category, "Clarity"
                        )

            return data

    def _fix_truncated_json(self, json_text: str) -> str:
        """
        Attempt to fix truncated or incomplete JSON strings.
        
        Common issues:
        - Incomplete strings (missing closing quotes)
        - Missing closing braces/brackets
        - Truncated text in string values
        """
        import re
        
        # Count braces and brackets to see if JSON is incomplete
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        
        fixed = json_text
        
        # If we have unclosed braces/brackets, try to close them
        if open_braces > close_braces:
            fixed += '}' * (open_braces - close_braces)
        if open_brackets > close_brackets:
            fixed += ']' * (open_brackets - close_brackets)
        
        # Try to fix incomplete strings (text that ends without closing quote)
        # Look for patterns like: "key": "incomplete text
        # This is tricky, so we'll be conservative
        incomplete_string_pattern = r'"([^"]*)":\s*"([^"]*)$'
        matches = list(re.finditer(incomplete_string_pattern, fixed))
        
        if matches:
            # For the last incomplete string, try to close it
            last_match = matches[-1]
            # If the string value is incomplete, close it
            if not fixed[last_match.end():last_match.end()+1] == '"':
                # Find where the string should end (before comma, brace, or bracket)
                end_pos = last_match.end()
                # Close the string
                fixed = fixed[:end_pos] + '"' + fixed[end_pos:]
        
        return fixed

    def run(self, pdf_path: str) -> dict:
        """
        Legacy synchronous method (kept for backward compatibility).
        Consider using review_thesis_async instead.
        """
        from master_thesis_corrector.utils.pdf_parser import parse_pdf_sections

        sections = parse_pdf_sections(pdf_path)
        results = asyncio.run(self.review_thesis_async(sections))

        return {
            "filename": pdf_path,
            "reviews": [review.model_dump() for review in results]
        }
