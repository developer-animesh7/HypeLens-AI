import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schema_postgres.sql')

def main():
    # Load .env so DATABASE_URL is available when running as a script
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL not set')
    engine = create_engine(url, future=True)
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()
    # Execute statements individually to avoid driver multi-statement limitations
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    print('PostgreSQL schema created/updated successfully')

if __name__ == '__main__':
    main()
