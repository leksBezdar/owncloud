from .models import File, Folder
from .schemas import CreateFile, CreateFolder, UpdateFile, UpdateFolder

from ..dao import BaseDAO


class FileDAO(BaseDAO[File, CreateFile, UpdateFile]):
    model = File


class FolderDAO(BaseDAO[Folder, CreateFolder, UpdateFolder]):
    model = Folder