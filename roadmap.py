from fastapi import FastAPI

import requests
from bs4 import BeautifulSoup
import os
import selenium

from huggingface_hub import InferenceClient

from PyPDF2 import PdfReader
import pdfplumber

class RoadMap_sh:
    def __init__(self,user_topic) -> None:
        self.user_topic=user_topic

    def extract_text2(self):
        file_path=f"D:\\workplace\\AP\\projects\\coursoo\\{self.user_topic}_roadmap.pdf"
        text=""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    #extract_text2()

    def download_roadmap_pdf_direct(self):
        pdf_url = f"https://roadmap.sh/pdfs/roadmaps/{self.user_topic}.pdf"
        pdf_response = requests.get(pdf_url)
        
        if pdf_response.status_code == 200:
            pdf_filename = f"{self.user_topic}_roadmap.pdf"
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)
            print(f"Downloaded {pdf_filename}")
        else:
            print(f"Failed to download PDF from {pdf_url}")

    '''
    def download_roadmap_pdf(topic):
        # Construct the URL for the roadmap
        url = f"https://roadmap.sh/{topic}"
        
        # Send a GET request to the roadmap page
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup.prettify())
            

            # Find the download button (it's an <a> tag with a specific class)
            download_button = soup.find('a', class_='download-pdf')
            
            if download_button:
                # Get the PDF download link
                pdf_url = download_button['href']
                
                # Ensure the URL is absolute
                if not pdf_url.startswith('http'):
                    pdf_url = f"https://roadmap.sh{pdf_url}"
                
                # Download the PDF
                pdf_response = requests.get(pdf_url)
                
                if pdf_response.status_code == 200:
                    # Save the PDF to a file
                    pdf_filename = f"{topic}_roadmap.pdf"
                    with open(pdf_filename, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                    
                    print(f"Downloaded {pdf_filename}")
                    return pdf_filename
                else:
                    print(f"Failed to download PDF from {pdf_url}")
            else:
                print("Download button not found on the page.")
        else:
            print(f"Failed to access {url}")
    '''


class AI_Roadmap:
    #set HF_TOKEN="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"   #run in bash
    def __init__(self,user_topic) -> None:

        self.user_topic=user_topic
        self.HF_TOKEN = "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"

    # Initialize client with token
        self.llm_client = InferenceClient(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=self.HF_TOKEN,
            timeout=120,
        )

    def call_llm(self,client: InferenceClient, prompt: str):
        try:
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def clean_response(self,roadmap):
        cleaned_roadmap=(
        roadmap.replace("**", "")  # Remove bold markers
        .replace("|", "-")         # Replace pipes with hyphens
        .replace("_", "")          # Remove underscores
        .replace("  ", " ")        # Fix double spaces
        )
        return cleaned_roadmap

    # Test the call
    def get_roadmap(self):
        response = self.call_llm(self.llm_client, f"Generate a roadmap for {self.user_topic} with the EXACT structure of roadmaps on roadmap.sh. "
            "Format the roadmap as follows:\n"
            f"{self.user_topic} roadmap:\n"
            "1. **Main Section Title**\n"
            "   - Subcategory 1\n"
            "   - Subcategory 2\n"
            "   - Subcategory 3\n"
            "2. **Next Main Section**\n"
            "   - Subcategory 1\n"
            "   - Subcategory 2\n"
            "   - Subcategory 3\n"
            "Use ONLY plain text (no markdown, URLs, or explanations). "
            "Ensure ALL subcategories are SPECIFIC and SEARCHABLE."
            "DO NOT use more than 5 subcategories for each main section"
            )
        if response:
            roadmap=response.choices[0].message.content
            cleaned_roadmap=self.clean_response(roadmap)
            print(cleaned_roadmap)

            with open(f"{self.user_topic}_roadmap.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_roadmap)
        else:
            print("failed to generate a roadmap")

#user_topic="advanced chess coaching"
#roadmap1=AI_Roadmap(user_topic)
#roadmap1.get_roadmap()
