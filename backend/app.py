from asyncio import wait_for, TimeoutError as AsyncTimeoutError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
from rag.pipeline import chain_with_history
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("atul_resume_qa")



app = FastAPI(title="Atul's Resume Q&A",description="An chatbot to answer questions about Atul's resume using a HuggingFace model.", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default_session"

@app.get('/')
def index():
    return {"message": "Atul's Resume Q&A API", "docs": "/docs"}

@app.post("/chat")
async def chat(request: QuestionRequest):
    try:
        response = await wait_for(
            chain_with_history.ainvoke(
                {"question": request.question},
                config={"configurable": {"session_id": request.session_id}}
            ),
            timeout=120  # 2 min for cold start
        )
        return {"question": request.question, "session_id": request.session_id, 
            "answer": response}
    
    except AsyncTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Model is taking too long. It may be loading — please retry in 30 seconds."
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error handling chat request")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
