import os
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['database']
        
        self.conn_str = f"host={self.config['host']} port={self.config['port']} dbname={self.config['dbname']} user={self.config['user']} password={self.config['password']} sslmode={self.config['sslmode']}"

    def get_connection(self, dbname=None):
        conn_params = self.config.copy()
        if dbname:
            conn_params['dbname'] = dbname
        
        conn_str = f"host={conn_params['host']} port={conn_params['port']} dbname={conn_params['dbname']} user={conn_params['user']} password={conn_params['password']} sslmode={conn_params['sslmode']}"
        return psycopg2.connect(conn_str, cursor_factory=RealDictCursor)

    def setup_database(self, schema_path):
        target_db = self.config['dbname']
        
        # 1. Connect to 'postgres' to check/create the target database
        try:
            print(f"Ensuring database '{target_db}' exists...")
            conn = self.get_connection(dbname='postgres')
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
                if not cur.fetchone():
                    print(f"Database '{target_db}' not found. Creating...")
                    cur.execute(f'CREATE DATABASE "{target_db}"')
            conn.close()
        except Exception as e:
            print(f"Warning: Could not check/create database: {e}")

        # 2. Connect to the target database and run schema
        print(f"Setting up schema for '{target_db}'...")
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
