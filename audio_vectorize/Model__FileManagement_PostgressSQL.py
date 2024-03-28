from typing import Optional

from sqlmodel import Field, SQLModel,UUID,create_engine,Session,Uuid,select,update,Relationship
from fastapi import UploadFile
import uuid

from datetime import datetime

class User(SQLModel,table=True):
    email:str=Field(primary_key=True)
    created_at:datetime

    databases:list["Database"]=Relationship(back_populates="owner",sa_relationship_kwargs={"cascade":"all, delete-orphan"})

class Database(SQLModel, table=True):
    id:Optional[uuid.UUID]=Field(default_factory=uuid.uuid4, primary_key=True)
    email:str=Field(foreign_key="user.email")
    name:str=Field(unique=True)
    created_at:datetime

    owner:User=Relationship(back_populates="databases")
    collections:list["Collection"]=Relationship(back_populates="database",sa_relationship_kwargs={"cascade":"all, delete-orphan"})

class Collection(SQLModel, table=True):
    id:Optional[uuid.UUID]=Field(default_factory=uuid.uuid4, primary_key=True)
    name: str=Field(unique=True)
    database_id:uuid.UUID=Field(foreign_key="database.id")
    created_at:datetime

    database:Database=Relationship(back_populates="collections")
    files:list["File"]=Relationship(back_populates="collection",sa_relationship_kwargs={"cascade":"all, delete-orphan"})


class File(SQLModel,table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    size: int
    type: str
    format:str
    created_at: datetime
    updated_at: datetime
    collection_id:uuid.UUID=Field(foreign_key="collection.id")

    collection:Collection=Relationship(back_populates="files")

class FileManagementModel():
    def __init__(self,connection_string):
        """
            connects to db using env connection string
        """
        self.engine=create_engine(connection_string)

    def getFile(self, file_id:str):
        """
            returns file info from SQL database
        """
        print("Getting file ", file_id, " from postgresQL")
        with Session(self.engine) as session:
            file=session.get(File, file_id)
            return file if file else Exception("File not found")


    def addFile(self,file:UploadFile,collection_id:str):
        """
            adds file info to SQL database, auto handles file extension
        """
        
        print("Adding ",file.filename," to postgresQL")
        file_extension = file.filename.split('.')[-1]
    
        tempFile=File(name=file.filename,size=file.size,type=file.content_type,format=file_extension,created_at=datetime.now(),updated_at=datetime.now(),collection_id=collection_id)

        with Session(self.engine) as session:
            session.add(tempFile)
            session.commit()
            session.refresh(tempFile)
        return tempFile
    
        
    def updateFile(self, file:UploadFile,file_id):
        """
            updates file info in SQL database
        """
        print("Updating ", file.filename, " in postgresQL")
        file_extension = file.filename.split('.')[-1]
        try:
            with Session(self.engine) as session:
                #newFile=File(file_id,name=file.filename,size=file.size,type=file.content_type,format=file_extension,updated_at=datetime.now())
                stmt = (
                update(File)
                .where(File.id == file_id)
                .values(
                    name=file.filename,
                    size=file.size,
                    type=file.content_type,
                    format=file_extension,
                    updated_at=datetime.now()
                    )
                )
                session.exec(stmt)
                session.commit()
            print("Updated successfully\n")
            return file
        except Exception as e:
            print(e)
            raise Exception({"Error":e,"details":"Error in updating file"})
    
    def deleteFile(self, file:UploadFile):
        """
            deletes file info in SQL database
        """
        print("Deleting ", file.file, " in postgresQL")
        try:
            with Session(self.engine) as session:
                session.delete(file)
                session.commit()
            return {"details":"File deleted"}
        except Exception as e:
            print(e)
            raise Exception({"Error":e,"details":"Error in updating file"})

    # def createDatabaseAndCollection(self,email:str,database:str,collection:str):
    #     database=Database(email=email,name=database,created_at=datetime.now())
    #     collection=Collection(name=collection, email=email, created_at=datetime.now())

    #     print("Creating database and collection \n",database,"\n",collection)
    #     with Session(self.engine) as session:
    #         stmt=select(User).where(User.email==email)
    #         user=session.exec(stmt).first()
    #         if not user:
    #             session.add(User(email=email, created_at=datetime.now()))
    #             session.commit()
    #         session.add(database)
    #         session.commit()
    #         session.add(collection)
    #         session.commit()
    #         session.refresh(database)
    #         session.refresh(collection)
    #     print("Database and collection created \n", database, "\n", collection)
    #     return database, collection
    

# Databse Actions
            
    def getDatabase(self, database_id:str) -> Database:
        print("Fetching database with id ", database_id)
        with Session(self.engine) as session:
            stmt=select(Database).where(Database.id==database_id)
            database=session.exec(stmt).first()
            if database:
                print("Fetched successfully\n")
                return database
        print("Database not found with id ", database_id)
        raise Exception("Database not found")
    
    def createDatabase(self, email:str, database:str) -> Database:
        database=Database(email=email, name=database, created_at=datetime.now())

        print("Creating database \n", database)
        with Session(self.engine) as session:
            stmt=select(User).where(User.email==email)
            user=session.exec(stmt).first()
            if not user:
                session.add(User(email=email, created_at=datetime.now()))
                session.commit()
            session.add(database)
            session.commit()
            session.refresh(database)
        print("Database created \n", database)
        return database
    
    def deleteDatabase(self, database_id:str) -> Database:
        print("Deleting database with id ", database_id)
        with Session(self.engine) as session:
            stmt=select(Database).where(Database.id==database_id)
            database=session.exec(stmt).first()
            if database:
                session.delete(database)
                session.commit()
        print("Database deleted with id ", database_id)
        return database
        # print("Deleting database with id ", database_id)
        # with Session(self.engine) as session:
        #     session.delete(Database)
        #     session.commit()
        # print("Database deleted with id ", database_id)
        # return {"Success":True,"message":"Database deleted"}


## Collection actions
    def createCollection(self, name:str, database_id:str) -> Collection:
        collection=Collection(name=name, database_id=database_id, created_at=datetime.now())

        print("Creating collection \n", collection)
        with Session(self.engine) as session:
            session.add(collection)
            session.commit()
            session.refresh(collection)
        print("Collection created \n", collection)
        return collection
    
    def getCollection(self, collection_id:str) -> Collection:
        print("Fetching collection with id ", collection_id)
        with Session(self.engine) as session:
            stmt=select(Collection).where(Collection.id==collection_id)
            collection=session.exec(stmt).first()
            if collection:
                print("Fetched successfully\n")
                return collection
        print("Collection not found with id ", collection_id)
        raise Exception("Collection not found")
    
    def deleteCollection(self, collection_id:str)  -> Collection:
        print("Deleting collection with id ", collection_id)
        with Session(self.engine) as session:
            stmt=select(Collection).where(Collection.id==collection_id)
            collection=session.exec(stmt).first()
            if collection:
                session.delete(collection)
                session.commit()
        print("Collection deleted with id ", collection_id)
        return collection
    

    ## Database and Collection Actions
    
    def getDatabaseAndCollections(self, email:str):
        print("Fetching databases and collection with ",email)
        with Session(self.engine) as session:
            query=select(Database.collections).where(Database.email==email).join(Collection, isouter=False).distinct()
            result=session.exec(query).all()
            print("Fetched successfully\n")
            return result
    

    def createTable(self):
        """
            creates table in db
        """
        SQLModel.metadata.create_all(self.engine)
        