#!/usr/bin/env python3
"""
Database setup script for PEDAGOGY system
Handles database creation, migration, and seeding
"""

import os
import sys
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    PSYCOPG2_AVAILABLE = True
except ImportError:
    print("Warning: psycopg2 not available. Cannot setup PostgreSQL database.")
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    ISOLATION_LEVEL_AUTOCOMMIT = None

try:
    from dotenv import load_dotenv
except ImportError:
    # Create a dummy load_dotenv if not available
    def load_dotenv():
        pass
import argparse
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_setup.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Handle database setup operations"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'dummydata')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '223344')
        
        # Connection string for connecting to PostgreSQL server (without specific database)
        self.server_conn_string = f"host={self.host} port={self.port} user={self.username} password={self.password}"
        
        # Connection string for connecting to the specific database
        self.db_conn_string = f"{self.server_conn_string} dbname={self.database}"
    
    def create_database(self) -> bool:
        """Create the pedagogy database if it doesn't exist"""
        try:
            # Connect to PostgreSQL server
            conn = psycopg2.connect(self.server_conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            exists = cursor.fetchone()
            
            if exists:
                logger.info(f"Database '{self.database}' already exists")
                return True
            
            # Create database
            cursor.execute(f"CREATE DATABASE {self.database}")
            logger.info(f"Database '{self.database}' created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def run_migration(self, migration_file: str) -> bool:
        """Run a specific migration file"""
        try:
            if not os.path.exists(migration_file):
                logger.error(f"Migration file not found: {migration_file}")
                return False
            
            # Connect to the database
            conn = psycopg2.connect(self.db_conn_string)
            cursor = conn.cursor()
            
            # Read and execute migration file
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            cursor.execute(migration_sql)
            conn.commit()
            
            logger.info(f"Migration executed successfully: {migration_file}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error running migration {migration_file}: {e}")
            return False
    
    def run_all_migrations(self) -> bool:
        """Run all migration files in order"""
        migrations_dir = "migrations"
        
        if not os.path.exists(migrations_dir):
            logger.error(f"Migrations directory not found: {migrations_dir}")
            return False
        
        # Get all SQL files in migrations directory and sort them
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
        migration_files.sort()
        
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        logger.info(f"Found {len(migration_files)} migration files")
        
        success = True
        for migration_file in migration_files:
            file_path = os.path.join(migrations_dir, migration_file)
            logger.info(f"Running migration: {migration_file}")
            
            if not self.run_migration(file_path):
                logger.error(f"Migration failed: {migration_file}")
                success = False
                break
        
        if success:
            logger.info("All migrations completed successfully")
        
        return success
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            cursor = conn.cursor()
            
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            logger.info(f"Database connection successful. PostgreSQL version: {version[0]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def reset_database(self) -> bool:
        """Drop and recreate the database (WARNING: This will delete all data!)"""
        try:
            # Connect to PostgreSQL server
            conn = psycopg2.connect(self.server_conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Terminate existing connections to the database
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (self.database,))
            
            # Drop database if exists
            cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
            logger.info(f"Database '{self.database}' dropped")
            
            # Create database
            cursor.execute(f"CREATE DATABASE {self.database}")
            logger.info(f"Database '{self.database}' recreated")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False
    
    def check_tables(self) -> bool:
        """Check if required tables exist"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            cursor = conn.cursor()
            
            # Check for key tables
            required_tables = ['students', 'templates', 'activities', 'lesson_plans']
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found {len(existing_tables)} tables: {existing_tables}")
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.warning(f"Missing required tables: {missing_tables}")
                return False
            else:
                logger.info("All required tables exist")
                return True
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error checking tables: {e}")
            return False

def main():
    """Main function to handle command line arguments"""
    if not PSYCOPG2_AVAILABLE:
        print("Error: psycopg2 is not available. Cannot setup PostgreSQL database.")
        print("To install: pip install psycopg2-binary")
        print("Alternatively, use mock database mode by setting USE_MOCK_DB=true")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Database setup for PEDAGOGY system')
    parser.add_argument('--create', action='store_true', help='Create database')
    parser.add_argument('--migrate', action='store_true', help='Run migrations')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: Deletes all data!)')
    parser.add_argument('--test', action='store_true', help='Test database connection')
    parser.add_argument('--check', action='store_true', help='Check database tables')
    parser.add_argument('--full-setup', action='store_true', help='Full setup: create database and run migrations')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    setup = DatabaseSetup()
    
    logger.info("Starting database setup...")
    logger.info(f"Target database: {setup.database} on {setup.host}:{setup.port}")
    
    if args.reset:
        logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
        confirm = input("Are you sure you want to reset the database? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            if not setup.reset_database():
                logger.error("Database reset failed")
                sys.exit(1)
        else:
            logger.info("Database reset cancelled")
            return
    
    if args.create or args.full_setup:
        if not setup.create_database():
            logger.error("Database creation failed")
            sys.exit(1)
    
    if args.migrate or args.full_setup:
        if not setup.run_all_migrations():
            logger.error("Migrations failed")
            sys.exit(1)
    
    if args.test:
        if not setup.test_connection():
            logger.error("Connection test failed")
            sys.exit(1)
    
    if args.check:
        if not setup.check_tables():
            logger.error("Table check failed")
            sys.exit(1)
    
    logger.info("Database setup completed successfully!")

if __name__ == "__main__":
    main()
