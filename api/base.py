"""Base API class using Vertex AI."""
import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from google.oauth2 import service_account
    VERTEX_AI_AVAILABLE = True
except ImportError as e:
    VERTEX_AI_AVAILABLE = False
    vertexai = None
    GenerativeModel = None
    service_account = None
    _vertex_ai_import_error = str(e)

from master_thesis_corrector.prompts.base import PromptBase

from dotenv import load_dotenv

load_dotenv()


class GoogleAPIBase:
    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        temperature: Optional[float] = None,
        prompt_template: Optional[PromptBase] = None
    ):
        if not VERTEX_AI_AVAILABLE:
            error_msg = (
                "google-cloud-aiplatform package not installed. "
                "Install with: pip install google-cloud-aiplatform"
            )
            if '_vertex_ai_import_error' in globals():
                error_msg += f"\nImport error: {_vertex_ai_import_error}"
            raise ImportError(error_msg)

        self.model_name = model
        self.temperature = temperature
        self.prompt_template = prompt_template

        # Get Vertex AI configuration from environment
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        if not self.project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable is missing. "
                "Set it in your .env file or environment."
            )

        # Load service account credentials if provided
        credentials = None
        service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if service_account_path:
            service_account_path = Path(service_account_path)
            if not service_account_path.exists():
                raise FileNotFoundError(
                    f"Service account file not found: {service_account_path}. "
                    "Please check GOOGLE_APPLICATION_CREDENTIALS path."
                )
            credentials = (
                service_account.Credentials.from_service_account_file(
                    str(service_account_path)
                )
            )
            print(f"✅ Loaded service account from: {service_account_path}")

        # Initialize Vertex AI with credentials
        vertexai.init(
            project=self.project_id,
            location=self.location,
            credentials=credentials
        )

        # Get system instruction if available
        system_instruction = None
        if self.prompt_template and self.prompt_template.system_prompt:
            system_instruction = self.prompt_template.system_prompt

        # Instantiate the model with system instruction
        # System instructions must be passed when creating the model,
        # not in generation_config
        self.model = GenerativeModel(
            self.model_name,
            system_instruction=system_instruction
        )

    def _make_prompt_inputs(self, inputs: dict) -> str:
        """Format prompt inputs using the template."""
        if self.prompt_template:
            return self.prompt_template.make_inputs(inputs)
        # Fallback if no template
        return str(inputs.get("text", ""))

    def _get_generation_config(
        self,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get generation config for the API call.

        Note: system_instruction is NOT part of generation_config in Vertex AI.
        It must be passed when creating the GenerativeModel instance.
        """
        config: Dict[str, Any] = {}

        # Add temperature if specified
        if self.temperature is not None:
            config["temperature"] = self.temperature

        # Disable structured output completely - Vertex AI has compatibility issues
        # We'll rely on the prompt to instruct the model to return JSON
        # and parse it manually
        # Don't set response_mime_type or response_schema - they cause errors

        return config

    def call_api(self, inputs: dict, return_text: bool = True) -> str:
        """Synchronous API call."""
        prompt = self._make_prompt_inputs(inputs)
        return self._call_api_direct(prompt, return_text)

    def _call_api_direct(
        self,
        prompt: str,
        return_text: bool = True,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Direct synchronous API call."""
        generation_config = self._get_generation_config(response_schema)

        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )

        if return_text:
            return response.text
        else:
            return response

    async def call_api_async(
        self,
        inputs: dict,
        return_text: bool = True,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Asynchronous API call using Vertex AI.

        Note: Vertex AI SDK may not have native async methods in all versions.
        We use run_in_executor to make the blocking call non-blocking.
        """
        prompt = self._make_prompt_inputs(inputs)
        generation_config = self._get_generation_config(response_schema)

        # Run the blocking call in an executor to make it async
        loop = asyncio.get_event_loop()

        def _sync_call():
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                if return_text:
                    return response.text
                else:
                    return response
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                print(f"Error in Vertex AI call ({error_type}): {error_msg}")
                import traceback
                print(f"Full traceback:\n{traceback.format_exc()}")
                raise

        return await loop.run_in_executor(None, _sync_call)
