from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv  
from huggingface_hub import InferenceClient
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from functools import lru_cache

import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("atul_resume_qa")

load_dotenv()

app = FastAPI(title="Atul's Resume Q&A",description="An chatbot to answer questions about Atul's resume using a HuggingFace model.", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize HuggingFace client
client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
)

@lru_cache(maxsize=1)
def get_vector_store():
    folder_path = "faiss_index"
    if not os.path.exists(folder_path):
        resume_context = load_resume_context()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""])
        chunks = splitter.create_documents([resume_context])
        vector_store = FAISS.from_documents(chunks, HuggingFaceEmbeddings(model_name=os.environ["HF_EMBEDDING_MODEL"]))
        vector_store.save_local(folder_path)
    else:
        vector_store = FAISS.load_local(folder_path, HuggingFaceEmbeddings(model_name=os.environ["HF_EMBEDDING_MODEL"]), allow_dangerous_deserialization=True)
    return vector_store


@lru_cache(maxsize=1)
def get_resume_context():
    return load_resume_context()

def generate_context(question):
    logger.info("Generating context for question: %s", question)
   
    # load the FAISS vector store from local disk if it exists, otherwise create it and save it for future use
    resume_context = get_resume_context()
    vector_store = get_vector_store()   
    relevant_chunks = vector_store.similarity_search(question, k=5)
    logger.info("Retrieved %d relevant chunks", len(relevant_chunks))
    if not relevant_chunks:
        logger.warning("No relevant chunks found; using full resume context")
        return resume_context
    context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
    return context


    
    


# Resume context

def load_resume_context():
    resume_path = "data/Atul_Kumar_Resume_2.docx"
    logger.info("Loading resume document from %s", resume_path)
    loader = Docx2txtLoader(resume_path)
    documents = loader.load()
    return documents[0].page_content
    



    

# Pydantic model for request
class QuestionRequest(BaseModel):
    question: str

def call_hf(prompt_value):
    text = prompt_value.to_string()
    logger.info("Calling HuggingFace model with prompt length %d", len(text))
    completion = client.chat.completions.create(
        model=os.environ["HF_MODEL"],
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
    )
    return completion.choices[0].message.content

prompt_template = ChatPromptTemplate.from_template(
    f"""You are an AI assistant knowledgeable about Atul's professional profile.

Resume Context:
{{context}}

Instructions:
- Use ONLY the information contained in the Resume Context.
- If the answer is not directly available in the context, respond exactly: I don't have that information.
- Do not invent facts or add information not supported by the resume.
- Keep answers concise and factual.

Question:
{{question}}

Answer:"""
)

chain = prompt_template | RunnableLambda(call_hf) | StrOutputParser()

@app.get('/')
def index():
    return {"message": "Atul's Resume Q&A API", "docs": "/docs"}

@app.post('/chat')
def chat(request: QuestionRequest):
    logger.info("Received chat request: %s", request.question)
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        context = generate_context(request.question)
        if not context.strip():
            logger.warning("Generated context is empty for question: %s", request.question)
            context = "No relevant information found in the resume."
        
        response = chain.stream({"question": request.question, "context": context})
        full_response = ''.join(response)
        logger.info("Returning response of length %d", len(full_response))
        return {"question": request.question, "answer": full_response}
    except Exception as e:
        logger.exception("Error handling chat request")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/predefined-questions')
def get_predefined_questions():
    questions = [
    "What are Atul's main skills?",
    "What certifications does Atul have?",
    "What is Atul's educational background?",
    "Tell me about Atul's experience",
    "What projects has Atul worked on?",
    "What is Atul's expertise in Agentic AI?",
    ]
    return {"questions": questions}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
