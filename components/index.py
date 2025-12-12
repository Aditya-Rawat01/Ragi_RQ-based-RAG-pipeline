from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

pathval = Path(__file__).parent / "nodejs.pdf"

# loading the file into the program
loader = PyPDFLoader(file_path=pathval)

doc = loader.load()


# coverting the file to chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap = 400
)

chunks = text_splitter.split_documents(doc)


embedding_model = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434/")



vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="rag-agent-1"
)