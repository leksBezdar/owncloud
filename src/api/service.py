import os

from loguru import logger

from fastapi import UploadFile
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import File

from . import schemas
from .dao import FileDAO, FolderDAO
from .config import ROOT_DIR, UPLOAD_DIR

from ..auth.service import DatabaseManager
from ..utils import get_unique_id


class FileCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db
        
    
    async def upload_file(self, token: str, file: UploadFile, folder_id: int) -> File:
               
        try: 
            await self._ensure_upload_folder_exists(user_id)         
            user_id = await self._get_user_id_from_token(token)        

            file_name, file_extension = file.filename.split('.')
            file_path = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id , f"{file_name}.{file_extension}")
            
            logger.info(f"User {user_id} creates file: {file.filename} into {file_path}")

            await self._create_file(file, file_path)
                
            db_file = await FileDAO.add(
                self.db,
                schemas.CreateFile(
                    id=await get_unique_id(),
                    file_name=file_name,
                    file_extension=file_extension,
                    file_path=file_path,
                    user_id=user_id,
                    folder_id=folder_id
                )
            )

            await self.db.commit()

            return db_file   
        
        except Exception as e:
            logger.opt(exception=e).critical("Error in upload_file")
            raise    
        
    
    async def get_file(self, token: str, file_path: str) -> str:
        
        user_id = await self._get_user_id_from_token(token)
        
        logger.info(f"User {user_id} gets file by file_path: {file_path}")      
        
        try: 
            target_file = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id, file_path)         
            return target_file  
                   
        except Exception as e:
            logger.opt(exception=e).critical("Error in get_file")
            raise
        
    async def delete_file(self, token: str, file_path: str) -> str:
        
        try: 
            user_id = await self._get_user_id_from_token(token)   
            logger.info(f"User {user_id} delete file by file_path: {file_path}")
            
            target_file = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id, file_path)
            
            if os.path.exists(target_file):
                os.remove(target_file)

            await FileDAO.delete(self.db, and_(File.user_id==user_id, File.file_path==file_path))
            self.db.commit()
            
            return {"Message": f"File {file_path} was deleted by user {user_id} successfully"}
        
        except Exception as e:
            logger.opt(exception=e).critical("Error in delete_file")
            raise
        
    async def _get_user_id_from_token(self, token: str):
        
        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud
        
        user_id = await token_service.get_access_token_payload(token)
        return user_id
    
    @staticmethod
    async def _create_file(file: UploadFile, file_path: str) -> None:     
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    
    @staticmethod
    async def _ensure_upload_folder_exists(user_id: str) -> None:
        upload_folder = os.path.join(ROOT_DIR, UPLOAD_DIR)
        user_folder = os.path.join(upload_folder, user_id)

        for folder in [upload_folder, user_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
            

class FolderCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    
    async def create_folder(self, folder: schemas.CreateFolder, token: str):
        
        user_id = await self._get_user_id_from_token(token)
        
        folder_path = await self._create_folder(folder.folder_name, folder.parent_folder_id)
        
        db_folder = await FolderDAO.add(
                self.db,
                schemas.CreateFolderDB(
                    id=await get_unique_id(),
                    user_id=user_id,
                    **folder.model_dump()
                )
            )

        await self.db.commit()
        
        return db_folder  
    
    async def _create_folder(self, folder_name: str, parent_folder_id: int = None):
        
        parent_folder_path = await self._get_folder_path(parent_folder_id)
        
        folder_path = os.path.join(parent_folder_path, folder_name)

        # Создаем папку, если она не существует
        os.makedirs(folder_path, exist_ok=True)
        
        return folder_path
    
    
    @staticmethod
    async def _get_folder_path(folder_id) -> str:
        ...
    
    async def _get_user_id_from_token(self, token: str) -> str:
        
        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud
        
        user_id = await token_service.get_access_token_payload(token)
        return user_id
            

class FileManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_crud = FileCRUD(db)

    async def commit(self):
        await self.db.commit()