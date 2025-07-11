#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MySQL
Run this script after setting up MySQL to migrate existing data
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.story import Base, Story

load_dotenv()


def migrate_data():
    """Migrate data from SQLite to MySQL"""

    # SQLite configuration
    sqlite_url = "sqlite:///./stories.db"
    sqlite_engine = create_engine(sqlite_url)
    SqliteSession = sessionmaker(bind=sqlite_engine)

    # MySQL configuration
    mysql_url = os.getenv("DATABASE_URL")
    if not mysql_url or "mysql" not in mysql_url:
        print("ERROR: MySQL DATABASE_URL not configured properly")
        print("Please set DATABASE_URL environment variable")
        return False

    mysql_engine = create_engine(mysql_url)
    MysqlSession = sessionmaker(bind=mysql_engine)

    print(f"Migration started at {datetime.now()}")
    print(f"From: SQLite ({sqlite_url})")
    print(f"To: MySQL ({mysql_url.split('@')[1] if '@' in mysql_url else mysql_url})")

    try:
        # Create tables in MySQL
        print("\n1. Creating tables in MySQL...")
        Base.metadata.create_all(bind=mysql_engine)
        print("✓ Tables created successfully")

        # Read data from SQLite
        print("\n2. Reading data from SQLite...")
        sqlite_session = SqliteSession()
        stories = sqlite_session.query(Story).all()
        print(f"✓ Found {len(stories)} stories in SQLite")

        if len(stories) == 0:
            print("No data to migrate.")
            return True

        # Write data to MySQL
        print("\n3. Writing data to MySQL...")
        mysql_session = MysqlSession()

        # Clear existing data in MySQL (optional)
        mysql_session.query(Story).delete()
        mysql_session.commit()

        # Insert stories
        success_count = 0
        for story in stories:
            try:
                # Create new story object (to avoid SQLAlchemy session conflicts)
                new_story = Story(
                    title=story.title,
                    content=story.content,
                    author=story.author,
                    genre=story.genre,
                    is_published=story.is_published,
                    created_at=story.created_at,
                    updated_at=story.updated_at,
                )
                mysql_session.add(new_story)
                success_count += 1
            except Exception as e:
                print(f"Error migrating story '{story.title}': {e}")

        mysql_session.commit()
        print(f"✓ Successfully migrated {success_count}/{len(stories)} stories")

        # Verify migration
        print("\n4. Verifying migration...")
        mysql_count = mysql_session.query(Story).count()
        print(f"✓ MySQL now contains {mysql_count} stories")

        # Close sessions
        sqlite_session.close()
        mysql_session.close()

        print(f"\nMigration completed successfully at {datetime.now()}")
        return True

    except Exception as e:
        print(f"\nERROR during migration: {e}")
        return False


def backup_sqlite():
    """Create a backup of the SQLite database"""
    import shutil
    from datetime import datetime

    source = "stories.db"
    if not os.path.exists(source):
        print("No SQLite database found to backup")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"stories_backup_{timestamp}.db"

    try:
        shutil.copy2(source, backup_name)
        print(f"✓ SQLite backup created: {backup_name}")
        return True
    except Exception as e:
        print(f"ERROR creating backup: {e}")
        return False


if __name__ == "__main__":
    print("=== Story Teller Database Migration ===")
    print("This script will migrate data from SQLite to MySQL")

    # Check if SQLite database exists
    if not os.path.exists("stories.db"):
        print("No SQLite database found. Nothing to migrate.")
        sys.exit(0)

    # Create backup
    print("\nCreating backup of SQLite database...")
    if not backup_sqlite():
        print("Failed to create backup. Aborting migration.")
        sys.exit(1)

    # Confirm migration
    response = input("\nProceed with migration? (y/N): ")
    if response.lower() != "y":
        print("Migration cancelled.")
        sys.exit(0)

    # Run migration
    if migrate_data():
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your application with MySQL")
        print("2. Update your docker-compose.yml if needed")
        print("3. Remove SQLite database if everything works correctly")
    else:
        print("\n✗ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
