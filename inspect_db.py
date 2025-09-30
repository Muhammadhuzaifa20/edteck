import os
import json
from database import DatabaseService, DatabaseConfig


def main():
    config = DatabaseConfig()
    service = DatabaseService(config)
    overview = service.get_schema_overview(schema=os.getenv('DB_SCHEMA', 'public'))
    print(json.dumps(overview, indent=2, default=str))


if __name__ == "__main__":
    main()


