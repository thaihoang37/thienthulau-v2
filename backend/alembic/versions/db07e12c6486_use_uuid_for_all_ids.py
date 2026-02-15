"""use uuid for all ids

Revision ID: db07e12c6486
Revises: 12e7533a8a18
Create Date: 2026-02-15 09:17:00.402687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'db07e12c6486'
down_revision: Union[str, Sequence[str], None] = '12e7533a8a18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop all foreign key constraints first
    op.drop_constraint('glossaries_first_chapter_id_fkey', 'glossaries', type_='foreignkey')
    op.drop_constraint('glossaries_book_id_fkey', 'glossaries', type_='foreignkey')
    op.drop_constraint('chapters_book_id_fkey', 'chapters', type_='foreignkey')

    # Drop unique constraints that reference FK columns
    op.drop_constraint('uq_chapters_book_id_order', 'chapters', type_='unique')
    op.drop_constraint('uq_glossaries_raw_type_book_id', 'glossaries', type_='unique')

    # Drop indexes on FK columns
    op.drop_index('ix_chapters_book_id', table_name='chapters')
    op.drop_index('ix_glossaries_book_id', table_name='glossaries')

    # Drop SERIAL default values before converting types
    op.alter_column('books', 'id', server_default=None)
    op.alter_column('chapters', 'id', server_default=None)
    op.alter_column('glossaries', 'id', server_default=None)

    # Drop old serial sequences
    op.execute('DROP SEQUENCE IF EXISTS books_id_seq CASCADE')
    op.execute('DROP SEQUENCE IF EXISTS chapters_id_seq CASCADE')
    op.execute('DROP SEQUENCE IF EXISTS glossaries_id_seq CASCADE')

    # Alter primary key columns to UUID using gen_random_uuid()
    op.alter_column('books', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=False,
               postgresql_using='gen_random_uuid()')

    op.alter_column('chapters', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=False,
               postgresql_using='gen_random_uuid()')

    op.alter_column('glossaries', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=False,
               postgresql_using='gen_random_uuid()')

    # Alter foreign key columns to UUID
    op.alter_column('chapters', 'book_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=False,
               postgresql_using='gen_random_uuid()')

    op.alter_column('glossaries', 'book_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=True,
               postgresql_using='gen_random_uuid()')

    op.alter_column('glossaries', 'first_chapter_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(),
               existing_nullable=True,
               postgresql_using='gen_random_uuid()')

    # Recreate foreign key constraints
    op.create_foreign_key('chapters_book_id_fkey', 'chapters', 'books', ['book_id'], ['id'])
    op.create_foreign_key('glossaries_book_id_fkey', 'glossaries', 'books', ['book_id'], ['id'])
    op.create_foreign_key('glossaries_first_chapter_id_fkey', 'glossaries', 'chapters', ['first_chapter_id'], ['id'])

    # Recreate unique constraints
    op.create_unique_constraint('uq_chapters_book_id_order', 'chapters', ['book_id', 'order'])
    op.create_unique_constraint('uq_glossaries_raw_type_book_id', 'glossaries', ['raw', 'type', 'book_id'])

    # Recreate indexes
    op.create_index('ix_chapters_book_id', 'chapters', ['book_id'], unique=False)
    op.create_index('ix_glossaries_book_id', 'glossaries', ['book_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop FK constraints
    op.drop_constraint('glossaries_first_chapter_id_fkey', 'glossaries', type_='foreignkey')
    op.drop_constraint('glossaries_book_id_fkey', 'glossaries', type_='foreignkey')
    op.drop_constraint('chapters_book_id_fkey', 'chapters', type_='foreignkey')

    op.drop_constraint('uq_chapters_book_id_order', 'chapters', type_='unique')
    op.drop_constraint('uq_glossaries_raw_type_book_id', 'glossaries', type_='unique')

    op.drop_index('ix_chapters_book_id', table_name='chapters')
    op.drop_index('ix_glossaries_book_id', table_name='glossaries')

    # Revert columns back to INTEGER (data will be lost)
    op.alter_column('glossaries', 'first_chapter_id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               postgresql_using='NULL')
    op.alter_column('glossaries', 'book_id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               postgresql_using='NULL')
    op.alter_column('glossaries', 'id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               postgresql_using='1')
    op.alter_column('chapters', 'book_id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               postgresql_using='1')
    op.alter_column('chapters', 'id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               postgresql_using='1')
    op.alter_column('books', 'id',
               existing_type=sa.UUID(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               postgresql_using='1')

    # Recreate FK constraints
    op.create_foreign_key('chapters_book_id_fkey', 'chapters', 'books', ['book_id'], ['id'])
    op.create_foreign_key('glossaries_book_id_fkey', 'glossaries', 'books', ['book_id'], ['id'])
    op.create_foreign_key('glossaries_first_chapter_id_fkey', 'glossaries', 'chapters', ['first_chapter_id'], ['id'])

    op.create_unique_constraint('uq_chapters_book_id_order', 'chapters', ['book_id', 'order'])
    op.create_unique_constraint('uq_glossaries_raw_type_book_id', 'glossaries', ['raw', 'type', 'book_id'])

    op.create_index('ix_chapters_book_id', 'chapters', ['book_id'], unique=False)
    op.create_index('ix_glossaries_book_id', 'glossaries', ['book_id'], unique=False)
