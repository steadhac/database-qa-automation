import pytest
import logging
from framework.db_utils import DBUtils

class DummyDBManager:
    def __init__(self, data=None, should_fail=False):
        self.data = data or []
        self.should_fail = should_fail

    def execute_query(self, query, params=None):
        if self.should_fail:
            logging.error(
                "Database operation failed",
                extra={"query": query, "params": params}
            )
            raise Exception(f"DB error occurred while executing query: {query!r} with params: {params!r}")
        if query.lower().startswith("select"):
            return self.data
        return None

def test_fetch_one_or_raise_returns_first_row_when_data_exists(caplog):
    logging.info("Starting test_fetch_one_or_raise_returns_first_row_when_data_exists")
    db = DummyDBManager(data=[("row1", "val1")])
    utils = DBUtils(db)
    try:
        with caplog.at_level(logging.DEBUG):
            row = utils.fetch_one_or_raise("SELECT * FROM test")
        assert row == ("row1", "val1")
        assert "Fetched one row" in caplog.text
    except AssertionError as e:
        logging.error("Expected row ('row1', 'val1') not returned or log missing. Data required: [('row1', 'val1')]. Error: %s", e)
        raise
    logging.info("Completed test_fetch_one_or_raise_returns_first_row_when_data_exists")

def test_fetch_one_or_raise_raises_value_error_when_no_data(caplog):
    logging.info("Starting test_fetch_one_or_raise_raises_value_error_when_no_data")
    db = DummyDBManager(data=[])
    utils = DBUtils(db)
    try:
        with pytest.raises(ValueError) as excinfo, caplog.at_level(logging.ERROR):
            utils.fetch_one_or_raise("SELECT * FROM test", error_msg="No data found")
        assert "No data found" in str(excinfo.value)
        assert "No data found" in caplog.text
    except AssertionError as e:
        logging.error("Expected ValueError not raised or log missing. Data required: []. Error: %s", e)
        raise
    logging.info("Completed test_fetch_one_or_raise_raises_value_error_when_no_data")

def test_fetch_value_or_raise_returns_column_value_when_data_exists(caplog):
    logging.info("Starting test_fetch_value_or_raise_returns_column_value_when_data_exists")
    db = DummyDBManager(data=[("row1", "val1")])
    utils = DBUtils(db)
    try:
        with caplog.at_level(logging.DEBUG):
            value = utils.fetch_value_or_raise("SELECT * FROM test", column=1)
        assert value == "val1"
        assert "Fetched value from column 1" in caplog.text
    except AssertionError as e:
        logging.error("Expected value 'val1' not returned or log missing. Data required: [('row1', 'val1')], column=1. Error: %s", e)
        raise
    logging.info("Completed test_fetch_value_or_raise_returns_column_value_when_data_exists")

def test_fetch_value_or_raise_raises_value_error_when_no_data(caplog):
    logging.info("Starting test_fetch_value_or_raise_raises_value_error_when_no_data")
    db = DummyDBManager(data=[])
    utils = DBUtils(db)
    try:
        with pytest.raises(ValueError):
            utils.fetch_value_or_raise("SELECT * FROM test", column=0)
    except AssertionError as e:
        logging.error("Expected ValueError not raised. Data required: [], column=0. Error: %s", e)
        raise
    logging.info("Completed test_fetch_value_or_raise_raises_value_error_when_no_data")

def test_fetch_all_safe_returns_all_rows_when_data_exists(caplog):
    logging.info("Starting test_fetch_all_safe_returns_all_rows_when_data_exists")
    db = DummyDBManager(data=[("row1",), ("row2",)])
    utils = DBUtils(db)
    try:
        result = utils.fetch_all_safe("SELECT * FROM test")
        assert result == [("row1",), ("row2",)]
    except AssertionError as e:
        logging.error("Expected result [('row1',), ('row2',)] not returned. Data required: [('row1',), ('row2',)]. Error: %s", e)
        raise
    logging.info("Completed test_fetch_all_safe_returns_all_rows_when_data_exists")

def test_fetch_all_safe_returns_empty_list_when_no_data(caplog):
    logging.info("Starting test_fetch_all_safe_returns_empty_list_when_no_data")
    db = DummyDBManager(data=[])
    utils = DBUtils(db)
    try:
        result = utils.fetch_all_safe("SELECT * FROM test")
        assert result == []
    except AssertionError as e:
        logging.error("Expected empty list not returned. Data required: []. Error: %s", e)
        raise
    logging.info("Completed test_fetch_all_safe_returns_empty_list_when_no_data")

def test_safe_execute_returns_true_when_query_succeeds(caplog):
    logging.info("Starting test_safe_execute_returns_true_when_query_succeeds")
    db = DummyDBManager()
    utils = DBUtils(db)
    try:
        with caplog.at_level(logging.INFO):
            success = utils.safe_execute("UPDATE test SET val=1")
        assert success is True
        assert "Successfully executed query" in caplog.text
    except AssertionError as e:
        logging.error("Expected True not returned or log missing. Query: 'UPDATE test SET val=1'. Error: %s", e)
        raise
    logging.info("Completed test_safe_execute_returns_true_when_query_succeeds")

def test_safe_execute_returns_false_when_query_raises_exception(caplog):
    logging.info("Starting test_safe_execute_returns_false_when_query_raises_exception")
    db = DummyDBManager(should_fail=True)
    utils = DBUtils(db)
    try:
        with caplog.at_level(logging.ERROR):
            success = utils.safe_execute("UPDATE test SET val=1")
        assert success is False
        assert "Error executing query" in caplog.text
    except AssertionError as e:
        logging.error("Expected False not returned or error log missing. Query: 'UPDATE test SET val=1', should_fail=True. Error: %s", e)
        raise
    logging.info("Completed test_safe_execute_returns_false_when_query_raises_exception")