from abc import ABC, abstractmethod
from typing import Type

from ..database import async_session_maker
from ..api.dao import FileDAO, FolderDAO
from ..auth.dao import UserDAO, RefreshTokenDAO


class IUnitOfWork(ABC):
    users: Type[UserDAO]
    refresh_tokens: Type[RefreshTokenDAO]
    files: Type[FileDAO]
    folders: Type[FolderDAO]
    
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()
        
        self.users: UserDAO(self.session)
        self.refresh_tokens: RefreshTokenDAO(self.session)
        self.files: FileDAO(self.session)
        self.folders: FolderDAO(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()