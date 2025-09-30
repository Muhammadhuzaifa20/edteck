# PEDAGOGY Database Integration

This document explains the PostgreSQL database integration added to the PEDAGOGY lesson planning system.

## Overview

The system now supports both PostgreSQL database storage and mock data for development/testing. The database integration provides:

- **Persistent storage** for students, templates, activities, and lesson plans
- **Scalable architecture** with connection pooling
- **Flexible deployment** with automatic fallback to mock data
- **Data integrity** with proper constraints and relationships

## Database Architecture

### Core Tables

1. **Students** - Student profiles and basic information
2. **Templates** - Lesson plan templates (5E, 7E, PBL, Dynamic)
3. **Activities** - Reusable learning activities for each template stage
4. **Lesson Plans** - Individual lesson plans created for students
5. **Learning History** - Track student progress over time

### Supporting Tables

- **Student relationships** (interests, strengths, challenges, SLOs)
- **Template definitions** (stages, best-for categories, confidence factors)
- **Activity details** (materials, adaptations)
- **LLM interactions** (audit trail for AI responses)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `python-dotenv==1.0.0` - Environment variable management

### 2. PostgreSQL Installation

#### Windows
```bash
# Download and install PostgreSQL from https://www.postgresql.org/download/windows/
# Or use chocolatey
choco install postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 3. Environment Configuration

Copy the example environment file:
```bash
cp env.example .env
```

Update `.env` with your database settings:
```env
# Use mock database (set to false for PostgreSQL)
USE_MOCK_DB=false

# PostgreSQL connection settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pedagogy
DB_USER=postgres
DB_PASSWORD=your_password

# Connection pool settings
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=20
```

### 4. Database Setup

#### Option A: Automated Setup (Recommended)
```bash
# Full setup: create database and run migrations
python setup_database.py --full-setup
```

#### Option B: Manual Setup
```bash
# 1. Create database
python setup_database.py --create

# 2. Run migrations
python setup_database.py --migrate

# 3. Test connection
python setup_database.py --test
```

#### Option C: SQL Command Line
```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE pedagogy;

-- Connect to the new database
\c pedagogy

-- Run the migration files
\i migrations/001_initial_schema.sql
\i migrations/002_seed_data.sql
```

### 5. Verify Setup

```bash
# Check that all tables exist
python setup_database.py --check

# Test the reasoner service
python reasoner.py
```

## Usage

### Development Mode (Mock Database)

Set `USE_MOCK_DB=true` in your `.env` file:
```bash
# Start the reasoner service with mock data
python reasoner.py
```

### Production Mode (PostgreSQL)

Set `USE_MOCK_DB=false` in your `.env` file:
```bash
# Start the reasoner service with PostgreSQL
python reasoner.py
```

### API Usage

The API endpoints remain the same, but now use database storage:

```bash
# Health check (shows database status)
curl http://localhost:5000/health

# Fetch student context
curl -X POST http://localhost:5000/context \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_123"}'

# Get template recommendation
curl -X POST http://localhost:5000/template/recommend \
  -H "Content-Type: application/json" \
  -d '{"grade": "8th", "subject": "Science", "slos": ["Understand scientific method"]}'
```

## Database Features

### Automatic Fallback

The system automatically falls back to mock data if PostgreSQL is not available:

```python
# The database service will use mock data if connection fails
db_service = create_database_service()  # Auto-detects availability
```

### Connection Pooling

Efficient connection management with configurable pool sizes:

```python
# Configure in environment variables
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=20
```

### Data Validation

Built-in constraints ensure data integrity:

- Grade format validation (e.g., "8th", "K", "Pre-K")
- Learning style validation
- Required field constraints
- Foreign key relationships

### Audit Trail

Track all LLM interactions for analysis and improvement:

```sql
SELECT * FROM llm_interactions 
WHERE interaction_type = 'template_recommendation'
ORDER BY created_at DESC;
```

## Database Schema

### Key Relationships

```
students (1) → (many) learning_history
students (1) → (many) lesson_plans
templates (1) → (many) activities
templates (1) → (many) lesson_plans
activities (many) ← (many) lesson_plan_activities
```

### Views

Pre-built views for common queries:

- `student_profiles` - Complete student information with all relationships
- `template_details` - Full template definitions with stages and metadata

## Migration Management

### Adding New Migrations

1. Create a new SQL file in `migrations/` with incremental numbering:
   ```
   migrations/003_add_new_feature.sql
   ```

2. Follow the migration template:
   ```sql
   -- =====================================================
   -- Migration Description
   -- Version: 003
   -- =====================================================
   
   -- Your changes here
   
   -- Update any necessary indexes
   -- Add comments for documentation
   ```

3. Run the migration:
   ```bash
   python setup_database.py --migrate
   ```

### Reset Database (Development Only)

**WARNING: This will delete all data!**

```bash
python setup_database.py --reset
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   ```
   psycopg2.OperationalError: could not connect to server
   ```
   - Check PostgreSQL is running
   - Verify connection settings in `.env`
   - Ensure database exists

2. **Permission Denied**
   ```
   psycopg2.OperationalError: FATAL: password authentication failed
   ```
   - Check username/password in `.env`
   - Verify PostgreSQL user permissions

3. **Database Does Not Exist**
   ```
   psycopg2.OperationalError: FATAL: database "pedagogy" does not exist
   ```
   - Run: `python setup_database.py --create`

4. **Tables Not Found**
   ```
   psycopg2.ProgrammingError: relation "students" does not exist
   ```
   - Run: `python setup_database.py --migrate`

### Enable Debug Logging

Set in your `.env` file:
```env
LOG_LEVEL=DEBUG
```

### Check Database Status

```bash
# Test connection
python setup_database.py --test

# Check tables
python setup_database.py --check

# View service health
curl http://localhost:5000/health
```

## Performance Considerations

### Indexes

The schema includes optimized indexes for common queries:

- Student lookups by ID, grade, subject
- Template and activity lookups
- Learning history by student and date
- Lesson plan queries

### Connection Pooling

Configure pool size based on your load:

```env
# For development
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=5

# For production
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=50
```

### Query Optimization

Use the built-in views for complex queries:

```sql
-- Instead of complex JOINs, use the view
SELECT * FROM student_profiles WHERE id = 'student_123';
```

## Future Enhancements

Planned database features:

1. **Data Migration Tools** - Import/export student data
2. **Backup Automation** - Scheduled database backups
3. **Analytics Tables** - Student performance analytics
4. **Caching Layer** - Redis integration for performance
5. **Multi-tenancy** - Support for multiple schools/organizations

## Support

For database-related issues:

1. Check the logs: `database_setup.log`
2. Verify environment configuration
3. Test connection: `python setup_database.py --test`
4. Review PostgreSQL logs for detailed error information

The system is designed to be resilient - it will continue working with mock data even if the database is unavailable, ensuring continuous operation during development and troubleshooting.
