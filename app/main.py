from fastapi import FastAPI

app = FastAPI(title="Jenkins Demo API")

@app.get("/")
def read_root():
    return {"message": "CI/CD Pipeline Running Successfully!"}

@app.get("/health")
def health():
    return {"status": "ok"}
