# AI Internship Task - Domain-Specific PDF Summarization

## Overview
This project is designed to process PDF documents, generate domain-specific summaries and keywords, and store them in a MongoDB database. The pipeline handles PDFs of varying lengths and supports parallel processing for efficiency.

## Project Structure
- **PDF Ingestion & Parsing**: Extracts text and metadata from PDFs and classifies them as short, medium, or long based on the number of pages.
- **Summarization**: Uses a Transformer model (T5) to generate dynamic summaries based on the content.
- **Keyword Extraction**: Extracts domain-specific keywords using term frequency.
- **MongoDB Integration**: Stores document metadata, summaries, and keywords in a MongoDB collection.

## Features
- **Concurrency**: Process multiple PDFs simultaneously.
- **Error Handling**: Logs any errors that occur during processing.
- **Domain-Specific Summarization**: The summaries and keywords are tailored to the specific content of each document.

## Setup Instructions

### Prerequisites
- Python 3.x
- MongoDB (local or remote)
- Required libraries: `PyPDF2`, `transformers`, `pymongo`, `torch`, etc.

### Install the Required Libraries

Run the following command to install dependencies:

```bash
pip install -r requirements.txt
