from fastapi import APIRouter, UploadFile, File

from secrets import token_hex

router = APIRouter()


@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    
    file_extinsion = file.filename.split('.').pop()
    file_name = token_hex(10)
    file_path = f"{file_name}.{file_extinsion}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"Message": "Upload was successfull", "file_path": file_path}
        