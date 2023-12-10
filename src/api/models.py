from sqlalchemy import ForeignKey
from ..database import Base 
from sqlalchemy.orm import Mapped, mapped_column


class File(Base):
    __tablename__ = 'files'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    file_path: Mapped[str] = mapped_column(nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    file_type: Mapped[str] = mapped_column(nullable=False)
    