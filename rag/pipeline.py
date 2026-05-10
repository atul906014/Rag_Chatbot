import os
import warnings
import logging
from functools import lru_cache

warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from .prompt import prompt_template as prompt
from langchain_ollama import ChatOllama

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("atul_resume_qa")


def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"{key} is required but not set in .env")
    return val

HF_TOKEN         = _require_env("HF_TOKEN")
HF_EMBEDDING_MODEL = _require_env("HF_EMBEDDING_MODEL")
EMBEDDING_API_URL  = os.getenv("EMBEDDING_API_URL")          # optional
FAISS_INDEX_PATH   = os.getenv("FAISS_INDEX_PATH", "faiss_index")


llm = ChatOllama(
    model="qwen2.5-coder:7b"
)


@lru_cache(maxsize=1)
def get_resume_documents():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    resume_path = os.path.join(BASE_DIR, "data", "Atul_Kumar_Resume_2.docx")
    logger.info("Loading resume from %s", resume_path)
    loader = Docx2txtLoader(resume_path)
    return loader.load()


@lru_cache(maxsize=1)
def _get_vector_store():
    embedding = HuggingFaceInferenceAPIEmbeddings(
        api_key=HF_TOKEN,
        model_name=HF_EMBEDDING_MODEL,
        api_url=EMBEDDING_API_URL if EMBEDDING_API_URL else None,
    )

    if not os.path.exists(FAISS_INDEX_PATH):
        logger.info("FAISS index not found, building from resume...")
        documents = get_resume_documents()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(documents)
        vector_store = FAISS.from_documents(chunks, embedding=embedding)
        vector_store.save_local(FAISS_INDEX_PATH)
        logger.info("FAISS index saved to %s", FAISS_INDEX_PATH)
    else:
        logger.info("Loading FAISS index from %s", FAISS_INDEX_PATH)
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings=embedding,
            allow_dangerous_deserialization=True,
        )

    return vector_store


def get_question(input: dict | str) -> str:
    if isinstance(input, dict):
        return input.get("question", "")
    return str(input)

def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _build_chain() -> RunnableWithMessageHistory:
    vector_store = _get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(get_question) | retriever | RunnableLambda(format_docs)
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    store: dict[str, ChatMessageHistory] = {}

    def get_session_history(session_id: str) -> ChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="question",       # key you send in invoke()
        history_messages_key="chat_history", # key MessagesPlaceholder expects
    )

    logger.info("RAG pipeline ready")
    return chain

chain_with_history = _build_chain()