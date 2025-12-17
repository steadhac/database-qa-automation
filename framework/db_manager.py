import os
import psycopg2
import pymysql
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self, db_type='postgres'):
        self.db_type = db_type
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        if self.db_type == 'postgres':
            self.connection = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT'),
                database=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
        elif self.db_type == 'mysql':
            self.connection = pymysql.connect(
                host=os.getenv('MYSQL_HOST'),
                port=int(os.getenv('MYSQL_PORT')),
                database=os.getenv('MYSQL_DB'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD')
            )
        return self.connection
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            try:
                results = cursor.fetchall()
            except:
                results = None
            self.connection.commit()
            cursor.close()
            return results
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise e
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()