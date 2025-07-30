"""Initial user tables for Upstash PostgreSQL

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create UUID extension if not exists (Upstash PostgreSQL supports this)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        
        # Additional user fields
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        
        # Timestamps with timezone support
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Subscription/Usage tracking
        sa.Column('is_premium', sa.Boolean(), nullable=False, default=False),
        sa.Column('total_messages', sa.String(length=20), nullable=False, default='0'),
    )
    
    # Create indexes for better performance on Upstash
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_is_premium', 'users', ['is_premium'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Add unique constraint on email
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    
    # Create trigger to automatically update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger and function
    op.execute('DROP TRIGGER IF EXISTS update_users_updated_at ON users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # Drop indexes
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_is_premium', table_name='users')
    op.drop_index('idx_users_is_active', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
    # Drop table
    op.drop_table('users')