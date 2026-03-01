"""add search vector trigger

Revision ID: 859d228d38ca
Revises: f95a2e7c34d9
Create Date: 2026-03-01 12:52:17.318941

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '859d228d38ca'
down_revision: Union[str, None] = 'f95a2e7c34d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a function that updates the search_vector column
    op.execute("""
        CREATE OR REPLACE FUNCTION notes_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create a trigger that fires before insert or update on the notes table
    op.execute("""
        CREATE TRIGGER notes_search_vector_trigger
        BEFORE INSERT OR UPDATE OF title, body ON notes
        FOR EACH ROW
        EXECUTE FUNCTION notes_search_vector_update();
    """)

    # Backfill existing notes
    op.execute("""
        UPDATE notes SET search_vector =
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(body, '')), 'B');
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS notes_search_vector_trigger ON notes;")
    op.execute("DROP FUNCTION IF EXISTS notes_search_vector_update();")
