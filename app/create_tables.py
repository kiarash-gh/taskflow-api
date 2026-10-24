from app.db import Base, engine
from app import models  # Registers the Task model with Base.metadata

Base.metadata.create_all(bind=engine)

print("Database tables created.")