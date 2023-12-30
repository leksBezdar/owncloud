from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class File(Base):
    __tablename__ = 'files'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    file_path: Mapped[str] = mapped_column(nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_extension: Mapped[str] = mapped_column(nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    is_favorite: Mapped[bool] = mapped_column(nullable=False, server_default='False')
    is_deleted: Mapped[bool] = mapped_column(nullable=False, server_default='False')
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    
    folder_id: Mapped[int] = mapped_column(ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)
    
class DeletedFile(Base):
    __tablename__ = 'deleted_files'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    file_id: Mapped[str] = mapped_column(ForeignKey('files.id', ondelete='CASCADE'))
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at: Mapped[int]
    
class Folder(Base):
    __tablename__ = 'folders'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    folder_name: Mapped[str] = mapped_column(nullable=False)
    folder_path: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(True), server_default=func.now()) 
    
    parent_folder_id: Mapped[int] = mapped_column(ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)