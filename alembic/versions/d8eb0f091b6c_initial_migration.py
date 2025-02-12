"""Initial migration

Revision ID: d8eb0f091b6c
Revises: 
Create Date: 2025-02-07 08:45:02.301346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8eb0f091b6c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('admin_first_name', sa.String(), nullable=True),
    sa.Column('admin_last_name', sa.String(), nullable=True),
    sa.Column('number', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('reg_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('question', sa.String(), nullable=True),
    sa.Column('var_1', sa.String(), nullable=True),
    sa.Column('var_2', sa.String(), nullable=True),
    sa.Column('var_3', sa.String(), nullable=True),
    sa.Column('var_4', sa.String(), nullable=True),
    sa.Column('correct_answer', sa.String(), nullable=True),
    sa.Column('timer', sa.Integer(), nullable=True),
    sa.Column('level', sa.Enum('LEVEL_1', 'LEVEL_2', 'LEVEL_3', name='testlevel'), nullable=True),
    sa.Column('test_type', sa.Enum('TYPE_1', 'TYPE_2', 'TYPE_3', name='testtype'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_first_name', sa.String(), nullable=True),
    sa.Column('user_last_name', sa.String(), nullable=True),
    sa.Column('number', sa.String(), nullable=True),
    sa.Column('par_first_name', sa.String(), nullable=True),
    sa.Column('par_last_name', sa.String(), nullable=True),
    sa.Column('par_number', sa.String(), nullable=True),
    sa.Column('birthday', sa.String(), nullable=True),
    sa.Column('school_class', sa.Integer(), nullable=True),
    sa.Column('university', sa.String(), nullable=True),
    sa.Column('group_number', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('is_blocked', sa.Boolean(), nullable=True),
    sa.Column('reg_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number')
    )
    op.create_table('test_rating',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('correct_all', sa.Integer(), nullable=True),
    sa.Column('category_objects_type1', sa.Integer(), nullable=True),
    sa.Column('category_objects_type2', sa.Integer(), nullable=True),
    sa.Column('category_actions_type1', sa.Integer(), nullable=True),
    sa.Column('category_actions_type2', sa.Integer(), nullable=True),
    sa.Column('category_actions_type3', sa.Integer(), nullable=True),
    sa.Column('category_skills_type1', sa.Integer(), nullable=True),
    sa.Column('category_skills_type2', sa.Integer(), nullable=True),
    sa.Column('category_skills_type3', sa.Integer(), nullable=True),
    sa.Column('time', sa.String(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_answers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_response', sa.String(), nullable=True),
    sa.Column('correctness', sa.Boolean(), nullable=True),
    sa.Column('answered_at', sa.DateTime(), nullable=True),
    sa.Column('attempt', sa.Integer(), nullable=True),
    sa.Column('timer', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.Column('rating_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rating_id'], ['test_rating.id'], ),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_answers')
    op.drop_table('test_rating')
    op.drop_table('users')
    op.drop_table('tests')
    op.drop_table('admins')
    # ### end Alembic commands ###
