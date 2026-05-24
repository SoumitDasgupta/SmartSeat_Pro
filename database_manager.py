import psycopg2
from psycopg2 import extras

def get_connection():
    # Update these credentials for your deployment environment
    return psycopg2.connect(
        dbname="SmartSeat_DB", user="postgres",
        password="root", host="localhost", port="5432"
    )

def upload_students(df):
    conn = get_connection(); cur = conn.cursor()
    # UPSERT Logic: Insert, but if regd_id exists, update the data
    query = """
        INSERT INTO students (regd_id, name, stream, year, semester, section, roll_no)
        VALUES %s
        ON CONFLICT (regd_id) DO UPDATE SET
            name = EXCLUDED.name,
            stream = EXCLUDED.stream,
            year = EXCLUDED.year,
            semester = EXCLUDED.semester,
            section = EXCLUDED.section,
            roll_no = EXCLUDED.roll_no;
    """
    extras.execute_values(cur, query, df.values.tolist())
    conn.commit(); cur.close(); conn.close()

def upload_halls(df):
    conn = get_connection(); cur = conn.cursor()
    # UPSERT Logic: Insert, but if hall_name exists, update the capacity/rows
    query = """
        INSERT INTO infrastructure (hall_name, total_rows, total_cols, bench_capacity)
        VALUES %s
        ON CONFLICT (hall_name) DO UPDATE SET
            total_rows = EXCLUDED.total_rows,
            total_cols = EXCLUDED.total_cols,
            bench_capacity = EXCLUDED.bench_capacity;
    """
    extras.execute_values(cur, query, df.values.tolist())
    conn.commit(); cur.close(); conn.close()

def upload_schedule(df):
    conn = get_connection(); cur = conn.cursor()
    df['exam_date'] = df['exam_date'].astype(str)
    # UPSERT Logic: Uses a composite of date, stream, and semester to check for existing entries
    query = """
        INSERT INTO exam_schedule (exam_identifier, exam_date, semester, stream, subject_code, subject_name)
        VALUES %s
        ON CONFLICT (exam_date, semester, stream, subject_code) DO UPDATE SET
            exam_identifier = EXCLUDED.exam_identifier,
            subject_name = EXCLUDED.subject_name;
    """
    extras.execute_values(cur, query, df.values.tolist())
    conn.commit(); cur.close(); conn.close()

def save_final_allocation(alloc_list):
    if not alloc_list: return
    conn = get_connection(); cur = conn.cursor()
    # Clean up previous allocation for the same exam/date before publishing to avoid duplicates
    cur.execute("DELETE FROM final_allocations WHERE exam_identifier = %s AND exam_date = %s", 
                (alloc_list[0]['exam_identifier'], alloc_list[0]['exam_date']))
    query = """INSERT INTO final_allocations (exam_identifier, exam_date, regd_id, student_name, hall_name, seat_label, display_id, subject) 
               VALUES %s"""
    vals = [(a['exam_identifier'], a['exam_date'], a['regd_id'], a['student_name'], 
             a['hall_name'], a['seat_label'], a['display_id'], a['subject']) for a in alloc_list]
    extras.execute_values(cur, query, vals)
    conn.commit(); cur.close(); conn.close()