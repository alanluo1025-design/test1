"""add_discord_messenger_to_notification_prefs

Revision ID: 13f8ad2a2ad3
Revises: 47c304ccb844
Create Date: 2026-05-20 22:10:05.324858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '13f8ad2a2ad3'
down_revision: Union[str, None] = '47c304ccb844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # notifications.channel: VARCHAR(10) → VARCHAR(15)
    # SQLite 不支援 ALTER COLUMN，使用 batch 模式重建資料表
    with op.batch_alter_table('notifications') as batch_op:
        batch_op.alter_column('channel',
                              existing_type=sa.VARCHAR(length=10),
                              type_=sa.String(length=15),
                              existing_nullable=False)

    # user_notification_prefs: 新增 Discord / Messenger 欄位
    op.add_column('user_notification_prefs',
                  sa.Column('notify_discord',   sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user_notification_prefs',
                  sa.Column('notify_messenger', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user_notification_prefs',
                  sa.Column('discord_user_id',  sa.String(length=100), nullable=True))
    op.add_column('user_notification_prefs',
                  sa.Column('messenger_psid',   sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('user_notification_prefs', 'messenger_psid')
    op.drop_column('user_notification_prefs', 'discord_user_id')
    op.drop_column('user_notification_prefs', 'notify_messenger')
    op.drop_column('user_notification_prefs', 'notify_discord')

    with op.batch_alter_table('notifications') as batch_op:
        batch_op.alter_column('channel',
                              existing_type=sa.String(length=15),
                              type_=sa.VARCHAR(length=10),
                              existing_nullable=False)
