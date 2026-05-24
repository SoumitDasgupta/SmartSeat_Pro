import pandas as pd
import numpy as np
import os

print("⏳ Loading libraries... (This may take a few seconds)")

# 1. GENERATE STUDENT DATABASE
def create_student_sample():
    print("📋 Generating Student Database...")
    streams = ['CSE', 'ECE', 'MECH']
    sections = ['A', 'B']
    semesters = [4, 6]
    data = []

    for stream in streams:
        for sem in semesters:
            for sec in sections:
                # Generate 20 students per group
                for roll in range(1, 21):
                    reg_id = f"2026{stream[:1]}{sem}{sec}{roll:02d}"
                    name = f"Student {reg_id}"
                    year = 2 if sem <= 4 else 3
                    data.append([reg_id, name, stream, year, sem, sec, roll])

    df_students = pd.DataFrame(data, columns=[
        'regd_id', 'name', 'stream', 'year', 'semester', 'section', 'roll_no'
    ])
    df_students.to_excel("sample_students.xlsx", index=False)
    print("✅ Created sample_students.xlsx")

# 2. GENERATE EXAM SCHEDULE
def create_schedule_sample():
    print("📅 Generating Exam Schedule...")
    # Matches the 'semester' and 'stream' of students above
    data = [
        ["End-Sem 2026", "2026-03-15", 4, "CSE", "CS401", "Operating Systems"],
        ["End-Sem 2026", "2026-03-15", 4, "ECE", "EC401", "Microprocessors"],
        ["End-Sem 2026", "2026-03-15", 6, "MECH", "ME601", "Thermodynamics"],
        ["End-Sem 2026", "2026-03-16", 6, "CSE", "CS601", "Compiler Design"]
    ]
    
    df_schedule = pd.DataFrame(data, columns=[
        'exam_identifier', 'exam_date', 'semester', 'stream', 'subject_code', 'subject_name'
    ])
    df_schedule.to_excel("sample_schedule.xlsx", index=False)
    print("✅ Created sample_schedule.xlsx")

# 3. GENERATE INFRASTRUCTURE
def create_infra_sample():
    print("🏫 Generating Infrastructure...")
    data = [
        ["Hall-101", 5, 4, 2], # 40 capacity
        ["Hall-102", 6, 3, 2], # 36 capacity
        ["Main-Auditorium", 10, 5, 3] # 150 capacity
    ]
    df_infra = pd.DataFrame(data, columns=[
        'hall_name', 'total_rows', 'total_cols', 'bench_capacity'
    ])
    df_infra.to_excel("sample_infrastructure.xlsx", index=False)
    print("✅ Created sample_infrastructure.xlsx")

if __name__ == "__main__":
    try:
        create_student_sample()
        create_schedule_sample()
        create_infra_sample()
        print("\n🚀 All files generated! You can now upload them to SmartSeat AI.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")