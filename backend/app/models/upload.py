from fastapi import FastAPI, File, UploadFile # type: ignore
import pdfplumber # type: ignore
import io
import os
from dotenv import load_dotenv # type: ignore
from openai import OpenAI   # type: ignore
from topic import generate_topics

load_dotenv('.env')
app = FastAPI()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Summarize the following text in brief: {text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; update as needed
        messages=[{"role": "user", "content": prompt}]
    )
    summarized_text = response.choices[0].message.content.strip()
    print("PDF summarized.")
    
    return generate_topics(summarized_text)
