from dotenv import load_dotenv
from google import genai
import os
from PyPDF2 import PdfReader
from prompt import PROMPT


load_dotenv()

class API:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"), 
        vertexai=True,
        project=os.getenv("GOOGLE_PROJECT_ID"),    
        location=os.getenv("GOOGLE_LOCATION"),
        )

    def generate_text(self, model="gemini-3-pro-preview", prompt=None):
        prompt = self.prompt if prompt is None else prompt
        response = self.client.generate_text(content=prompt, model=model)
        return response.text

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file) 
            pages = reader.pages              
            text = ""
            for page in pages:
                text += page.extract_text() 
            return text
        
    def generate_text_from_pdf(self, pdf_path, model="gemini-3-pro-preview"):
        text = self.extract_text_from_pdf(pdf_path)
        return self.generate_text(model=model, prompt=text)

    def get_text_from_pdf(self, pdf_path):
        pages = self.extract_text_from_pdf(pdf_path)
        text = ""
        for page in pages:
            text += page.extract_text()
        return text
    
