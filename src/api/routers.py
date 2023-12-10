from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from .service import FileManager


router = APIRouter()


@router.post("/upload_file")
async def upload_file(
    token: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
    ):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    return await file_crud.upload_file(token=token, file=file)


@router.get("/get_file/{file_path}")
async def get_file(
    token: str,
    file_path: str,
    db: AsyncSession = Depends(get_async_session)
    ):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    target_file = await file_crud.get_file(token=token, file_path=file_path)
    
    return FileResponse(target_file)


@router.delete("/delete_file")
async def delete_file(
    token: str,
    file_path: str,
    db: AsyncSession = Depends(get_async_session)
):
    
    file_manager = FileManager(db)
    file_crud = file_manager.file_crud
    
    return await file_crud.delete_file(token, file_path)
     
