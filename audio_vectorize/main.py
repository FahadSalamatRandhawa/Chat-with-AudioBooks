from fastapi import FastAPI,Request,HTTPException,UploadFile,File,Body,Form,status
from fastapi.responses import RedirectResponse,JSONResponse
#from starlette.middleware.sessions import SessionMiddleware

from audio_vectorize.Model__Speech_Recognition import SpeechRecognitionModel
from audio_vectorize.Model__FileManagement_PostgressSQL import FileManagementModel
from audio_vectorize.Model__VectorDatabase_MongoDBAtlas import MongoDBAtlas, Collection
from audio_vectorize.Model__Embedding_HuggingFace import HuggingFaceEmbeddingsModel

from typing import List,Any

import os
from dotenv import load_dotenv, find_dotenv

audio_file_types = {
    'WAV',  # Windows container format
    'MP3',  # Popular lossy format
    'AAC',  # Advanced lossy format
    'OGG',  # Open-source lossy format
    'FLAC', # Free lossless format
    'ALAC', # Apple lossless format
    'PCM',  # Uncompressed audio format
    'AIFF', # Mac container format
    'WMA'   # Microsoft format, both lossy and lossless
}

app = FastAPI()

@app.on_event("startup")
async def startup_event():

    _:bool=load_dotenv(find_dotenv())

    global SpeechToTextModel; global FilesDatabase; global VectorDatabase; global embeddings
    SpeechToTextModel=SpeechRecognitionModel()
    FilesDatabase=FileManagementModel(os.getenv('NEON_CONNECTION_STRING'))
    FilesDatabase.createTable()

    VectorDatabase=MongoDBAtlas(os.getenv('MONGODBATLAS_CONNECTION_STRING'))

    embeddings=HuggingFaceEmbeddingsModel()

@app.get("/api")
def hello_world():
    return {"message": "Hello World"}


@app.post("/api/audio/upload")
async def uploadAudio(audiofiles:List[UploadFile]=File(...),database_id:str=Form(...),collection_id:str=Form(...),chunk_size:int=Form(...),chunk_overlap:int=Form(...)):
    successful:List[str]=[]
    print("POST : upload files",len(audiofiles))

    # get db and collection name using id's
    database=FilesDatabase.getDatabase(database_id)
    if not database:
        raise HTTPException(status_code=410, detail="No database")
    collection=FilesDatabase.getCollection(collection_id)
    if not collection:
        raise HTTPException(status_code=410, detail="No collection")
    try:
        for file in audiofiles:
            print(file)
            transcription=await SpeechToTextModel.audioToText(file)
            print(transcription)
            uploadedFile=FilesDatabase.addFile(file,collection_id)
            metadata=[{"id":uploadedFile.id}]
            
            if uploadedFile:
                result=VectorDatabase.Insert_Files(transcription,metadata,database.name,collection.name,embeddings,"hf_embeddings",chunk_size,chunk_overlap)
                successful.append(file.filename)
                print("\n-----------------------------------------------------------------------\n")

        return {"success":True,"message":"files uploaded","successful":successful,"unsuccessful":len(audiofiles)-len(successful)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=f"Error in uploading audio Error={e}, {len(successful)}/{len(audiofiles)} successfuly uploaded : List {successful}")

@app.put("/api/audio/update")
async def updateAudio(audiofiles:List[UploadFile]=File(...),database_id:str=Form(...),collection_id:str=Form(...),file_id:str=Form(...),chunk_size:int=Form(...),chunk_overlap:int=Form(...)):
    successful:List[str]=[]
    print("POST : upload files",len(audiofiles))

    # get db and collection name using id's
    database=FilesDatabase.getDatabase(database_id)
    if not database:
        raise HTTPException(status_code=410, detail="No database")
    collection=FilesDatabase.getCollection(collection_id)
    if not collection:
        raise HTTPException(status_code=410, detail="No collection")
    try:
        for file in audiofiles:
            transcription=await SpeechToTextModel.audioToText(file)
            print(transcription)
            successful.append(file.filename)
            updated=VectorDatabase.Update_Files(transcription,file_id,database.name,collection.name,embeddings,"hf_embeddings",chunk_size,chunk_overlap)

            return {"success":True,"message":"files updated"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error in updating audio {len(successful)}/{len(audiofiles)} successfuly updated : List {successful}")
    return {"message":"files updated"}

@app.delete("/api/audio/{id}")
def deleteAudio(id:str):
    try:
        print("DELETE : FastAPI delete")
        FilesDatabase.deleteFile(id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error in deleting audio")


# VectorStore Collection Management

@app.get("/api/FileManagement/database_and_collections")
def getDatabaseAndCollections():
    DBAndCollections= FilesDatabase.getDatabasesAndCollections()
    print(DBAndCollections)

    return {"success":True,"message":"databases and collections","databases":DBAndCollections}

@app.post("/api/FileManagement/create/database")
def createDatabase(email:str=Body(...),database:str=Body(...)):
    try:
        database= FilesDatabase.createDatabase(email,database)
        return {"success":True,"message":"created database","database":database}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error {e}")
    
@app.post("/api/FileManagement/create/collection")
def createCollection(name:str=Body(...), database_id:str=Body(...)):
    try:
        collection= FilesDatabase.createCollection(name, database_id)
        return {"success":True,"message":"created collection","collection":collection}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error {e}")
    


@app.post("/api/testing/documentcreation")
def createDocument(textdata:str=Body(...,embed=True)):
    print("Testsing Doc creation",textdata)
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    doc = text_splitter.create_documents([textdata],[{"id":"fileid"}])
    print(doc)
    docs=text_splitter.split_documents(doc)
    print(len(docs))
    # metadatalist=[{"id":index} for index,_ in enumerate(texts)]
    
    print(docs)