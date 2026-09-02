"""Initial schema: users, subscriptions, alerts

Revision ID: e39c445e9c34
Revises: 
Create Date: 2026-08-29 22:49:27.543187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e39c445e9c34'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Creates users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        if_not_exists=True
    )
    # Creates subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('billing_cycle', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=100), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    # Creates alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('sub_id', sa.UUID(), nullable=False),
        sa.Column('renewal_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('is_delivered', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['sub_id'], ['subscriptions.id']),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_table('alerts', if_exists=True)
    op.drop_table('subscriptions', if_exists=True)
    op.drop_table('users', if_exists=True)
