from fastapi import FastAPI, Query
from components.redis_client import queue
from components.worker import process_query
app = FastAPI()


@app.get("/")
def pingpong():
    return {"msg":"ok"}


@app.post("/chat")
def chat(
    query:str = Query(..., description="chat query of the user")
):
    
    job = queue.enqueue(process_query, query)


    return {"status":"queued", "job_id": job.id}



@app.post("/job-status")
def status(
    job_id:str = Query(..., description="job id")
):
    job = queue.fetch_job(job_id)
    if not job:
        return {"msg": "job not found"}
    result = job.return_value()
    return {"result": result}