from pydantic import BaseModel
from typing import Dict


class DataModel(BaseModel):
    """Base model for data validation and serialization."""
    
    @classmethod
    def from_dict(cls, data_dict: Dict):
        """Create an instance from a dictionary."""
        return cls.model_validate(data_dict)
    
    def to_dict(self) -> Dict:
        """Convert the instance to a dictionary."""
        # return {k: v for k, v in self.model_dump().items() if v is not None}
        return self.model_dump(exclude_none=True)
    
    def to_string(self, indent: int = 2) -> str:
        """Convert the instance to a formatted string."""
        return self.model_dump_json(indent=indent, exclude_none=True)