from fastapi import FastAPI

app = FastAPI(title="JobTrail API")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "JobTrail API"}