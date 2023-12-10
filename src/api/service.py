import os

from loguru import logger

from fastapi import Depends, UploadFile, WebSocket
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from .models import File
from .dao import FileDAO
from .config import ROOT_DIR, UPLOAD_DIR

from ..auth.models import User
from ..auth.service import DatabaseManager
from ..database import get_async_session
from ..utils import check_record_existence, get_unique_id


class FileCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db
        
    
    async def upload_file(self, token: str, file: UploadFile) -> File:
        
        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud
        
        try: 
            user_id = await token_service.get_access_token_payload(token)
            
            logger.info(f"User {user_id} creates file: {file.filename}")
            await self._ensure_upload_folder_exists(user_id)

            file_name, file_extension = file.filename.split('.')
            file_path = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id , f"{file_name}.{file_extension}")

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
                
                db_file = await FileDAO.add(
                self.db,
                schemas.CreateFile(
                    id=await get_unique_id(),
                    file_name=file_name,
                    file_extension=file_extension,
                    file_path=file_path,
                    user_id=user_id,
                )
            )

                self.db.add(db_file)
                await self.db.commit()
                await self.db.refresh(db_file)

            return db_file   
        
        except Exception as e:
            logger.opt(exception=e).critical("Error in upload_file")
            raise    
        
    
    async def get_file(self, token: str, file_path: str) -> str:
        
        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud
        
        user_id = await token_service.get_access_token_payload(token)
        
        await check_record_existence(self.db, User, user_id)
        
        logger.info(f"User {user_id} gets file by file_path: {file_path}")      
        
        try: 
            target_file = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id, file_path)
            
            return target_file  
                   
        except Exception as e:
            logger.opt(exception=e).critical("Error in get_file")
            raise
        
    async def delete_file(self, token: str, file_path: str) -> str:
        
        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud
        
        user_id = await token_service.get_access_token_payload(token)    
        await check_record_existence(self.db, User, user_id)
        
        logger.info(f"User {user_id} delete file by file_path: {file_path}")
        
        try: 
            
            target_file = os.path.join(ROOT_DIR, UPLOAD_DIR, user_id, file_path)
            
            if os.path.exists(target_file):
                os.remove(target_file)

            await FileDAO.delete(self.db, and_(File.user_id==user_id, File.file_path==file_path))
            self.db.commit()
            
            return {"Message": f"File {file_path} was deleted by user {user_id} successfully"}
        
        except Exception as e:
            logger.opt(exception=e).critical("Error in delete_file")
            raise
        
    @staticmethod
    async def _ensure_upload_folder_exists(user_id: str) -> None:
        upload_folder = os.path.join(ROOT_DIR, UPLOAD_DIR)
        user_folder = os.path.join(upload_folder, user_id)

        for folder in [upload_folder, user_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
            

class FileManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_crud = FileCRUD(db)

    async def commit(self):
        await self.db.commit()