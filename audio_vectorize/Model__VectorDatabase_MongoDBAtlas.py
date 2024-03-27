from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

from sqlmodel import SQLModel

class Collection(SQLModel):
    database:str
    collection:str


class MongoDBAtlas():
    def __init__(self, connection_string):
        self.client=MongoClient(connection_string)

    def Get_Database_And_Collection_Names(self):
        """
            returns all available database and collection names
            in the current database.
        """
        db_names = self.client.list_database_names()
        db_collection_mapping={}
        for db_name in db_names:
            db_collection_mapping[db_name]=self.client[db_name].list_collection_names()
        return db_collection_mapping
    
    def Add_Collection(self,collection:Collection):
        """
            Adds a collection and db, if db exists adds collection in it
        """
        try:
            print("Creating database and collection in MongoDBAtlas")
            db=self.client[collection.database]
            collextion=db[collection.collection]
            print("Successfully created ", collextion)

            return collextion
        except Exception as e:
            print(e)
            return {"success":False,"Error":e,"details":"Error in creating collection"}

    
    # File operations
        
    def Get_File(self, file_id, database, collection):
        """
        get file or document in MongoDBAtlast in specified collection, provide all parameters
        """
        print("\nInside Model__VectorDatabase_MongoDBAtlas : Get_File\n")
        try:
            collection=self.client[database][collection]
            print("Getting file from collection", collection)
            doc=collection.find({"id":file_id})
            print("Successfully got file from collection", collection)
            return doc
        except Exception as e:
            print("Error in Model MongoDBVector Get")
            print(e)
            return {"success":False,"Error":e,"details":"Error in getting file"}

    def Insert_Files(self,file,metadata,database,collection,embedding_model,index_name,chunk_size,chunk_overlap):
        """
        insert files or documents in MongoDBAtlast in specified collection, provide all parameters
        """
        print("\nInside Model__VectorDatabase_MongoDBAtlas : Insert_Files\n")

        try:
            collection=self.client[database][collection]
            print("Inserting in collection", collection)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            doc=text_splitter.create_documents([file],[metadata])
            docs=text_splitter.split_documents(doc)
            print(docs)
            MongoDBAtlasVectorSearch.from_documents(docs,embedding_model,collection=collection,index_name=index_name)
            print("Successfully inserted in collection", collection)
            return {"success":True,"details":"File successfully inserted in collection"}
        except Exception as e:
            print("Error in Model MongoDBVector Insert")
            print(e)
            return {"success":False,"Error":e,"details":"Error in uploading files"}
        
    def Update_Files(self, file, file_id, database, collection, embedding_model, index_name, chunk_size, chunk_overlap):
        """
        update files or documents in MongoDBAtlast in specified collection, provide all parameters
        """
        print("\nInside Model__VectorDatabase_MongoDBAtlas : Update_Files\n")
        metadata={"id":file_id}
        

        try:
            collection=self.client[database][collection]
            collection.delete_many({"id":file_id})
            print("Updating in collection", collection)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            doc=text_splitter.create_documents([file], [metadata])
            docs=text_splitter.split_documents(doc)
            print(docs)
            MongoDBAtlasVectorSearch.from_documents(docs, embedding_model, collection=collection, index_name=index_name)
            print("Successfully updated in collection", collection)
            return {"success":True,"details":"File successfully updated in collection"}
        except Exception as e:
            print("Error in Model MongoDBVector Update")
            print(e)
            raise Exception({"error":str(e)})
    
    def Delete_File(self,file_id,database,collection):
        """
        delete files or documents in MongoDBAtlast in specified collection, provide all parameters
        """
        print("\nInside Model__VectorDatabase_MongoDBAtlas : Delete_File\n")
        
        collection=self.client[database][collection]
        collection.delete_many({"id":file_id})
        print("Successfully deleted in collection", collection)
        return {"success":True,"details":"File successfully deleted in collection"}