from fastapi import APIRouter, Depends, UploadFile, File

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from .service import FileManager
from . import schemas

router = APIRouter()


@router.post("/upload_file")
async def upload_file(
    token: str,
    folder_id: int = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
    ):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    return await file_crud.upload_file(token=token, file=file, folder_id=folder_id)

@router.post("/create_folder")
async def create_folder(
    token: str,
    folder_data: schemas.CreateFolder,
    db: AsyncSession = Depends(get_async_session)
):
    
    file_manager = FileManager(db)
    folder_crud = file_manager.folder_crud
    
    return await folder_crud.create_folder(folder=folder_data, token=token)


@router.get("/get_file/{file_id}")
async def get_file(
    file_id: str,
    token: str,
    db: AsyncSession = Depends(get_async_session)
):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    target_file = await file_crud.get_file(token=token, file_id=file_id)
    
    return FileResponse(target_file)


@router.get("/get_folders")
async def get_folders(
    token: str, 
    folder_id: int = None, 
    db: AsyncSession = Depends(get_async_session)
):
    
    folder_manager = FileManager(db)
    folder_crud = folder_manager.folder_crud
    
    target_folder = await folder_crud.get_folders(token=token, folder_id=folder_id)
    
    return target_folder


@router.get("/get_folder_files")
async def get_folder_files(
    token: str,
    folder_id: int = None,
    db: AsyncSession = Depends(get_async_session)
):
        
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    return await file_crud.get_folder_files(token=token, folder_id=folder_id)
    
    
@router.delete("/delete_file")
async def delete_file(
    token: str,
    file_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    return await file_crud.delete_file(token, file_id)

@router.delete("/delete_folder")
async def delete_folder(
    token: str, 
    folder_id: int, 
    db: AsyncSession = Depends(get_async_session)
):
    
    file_manager = FileManager(db)
    folder_crud = file_manager.folder_crud

    return await folder_crud.delete_folder(token, folder_id)