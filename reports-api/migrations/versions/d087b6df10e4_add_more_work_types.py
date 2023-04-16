"""add_more_work_types

Revision ID: d087b6df10e4
Revises: 839af60c1e2d
Create Date: 2023-04-12 10:42:10.669952

"""
from collections import defaultdict
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table, text

from pathlib import Path

# revision identifiers, used by Alembic.
revision = 'd087b6df10e4'
down_revision = '839af60c1e2d'
branch_labels = None
depends_on = None

def _filter_dataset(data, filter_key, filter_value):
    """Function to filter dataset by key and value"""
    return filter(lambda x: x[filter_key] == filter_value, data)

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    milestones_table = table(
        "milestones",
        column("id", sa.Integer),
        column("name", sa.String),
        column("kind", sa.String),
        column("phase_id", sa.Integer),
        column("milestone_type_id", sa.Integer),
        column("sort_order", sa.Integer),
        column("start_at", sa.Integer),
        column("duration", sa.Integer),
        column("auto", sa.Boolean),
    )

    phase_table = table(
        "phase_codes",
        column("id", sa.Integer),
        column("name", sa.String),
        column("work_type_id", sa.Integer),
        column("ea_act_id", sa.Integer),
        column("sort_order", sa.Integer),
        column("duration", sa.Integer),
        column("color", sa.String),
        column("legislated", sa.Boolean),
    )

    outcomes_table = table(
        "outcomes",
        column("id", sa.Integer),
        column("name", sa.String),
        column("milestone_id", sa.Integer),
        column("sort_order", sa.Integer),
        column("terminates_work", sa.Boolean),
    )
    # Get the connection object for executing queries

    conn = op.get_bind()

    file_path = Path(__file__, "../../data/002-work_types.json")

    with file_path.resolve().open("r") as f:
        data = json.load(f)
        phase_data = data["phases"]
        work_types = defaultdict(list)
        milestones_data = data["milestones"]
        outcomes_data = data["outcomes"]

        for phase in phase_data:
            work_types[phase["work_type_id"]].append(phase)

        for _, work_type_data in work_types.items():
            for index, phase in enumerate(work_type_data):
                phase_sort_order = index + 1
                phase_ref = phase.pop("id")
                phase["sort_order"] = phase_sort_order 
                name = phase["name"]
                work_type_id = phase["work_type_id"]
                conditions = (
                    f"WHERE name = '{name}' AND work_type_id = {work_type_id} "
                )
                query = text(f"SELECT id from phase_codes {conditions}")
                phase_obj = conn.execute(query, phase).fetchone()
                if phase_obj is None:
                    phase_obj = conn.execute(
                        phase_table.insert(phase).returning(
                            (phase_table.c.id).label("id")
                        )
                    )
                else:
                    conn.execute(
                        phase_table.update()
                        .where(phase_table.c.id == phase_obj.id)
                        .values(**phase)
                    )
                phase_id = phase_obj.id if hasattr(phase_obj,"id") else phase_obj.first()["id"]
                milestones = _filter_dataset(milestones_data, "phase_id", phase_ref)
                milestone_sort_order = 0
                for milestone in milestones:
                    milestone_sort_order += 1
                    milestone_ref = milestone.pop("id", None)
                    milestone["phase_id"] = phase_id
                    milestone["sort_order"] = milestone_sort_order
                    milestone["auto"] = milestone.get('auto', False)
                    conditions = f"WHERE phase_id={phase_id} AND milestone_type_id=:milestone_type_id AND kind='{milestone['kind']}' AND name=:name"
                    query = text(
                        f"SELECT id, name, phase_id, auto, kind from milestones {conditions}"
                    )
                    milestone_obj = conn.execute(query, milestone).fetchone()
                    if milestone_obj is None: 
                        milestone_obj = conn.execute(
                            milestones_table.insert(milestone).returning(
                                (milestones_table.c.id).label("id")
                            )
                        )
                    else:
                        conn.execute(
                            milestones_table.update()
                            .where(milestones_table.c.id == milestone_obj.id)
                            .values(**milestone)
                        )
                    milestone_id = milestone_obj.id if hasattr(milestone_obj,"id") else milestone_obj.first()["id"]
                    if milestone_ref:
                        outcomes = _filter_dataset(
                            outcomes_data, "milestone_id", milestone_ref
                        )
                        outcome_sort_order = 0
                        for outcome in outcomes:
                            outcome_sort_order += 1
                            outcome["sort_order"] = outcome_sort_order
                            outcome["milestone_id"] = milestone_id
                            conditions = f"WHERE milestone_id ={milestone_id} AND name='{milestone['name']}'"
                            query = text(
                                f"SELECT id, name from outcomes {conditions}"
                            )
                            outcome_obj = conn.execute(query, outcome).fetchone()
                            if outcome_obj is None:
                                conn.execute(
                                    outcomes_table.insert(outcome)
                                )
                            else:
                                conn.execute(
                                    outcomes_table.update()
                                    .where(outcomes_table.c.id == outcome_obj.id)
                                    .values(**outcome)
                                )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###