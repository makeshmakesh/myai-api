
#pylint:disable=all
from fastapi import FastAPI, File, UploadFile, HTTPException,Form
from sqlalchemy.orm import Session
from mangum import Mangum
from fastapi.responses import JSONResponse
import shutil
from pinecone import Pinecone

app = FastAPI(title="Myai API", description="API for managing myai")


def get_assistant(assistant_name, pinecone_api_key):
    """
    Creates or retrieves a Pinecone assistant.
    
    Args:
        assistant_name (str): Name of the assistant to retrieve or create
        pinecone_api_key (str): API key for Pinecone authentication
        
    Returns:
        Pinecone assistant object or redirects to error page on failure
    """
    pinecone_client = Pinecone(api_key=pinecone_api_key)
    try:
        return pinecone_client.assistant.Assistant(
            assistant_name=assistant_name,
        )
    except Exception as error:
        print("Error", error)
        return None

@app.get("/documents")
def read_root():
    return {"message": "Welcome to the myai-api"}

@app.post("/documents/assitant-file")
async def upload_file(
    apikey: str = Form(...),
    username: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        save_path = f"/tmp/{file.filename}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"Received file: {file.filename}")
        pinecone_assistant = get_assistant(assistant_name=username, pinecone_api_key=apikey)
        
        if pinecone_assistant is None:
            return JSONResponse(content={"message": "Pinecone assistant not found, please check apikey", "apikey": apikey})
        
        response = pinecone_assistant.upload_file(file_path=save_path, timeout=None)
        return JSONResponse(content={"message": "File uploaded successfully", "filename": file.filename})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/documents/assitant-file")
async def delete_file(
    apikey: str = Form(...),
    username: str = Form(...),
    file_id: str = Form(...)
):
    try:
        pinecone_assistant = get_assistant(assistant_name=username, pinecone_api_key=apikey)
        
        if pinecone_assistant is None:
            return JSONResponse(content={"message": "Pinecone assistant not found, please check apikey", "apikey": apikey})
        
        pinecone_assistant.delete_file(file_id=file_id)
        return JSONResponse(content={"message": "File deleted successfully", "file_id": file_id})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")




# Handler for AWS Lambda
handler = Mangum(app)