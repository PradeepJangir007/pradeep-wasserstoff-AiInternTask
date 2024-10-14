import streamlit as st
import os
import fitz  # prumst for PDF processing
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
import mymodule


# Streamlit app layout
st.title("PDF Summarizer")
st.write("Upload a PDF file to generate a summary.")

# File upload functionality
path = st.text_input("folder path")
b=st.button('generate a summary')
if b==True:
    if __name__ == "__main__":
        start= time.time()
        ts=mymodule
        d=ts.main(path)
        end= time.time()
        st.write(f"PDF processing completed.\n In {round(end-start)} seconds")
        