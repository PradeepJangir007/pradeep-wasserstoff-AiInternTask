import os
import fitz  # PyMuPDF for PDF processing
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
import json
import logging
from collections import Counter
import re
import time
import nltk
from nltk.corpus import stopwords
from transformers import T5ForConditionalGeneration, T5Tokenizer
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small')

client = MongoClient('mongodb://localhost:27017/')
db = client['pdf_pipeline']
collection = db['pdf_metadata']

# Function to read PDF content

def extract_metadata(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        pdf_metadata = {
            'name': os.path.basename(pdf_path),
            'path': pdf_path,
            'size': f'{(os.path.getsize(pdf_path))/(1024*1024)} Mb',
            'num_pages': doc.page_count,
            'pdf_type': 'Long PDFs' if doc.page_count > 30 else 'Medium PDFs' if 10 <= doc.page_count <= 30 else 'Short PDFs',
            'status' : "pending"  
        }
        doc.close()
        return pdf_metadata
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {str(e)}")
        return None

def ingest_pdfs(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    pdf_metadata_list = []

    # Process PDFs in parallel
    with ThreadPoolExecutor() as executor:
        for metadata in executor.map(extract_metadata, pdf_files):
            if metadata:
                # Insert the metadata into MongoDB
                collection.insert_one(metadata)
                pdf_metadata_list.append(metadata)
    
    return pdf_metadata_list


def summarize_text(text, max_length=700, min_length=40):
    # Prepare the text input for the model
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    # Generate summary with specified constraints
    summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=2, early_stopping=True)

    # Decode the generated tokens into the final summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary.strip()

def extract_keywords(text, num_keywords=5):
    words = re.findall(r'\w+', text.lower())  # Find words and convert to lowercase
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words and word.isalpha()]# remove the stopword and numerical word
    common_words = Counter(filtered_words).most_common(num_keywords)
    keywords = [word for word, count in common_words]
    return keywords

def process_pdf(pdf_metadata):
    try:
        pdf_path=pdf_metadata['path']
        doc = fitz.open(pdf_path)  # Open the PDF file
        total_pages = doc.page_count
        summary = ""
        keywords=set()
        chunk_size=250
        # Process pages in chunks
        for i in range(0, total_pages, chunk_size):
            chunk_text = ""

            # Loop through each page in the current chunk
            for page_num in range(i, min(i + chunk_size, total_pages)):
                page = doc.load_page(page_num)  # Load each page individually
                chunk_text += page.get_text() 
            # Summarization and keyword extraction
            summary += summarize_text(chunk_text) + ' '
            keywords=keywords.union(set(extract_keywords(chunk_text)))
        doc.close()
        keywords=list(keywords)
        # Update MongoDB with summary and keywords
        collection.update_one(
        {"name": os.path.basename(pdf_path)},
        {"$set": {"summary": summary, "keywords": keywords, "status": "processed"}}
    )
        chunk_text=''
        summary=''
    except Exception as e:
        logging.error(f"Error processing PDF {pdf_metadata['path']}: {str(e)}")

def process_pdfs_in_parallel(pdf_metadata_list):
    # Process PDFs concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(process_pdf, pdf_metadata_list)

def main(folder_path):
    start=time.time()
    # Step 1: Ingest PDFs and store metadata in MongoDB
    pdf_metadata_list = ingest_pdfs(folder_path)

    # Step 2: Process each PDF (summarization and keyword extraction)
    process_pdfs_in_parallel(pdf_metadata_list)
    end=time.time()

    # Fetch all documents from the collection
    documents = collection.find()
    # Convert documents to a list of dictionaries
    documents_list = list(documents)
    return(documents_list)
                                


