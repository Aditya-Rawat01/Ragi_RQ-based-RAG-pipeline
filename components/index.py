from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
import re
pathval = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=pathval)

docs = loader.load()
def clean_page_content(text:str):
    # Regex to replace 3 or more consecutive dots with a single space , this caused the ollamaEmbeddings to crash for chunk size of 1000
    # This fixes the "Table of Contents" crash
    text = re.sub(r'\.{3,}', ' ', text)
    
    # Also remove null bytes (common PDF artifact) just in case
    text = text.replace('\x00', '') 
    return text

for doc in docs:
    doc.page_content = clean_page_content(doc.page_content)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap = 200
)

chunks = text_splitter.split_documents(docs)
print(f"Total chunks to process: {len(chunks)}")
embedding_model = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434/")

# in case of any fatal error, uncomment this to see any embedding related issue 
# print("Starting safety check...")
# for i, doc in enumerate(chunks):
#     try:
#         # Try to embed just this one chunk
#         content = doc.page_content
#         print(f"Processing chunk {i}/{len(chunks)} (Length: {len(content)})...", end="\r")
        
#         # We perform a raw embed call to test it
#         embedding_model.embed_query(content)
        
#     except Exception as e:
#         print(f"\n\nCRITICAL FAILURE at Chunk {i}!")
#         print(f"Length: {len(content)}")
#         print("Content Start:", content[:100])
#         print("Content End:", content[-100:])
#         print("Error:", e)
#         break

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="rag-agent-1"
)