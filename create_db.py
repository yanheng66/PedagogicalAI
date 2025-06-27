from database import engine, Base

# Create all tables. Only run once.
if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Done.") 