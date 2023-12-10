from .models import File
from .schemas import CreateFile, UpdateFile

from ..dao import BaseDAO


class FileDAO(BaseDAO[File, CreateFile, UpdateFile]):
    model = File