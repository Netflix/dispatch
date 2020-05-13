import uvicorn

if __name__ == "__main__":
    uvicorn.run("dispatch.main:app", host="0.0.0.0")
