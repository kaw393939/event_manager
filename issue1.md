# 500 Internal error for register and login

## Cause: Missing DB attributes
## Fix:
The attributes "is_professional" and "professional_status_updated_at" missing in the alembic version file. The issue fixed by adding these attributes to the DB
    sa.Column('is_professional', sa.Boolean(), nullable=True, default=False),
    sa.Column('professional_status_updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
