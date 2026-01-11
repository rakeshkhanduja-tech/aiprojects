import os
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['database']
        
        self.conn_str = f"host={self.config['host']} port={self.config['port']} dbname={self.config['dbname']} user={self.config['user']} password={self.config['password']} sslmode={self.config['sslmode']}"

    def get_connection(self):
        return psycopg2.connect(self.conn_str, cursor_factory=RealDictCursor)

    def setup_database(self, schema_path):
        print(f"Setting up database {self.config['dbname']}...")
        conn = self.get_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            with open(schema_path, 'r') as f:
                cur.execute(f.read())
        conn.close()
        print("Schema created successfully.")

    def seed_data(self, seed_script_path):
        print("Seeding database...")
        # Since seeding is complex, we might import the seed module or run it
        import importlib.util
        spec = importlib.util.spec_from_file_location("seed_module", seed_script_path)
        seed_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seed_module)
        seed_module.run_seed(self)
        print("Seeding completed.")

    def query(self, sql, params=None):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    return cur.fetchall()
                return None
    
    def execute(self, sql, params=None):
        with self.get_connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.rowcount
