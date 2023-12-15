from pydantic import BaseModel


class FileBase(BaseModel):
    file_name: str
    file_extension: str
    file_path: str
    user_id: str
    folder_id: int | None = None


class CreateFile(FileBase):
    id: str 
    

class UpdateFile(FileBase):
    file_name: str | None = None 
    file_extension: str | None = None 


class FolderBase(BaseModel):
    folder_name: str
    parent_folder_id: int | None = None

class CreateFolder(FolderBase):
    pass
    
class CreateFolderDB(CreateFolder):
    id: int
    user_id: str
    
class UpdateFolder(BaseModel):
    pass