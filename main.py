from fastapi import FastAPI

# Create a FastAPI instance
app = FastAPI()

# Define a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

# Define a dynamic endpoint
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

# POST endpoint example
@app.post("/create-item/")
def create_item(name: str, description: str = None):
    return {"name": name, "description": description}
