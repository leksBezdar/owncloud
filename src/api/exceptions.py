from fastapi import HTTPException


class FolderAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Folder already exists")