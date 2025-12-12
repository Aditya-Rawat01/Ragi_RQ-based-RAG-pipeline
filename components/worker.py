from dotenv import load_dotenv
from openai import OpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from os import getenv
load_dotenv()


api_key = getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

embedding_model = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434/")

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="rag-agent-1" # must match already present collection.
)



def process_query(query:str):
    search_results = vector_db.similarity_search(query)


    context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])

    SYSTEM_PROMPT = f"""
    You are a helpfull AI Assistant who answere's user query based on the available context retrieved from a PDF file along with page_contents and page number.

    You should only ans the user based on the following context and navigate the user to open the right page number to know more.

    Context:
    {context}
    """

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": query
            }
        ]
    )

    return f"🤖: {response.choices[0].message.content}"

