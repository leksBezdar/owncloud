from pydantic import BaseModel


class FileBase(BaseModel):
    file_name: str
    file_extension: str
    file_path: str
    user_id: str


class CreateFile(FileBase):
    id: str 
    

class UpdateFile(FileBase):
    file_name: str | None = None 
    file_extension: str | None = None 