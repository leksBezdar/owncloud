"""add folder

Revision ID: 486087db5814
Revises: 029ecd812979
Create Date: 2023-12-14 20:38:33.875310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '486087db5814'
down_revision: Union[str, None] = '029ecd812979'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('folders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('folder_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('parent_folder_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_folder_id'], ['folders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_folders_id'), 'folders', ['id'], unique=False)
    op.add_column('files', sa.Column('folder_id', sa.Integer(), nullable=True))
    op.drop_constraint('files_file_name_key', 'files', type_='unique')
    op.create_foreign_key(None, 'files', 'folders', ['folder_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.create_unique_constraint('files_file_name_key', 'files', ['file_name'])
    op.drop_column('files', 'folder_id')
    op.drop_index(op.f('ix_folders_id'), table_name='folders')
    op.drop_table('folders')
    # ### end Alembic commands ###