"""
Database initialization script
Run this to create all database tables
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freelance_app.models.base import Base, engine, init_db, drop_db
from freelance_app.models import (
    User, UserSkill, UserPreference,
    FreelancePlatform,
    Client, ClientReview, ClientRedFlag,
    Job, JobApplication,
    CompanyResearch,
    ScamReport,
    SavedSearch,
    UserAnalytics, PlatformAnalytics
)


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")

        # List created tables
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


def drop_tables():
    """Drop all database tables"""
    print("Dropping all database tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped successfully!")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        raise


def seed_data():
    """Seed initial data"""
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("\nSeeding initial data...")

        # Check if platforms already exist
        existing_platforms = session.query(FreelancePlatform).count()
        if existing_platforms > 0:
            print(f"  Platforms already exist ({existing_platforms} platforms). Skipping...")
            return

        # Seed freelance platforms
        platforms = [
            FreelancePlatform(
                name="Upwork",
                base_url="https://www.upwork.com",
                has_api=True,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Freelancer",
                base_url="https://www.freelancer.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Fiverr",
                base_url="https://www.fiverr.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Guru",
                base_url="https://www.guru.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="PeoplePerHour",
                base_url="https://www.peopleperhour.com",
                has_api=False,
                scraper_enabled=True
            ),
        ]

        session.add_all(platforms)
        session.commit()

        print(f"✓ Seeded {len(platforms)} freelance platforms")

    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument(
        "command",
        choices=["create", "drop", "recreate", "seed"],
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "create":
        create_tables()

    elif args.command == "drop":
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Aborted.")

    elif args.command == "recreate":
        confirm = input("Are you sure you want to recreate all tables? All data will be lost! (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
            create_tables()
            seed_data()
        else:
            print("Aborted.")

    elif args.command == "seed":
        seed_data()
