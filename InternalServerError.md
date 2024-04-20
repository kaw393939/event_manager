# 500 Internal Error during Login and Registration

## Root Cause: Absence of Database Attributes

## Solution:

There are two missing characteristics in the alembic version file: "is_professional" and "professional_status_updated_at". Adding these characteristics to the database resolved the problem.

>>> sa.Column('is_professional', sa.Boolean(), nullable=True, default=False),
    sa.Column('professional_status_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
