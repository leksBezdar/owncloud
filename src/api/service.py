import os

from loguru import logger

from fastapi import UploadFile
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import File, Folder

from . import schemas, exceptions
from .dao import FileDAO, FolderDAO
from .config import ROOT_DIR, UPLOAD_DIR

from ..auth.service import DatabaseManager
from ..utils import get_unique_id


class PathService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.root_path = f"{ROOT_DIR}{UPLOAD_DIR}"

    async def get_folder_path(self, parent_folder_id: int, user_id: str) -> str:

        if parent_folder_id is None:
            return os.path.join(self.root_path, user_id)

        parent_folder = await FolderDAO.find_one_or_none(self.db, and_(
            Folder.id == parent_folder_id, Folder.user_id == user_id))

        if not parent_folder:
            raise exceptions.FolderWasNotFound

        return parent_folder.folder_path
    
    async def get_file_path(self, file_id: int, user_id: str) -> str:
        
        file = await FileDAO.find_one_or_none(self.db, and_(
            File.id == file_id, File.user_id == user_id))
        
        if not file:
            raise exceptions.FileWasNotFound
        
        return file.file_path
    
    @staticmethod
    async def ensure_upload_folder_exists(user_id: str) -> None:
        upload_folder = os.path.join(ROOT_DIR, UPLOAD_DIR)
        user_folder = os.path.join(upload_folder, user_id)

        for folder in [upload_folder, user_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)


class FileCRUD:

    def __init__(self, db: AsyncSession, path_service: PathService):
        self.db = db
        self.path_service = path_service

    async def upload_file(self, token: str, file: UploadFile, folder_id: int) -> File:

        try:
            user_id = await self._get_user_id_from_token(token)
            await self.path_service.ensure_upload_folder_exists(user_id)
            
            folder_path = await self.path_service.get_folder_path(folder_id, user_id)
            file_name, file_extension = file.filename.split('.')
            file_path = os.path.join(folder_path, f"{file_name}.{file_extension}")

            logger.info(f"User {user_id} creates file: {file.filename} into {file_path}")

            await self._create_file(file, file_path)
            db_file = await self._upload_file(file_name, file_extension, file_path, user_id, folder_id)

            return db_file

        except Exception as e:
            logger.opt(exception=e).critical("Error in upload_file")
            raise e

    async def _upload_file(self, file_name, file_extension, file_path, user_id, folder_id) -> File:
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

    async def get_file(self, token: str, file_id: str) -> str:

        user_id = await self._get_user_id_from_token(token)

        logger.info(f"User {user_id} gets file {file_id}")

        try:
            target_file = await self.path_service.get_file_path(file_id, user_id)
            return target_file

        except Exception as e:
            logger.opt(exception=e).critical("Error in get_file")
            raise

    async def get_folder_files(self, token: str, folder_id: str) -> list[File]:

        user_id = await self._get_user_id_from_token(token)

        target_files = await FileDAO.find_all(self.db, and_(
            File.user_id == user_id,
            File.folder_id == folder_id))
        
        return target_files

    async def delete_file(self, token: str, file_id: str) -> str:

        try:
            file_path = await self.path_service.get_file_path(file_id)           
            user_id = await self._get_user_id_from_token(token)
            logger.info(f"User {user_id} deletes file by file_path: {file_path}")

            if os.path.exists(file_path):
                os.remove(file_path)
                await self._delete_file_db(user_id, file_path)    
                return {"Message": f"File {file_path} was deleted by user {user_id} successfully"}

            return {"Message": f"File {file_id} does not exist"}        

        except Exception as e:
            logger.opt(exception=e).critical("Error in delete_file")
            raise
        
    async def _delete_file_db(self, user_id: str, file_path: str) -> None:
        
        await FileDAO.delete(self.db, and_(user_id == File.user_id, file_path == File.file_path))
        await self.db.commit()

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


class FolderCRUD:

    def __init__(self, db: AsyncSession, path_service: PathService):
        self.db = db
        self.path_service = path_service

    async def create_folder(self, folder: schemas.CreateFolder, token: str):

        try:

            user_id = await self._get_user_id_from_token(token)
            folder_path = await self._create_folder(folder.folder_name, user_id, folder.parent_folder_id)

            db_folder = await self._create_folder_db(folder, user_id, folder_path)

            response = {"db_folder": db_folder, "folder_path": folder_path}
            return response

        except Exception as e:
            logger.opt(exception=e).critical("Error in create_folder")
            raise e

    async def _create_folder(self,folder_name: str, user_id: str, parent_folder_id: int = None):

        await self.path_service.ensure_upload_folder_exists(user_id)
        parent_folder_path = await self.path_service.get_folder_path(parent_folder_id, user_id)
        folder_path = os.path.join(parent_folder_path, folder_name)

        # Создаем папку, если она не существует
        os.makedirs(folder_path, exist_ok=False)

        return folder_path

    async def _create_folder_db(self, folder: schemas.CreateFolder, user_id: str, folder_path: str):
        
        db_folder = await FolderDAO.add(
                self.db,
                schemas.CreateFolderDB(
                    user_id=user_id,
                    folder_path=folder_path,
                    **folder.model_dump()
                )
            )
        await self.db.commit()      
        return db_folder

    async def get_folders(self, folder_id: int | None, token: str) -> list[Folder]:

        user_id = await self._get_user_id_from_token(token)
        
        folder = await FolderDAO.find_all(
            self.db, Folder.parent_folder_id == folder_id,
            Folder.user_id==user_id
        )

        return folder

    async def _get_user_id_from_token(self, token: str) -> str:

        db_manager = DatabaseManager(self.db)
        token_service = db_manager.token_crud

        user_id = await token_service.get_access_token_payload(token)
        return user_id
    
    async def delete_folder(self, token: str, folder_id: int) -> str:
        
        user_id = await self._get_user_id_from_token(token)      
        folder_path = await self.path_service.get_folder_path(folder_id, user_id)
        
        if os.path.exists(folder_path):
            os.remove(folder_path)
            await self._delete_folder_db(folder_id, user_id)
            return {"Message":f"Folder {folder_id} was deleted by user {user_id} successfully"}  
        
        return {"Message": f"folder {folder_id} does not exist"}           

    async def _delete_folder_db(self, folder_id, user_id):
         
        await FolderDAO.delete(self.db, and_(Folder.id == folder_id, Folder.user_id == user_id))
        await self.db.commit()

class FileManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._path_service = PathService(db)
        self.file_crud = FileCRUD(db, self._path_service)
        self.folder_crud = FolderCRUD(db, self._path_service)

    async def commit(self):
        await self.db.commit()
