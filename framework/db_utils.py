"""
DBUtils: Safe database operations wrapper for DatabaseManager.

Provides:
- Safe fetching of single row or value
- Fetching all rows safely
- Safe insert/update/delete execution

Integrates with DatabaseManager to prevent NoneType or index errors in tests.
"""

import logging
from typing import Any, Optional, Tuple, List

# Configure logging for this module
logger = logging.getLogger(__name__)

class DBUtils:
    """
    Wraps a DatabaseManager instance for safe SQL operations.
    """

    def __init__(self, db_manager: Any):
        """
        Initialize with a DatabaseManager instance.

        Args:
            db_manager (DatabaseManager): Existing DB connection manager
        """
        self.db = db_manager

    def fetch_one_or_raise(
        self, 
        query: str, 
        params: Optional[Tuple] = None, 
        error_msg: Optional[str] = None
    ) -> Tuple:
        """
        Fetch a single row from the database.

        Args:
            query (str): SQL query
            params (tuple, optional): Query parameters
            error_msg (str, optional): Custom error if no row returned

        Returns:
            tuple: First row from the query result

        Raises:
            ValueError: If no rows returned
        """
        result = self.db.execute_query(query, params)
        if not result:
            logger.error(error_msg or f"No rows returned for query: {query}")
            raise ValueError(error_msg or f"No rows returned for query: {query}")
        logger.debug(f"Fetched one row: {result[0]}")
        return result[0]

    def fetch_value_or_raise(
        self, 
        query: str, 
        params: Optional[Tuple] = None, 
        column: int = 0, 
        error_msg: Optional[str] = None
    ) -> Any:
        """
        Fetch a single value from the database.

        Args:
            query (str): SQL query
            params (tuple, optional)
            column (int): Column index (default 0)
            error_msg (str, optional)

        Returns:
            Any: Value from the specified column

        Raises:
            ValueError: If query returns no rows
        """
        row = self.fetch_one_or_raise(query, params, error_msg)
        logger.debug(f"Fetched value from column {column}: {row[column]}")
        return row[column]

    def fetch_all_safe(
        self, 
        query: str, 
        params: Optional[Tuple] = None
    ) -> List[Tuple]:
        """
        Fetch all rows from a query safely.

        Args:
            query (str): SQL query
            params (tuple, optional)

        Returns:
            list[tuple]: All rows, or empty list if none
        """
        result = self.db.execute_query(query, params)
        logger.debug(f"Fetched all rows: {result or []}")
        return result or []

    def safe_execute(
        self, 
        query: str, 
        params: Optional[Tuple] = None
    ) -> bool:
        """
        Execute an INSERT/UPDATE/DELETE query safely.

        Args:
            query (str): SQL query
            params (tuple, optional)

        Returns:
            bool: True if query succeeded, False if exception occurred
        """
        try:
            self.db.execute_query(query, params)
            logger.info(f"Successfully executed query: {query}")
            return True
        except Exception as e:
            logger.error(f"[DBUtils] Error executing query: {e}")
            return False