"""Base prompt class for Master Thesis Corrector."""
try:
    from pydantic import BaseModel
except ImportError:
    # Fallback if pydantic is not available
    class BaseModel:
        pass

class PromptBase(BaseModel):
    """Base prompt class for all prompts. Containing the following fields:
    - prefix: The prefix of the prompt. Usually the system prompt, role description, etc.
    - inputs: The inputs of the prompt, containing the actual user inputs, which are represented by placeholders. Placeholders are typically denoted by double curly braces, e.g. {{input_key}}.
    - suffix: The suffix of the prompt. Usually the instruction, output format, etc.
    """
    system_prompt: str
    prefix: str
    inputs: str
    suffix: str
    
    def to_string(self) -> str:
        """Convert the prompt to a string. System prompt would not be included in the string."""
        return f"{self.prefix}\n{self.inputs}\n{self.suffix}".strip()
    
    def __str__(self) -> str:
        """Convert the prompt to a string."""
        return self.to_string()
    
    def to_dict(self) -> dict:
        """Convert the prompt to a dictionary."""
        return {
            "system_prompt": self.system_prompt,
            "prefix": self.prefix,
            "inputs": self.inputs,
            "suffix": self.suffix
        }
    
    def make_prompt(self, inputs: dict) -> str:
        """Apply the inputs to the prompt."""
        res = self.to_string()
        for key, value in inputs.items():
            # Try both single and double braces for compatibility
            placeholder_double = "{{" + key + "}}"
            placeholder_single = "{" + key + "}"
            
            if placeholder_double in res:
                res = res.replace(placeholder_double, str(value))
            elif placeholder_single in res:
                res = res.replace(placeholder_single, str(value))
        return res
    
    def make_inputs(self, inputs: dict) -> str:
        """Apply inputs to the inputs template."""
        res = self.inputs
        for key, value in inputs.items():
            # Try both single and double braces for compatibility
            # Double braces: {{key}} (used in f-strings)
            placeholder_double = "{{" + key + "}}"
            # Single braces: {key} (standard format)
            placeholder_single = "{" + key + "}"
            
            if placeholder_double in res:
                res = res.replace(placeholder_double, str(value))
            elif placeholder_single in res:
                res = res.replace(placeholder_single, str(value))
        return res
