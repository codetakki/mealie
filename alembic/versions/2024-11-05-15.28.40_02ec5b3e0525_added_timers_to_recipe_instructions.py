"""added timers to recipe instructions

Revision ID: 02ec5b3e0525
Revises: 3897397b4631
Create Date: 2024-11-05 15:28:40.528380

"""

import json
from datetime import datetime

import dateparser.search
import sqlalchemy as sa
from sqlalchemy import orm

from alembic import op
from mealie.core.root_logger import get_logger
from mealie.db.models._model_utils.guid import GUID
from mealie.services.parser_services.parser_utils.duration_parser import DurationParser

# revision identifiers, used by Alembic.
revision = "02ec5b3e0525"
down_revision: str | None = "3897397b4631"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

logger = get_logger()


# Intermediate table definitions
class SqlAlchemyBase(orm.DeclarativeBase):
    pass


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"

    id: orm.Mapped[GUID] = orm.mapped_column(GUID, primary_key=True, default=GUID.generate)
    recipe_id: orm.Mapped[GUID | None] = orm.mapped_column(GUID, index=True)
    text: orm.Mapped[str | None] = orm.mapped_column(sa.String, index=True)
    timers_json: orm.Mapped[str | None] = orm.mapped_column(sa.String)


def parse_instructions(session: orm.Session):
    SAMPLE_SIZE = 20

    # Fetch one instruction for each recipe
    distinct_recipe_ids = session.query(RecipeInstruction.recipe_id).distinct().limit(SAMPLE_SIZE).subquery()

    instruction_samples = (
        session.query(RecipeInstruction)
        .join(distinct_recipe_ids, RecipeInstruction.recipe_id == distinct_recipe_ids.c.recipe_id)
        .filter(RecipeInstruction.text.isnot(None), RecipeInstruction.text != "")
        .distinct(RecipeInstruction.recipe_id)
        .limit(SAMPLE_SIZE)
        .all()
    )

    # Extract the languages from each instruction
    results: list[list[tuple[str, datetime, str]]] = [
        dateparser.search.search_dates(instruction.text, add_detected_language=True)  # type: ignore
        for instruction in instruction_samples
        if instruction.text
    ]

    languages = {"en"}
    for result in results:
        if not result:
            continue

        for _, _, lang in result:
            languages.add(lang)

    # Parse all instructions using the detected languages
    logger.info(f"Detected languages: {languages}")

    duration_parser = DurationParser()
    for instruction in session.query(RecipeInstruction).all():
        if not instruction.text:
            continue

        timers = duration_parser.get_all_durations(instruction.text, languages=languages)
        instruction.timers_json = json.dumps(timers)

    session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("recipe_instructions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("timers_json", sa.String(), nullable=True))

    # ### end Alembic commands ###

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    try:
        logger.info("Parsing instruction timers")
        parse_instructions(session)
    except Exception:
        logger.exception("Failed to parse instruction timers; continuing with migration anyway")
        session.rollback()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("recipe_instructions", schema=None) as batch_op:
        batch_op.drop_column("timers_json")

    # ### end Alembic commands ###
