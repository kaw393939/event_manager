# 500 An internal Server Error occurred during registration and login.
## Cause: DB characteristics missing
## Remedy:
In the alembic version file, the attributes "is_professional" and "professional_status_updated_at" are absent. By adding these properties to the database, the problem was resolved.

>>>sa.Column('is_professional', sa.Boolean(), nullable=True, default=False),
>>>sa.Column('professional_status_updated_at',sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
