import os
import pytest
from geonature.utils.env import load_config, get_config_file_path
import warnings

# UserWarning: The psycopg2 wheel package will be renamed from release 2.8 ...
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")
import psycopg2  # noqa: E402


def pytest_sessionstart(session):
    """before session.main() is called."""
    # execute_script('delete_sample_data.sql')
    # execute_script('sample_data.sql')
    pass


def execute_script(file_name):
    """
    Execute a script to set or delete sample data before test
    """
    config_path = get_config_file_path()
    config = load_config(config_path)
    conn = psycopg2.connect(config["SQLALCHEMY_DATABASE_URI"])
    cur = conn.cursor()
    sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    cur.execute(open(sql_file, "r").read())
    conn.commit()
    cur.close()
    conn.close()


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)
