import streamlit as st
from pdf2text import convert_pdf_to_text
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index import VectorStoreIndex
import os
import re
import threading
import time
from pathlib import Path

def find_page_number(node_text, document_path):
    search_text = node_text[:30]
    
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()

    position = content.find(search_text)

    if position == -1:
        return None

    subsequent_content = content[position:]
    page_match = re.search(r'Page: (\d+)', subsequent_content)

    if page_match:
        return int(page_match.group(1))
    else:
        return None

@st.cache_resource()
def load_data_and_index():
    filename_fn = lambda filename: {'file_name': filename}
    documents = SimpleDirectoryReader('Squire_GPT/Library/TEXT', file_metadata=filename_fn).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(max_nodes=6, max_tokens=500)
    return index, query_engine, [doc['file_name'] for doc in documents]  # Return the filenames of loaded documents


def get_response(user_query, query_engine):
    response = query_engine.query(user_query)
    node_texts = [node.node.text[:30] for node in response.source_nodes]
    filenames = [node.node.metadata['file_name'] for node in response.source_nodes]

    # Extracting page numbers using the `find_page_number` function
    pages = [find_page_number(node_text, Path(f)) for node_text, f in zip(node_texts, filenames)]
    sources = [(f, p) for f, p in zip(filenames, pages) if p is not None]
    
    return response.response, sources

def process_pdfs(pathtoPDF, pathtoText, status):
    try:
        convert_pdf_to_text(pathtoPDF, pathtoText)
        status[0] = "Processing complete!"
    except Exception as e:
        status[0] = f"Error occurred during processing: {str(e)}"

# Ensure that required directories exist
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)



def spearhead_library():
    st.title("SpearHead_Library")
    st.markdown("Welcome to SpearHead_Library! This tool allows you to search through a collection of documents with natural language. It will cite the source of the information and the page number where it was found. Processing may take a few minutes for larger PDFs.")

    ensure_directory_exists("Squire_GPT/Library/PDF")
    ensure_directory_exists("Squire_GPT/Library/TEXT")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        with open(os.path.join("Squire_GPT/Library/PDF", uploaded_file.name), "wb") as file:
            file.write(uploaded_file.getbuffer())
        st.success(f"{uploaded_file.name} has been uploaded successfully!")

    pdf_folder_path = 'Squire_GPT/Library/PDF'
    pdf_files = os.listdir(pdf_folder_path) if os.path.exists(pdf_folder_path) else []

    # Initialize session state
    if "show_textbox" not in st.session_state:
        st.session_state.show_textbox = False

    if "processed" not in st.session_state:
        st.session_state.processed = False

    # Initialize status
    status = [None]

    if pdf_files and not st.session_state.processed:
        if st.button("Process"):
            pathtoPDF = pdf_folder_path
            pathtoText = 'Squire_GPT/Library/TEXT'
            status_box = st.empty()
            processing_thread = threading.Thread(target=process_pdfs, args=(pathtoPDF, pathtoText, status))
            processing_thread.start()
            progress_bar = st.progress(0)
            
            while processing_thread.is_alive():
                time.sleep(0.1)
                progress_bar.progress(50)
            
            processing_thread.join()
            progress_bar.empty()  # Remove the progress bar
            status_box.write(status[0])  # Update the UI from the main thread
            st.session_state.processed = True
            st.session_state.show_textbox = True
    index, query_engine, loaded_pdfs = load_data_and_index()  # Load the data and get the loaded pdf filenames
    
    st.write("PDFs Loaded into Vector DB:", ', '.join([Path(pdf).stem for pdf in loaded_pdfs]))  # Display the loaded pdf names


    if st.session_state.show_textbox:
        user_query = st.text_input("Enter your question:")

        index, query_engine = load_data_and_index()

        if user_query:
            response_text, sources = get_response(user_query, query_engine)

            # Displaying filenames and their respective pages
            source_strings = [f"{Path(f).stem} (Page: {p})" for f, p in sources]

            st.write(response_text)
            st.write("Sources:", ', '.join(source_strings))
        else:
            st.write("Put new Questions into the Text box and press Enter. Delete old one before entering new one.")


if __name__ == "__main__":
    spearhead_library()
