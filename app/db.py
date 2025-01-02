import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def connect_to_db():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: A database connection object, or None on failure.
    """
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        return None

def execute_query(conn, query, params=None):
    """
    Executes a SQL query against the database.

    Args:
        conn (psycopg2.extensions.connection): The database connection object.
        query (str): The SQL query to execute.
        params (tuple or dict, optional): Parameters for the query (to prevent SQL injection). Defaults to None.

    Returns:
        list: A list of tuples representing the query results, or None on error.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit() # Commit changes for INSERT, UPDATE, DELETE
            if cur.description: # Check if the query returns data (e.g., SELECT)
                return cur.fetchall()
            else:
                return None
    except psycopg2.Error as e:
        conn.rollback() # Rollback changes in case of error
        return None

def fetch_user_leave_balance(conn, user_id):
    """
    Retrieves the leave balance for a specific user.

    Args:
        conn: The database connection.
        user_id: The user's Azure AD ID.

    Returns:
        list: A list of tuples representing the leave balances for the user, or None if there is an error.
    """
    query = """
        SELECT lt.leave_type_name, lb.available_days, lb.used_days
        FROM leave_balances lb
        JOIN employees e ON lb.employee_id = e.employee_id
        JOIN leave_types lt ON lb.leave_type_id = lt.leave_type_id
        WHERE e.user_id = %s;
    """
    return execute_query(conn, query, (user_id,))

def create_leave_request(conn, employee_id, leave_type_id, start_date, end_date, days_requested, reason):
    """
    Inserts a new leave request into the leave_requests table.

    Args:
        conn: The database connection.
        employee_id: The employee's ID.
        leave_type_id: The ID of the leave type.
        start_date: The start date of the leave.
        end_date: The end date of the leave.
        days_requested: The number of days requested.
        reason: The reason for the leave request.

    Returns:
        bool: True if the request was successfully created, False otherwise.
    """
    query = """
        INSERT INTO leave_requests (employee_id, leave_type_id, start_date, end_date, days_requested, reason, status, request_date)
        VALUES (%s, %s, %s, %s, %s, %s, 'Pending', NOW());
    """
    result = execute_query(conn, query, (employee_id, leave_type_id, start_date, end_date, days_requested, reason))
    return result is None

def fetch_leave_requests(conn, employee_id):
    """
    Retrieves leave requests for a specific employee.

    Args:
        conn: The database connection.
        employee_id: The employee's ID.

    Returns:
        list: A list of tuples representing the leave requests, or None if there is an error.
    """
    query = """
        SELECT lr.leave_request_id, lt.leave_type_name, lr.start_date, lr.end_date, lr.days_requested, lr.reason, lr.status, lr.request_date
        FROM leave_requests lr
        JOIN leave_types lt ON lr.leave_type_id = lt.leave_type_id
        WHERE lr.employee_id = %s
        ORDER BY lr.request_date DESC;
    """
    return execute_query(conn, query, (employee_id,))