import pandas as pd
import streamlit as st

def allocate_seats(students_raw, halls_raw, schedule_raw, sort_order, interleave_cols, target_date, exam_name, gap_mode=False):
    """
    Core allocation method for a single exam instance.
    """
    df_s = pd.DataFrame(students_raw, columns=['regd_id', 'name', 'stream', 'year', 'semester', 'section', 'roll_no'])
    df_h = pd.DataFrame(halls_raw, columns=['hall_name', 'rows', 'cols', 'b_cap'])
    df_sch = pd.DataFrame(schedule_raw, columns=['ex_id', 'ex_date', 'sem', 'stream', 'sub_code', 'sub_name'])

    df_sch['ex_date'] = pd.to_datetime(df_sch['ex_date']).dt.date
    current_schedule = df_sch[(df_sch['ex_date'] == target_date) & (df_sch['ex_id'] == exam_name)]
    
    if current_schedule.empty:
        return []

    df_joined = pd.merge(df_s, current_schedule[['sem', 'stream', 'sub_name', 'sub_code']], 
                         left_on=['semester', 'stream'], right_on=['sem', 'stream'], how='inner')

    if df_joined.empty:
        return []

    # --- CAPACITY VALIDATION ---
    total_capacity = (df_h['rows'] * df_h['cols'] * df_h['b_cap']).sum()
    available_seats = total_capacity // 2 if gap_mode else total_capacity
    
    if len(df_joined) > available_seats:
        st.error(f"🚨 CAPACITY EXCEEDED on {target_date}: {len(df_joined)} students, but only {available_seats} seats.")
        return []

    # --- MIXING LOGIC ---
    if interleave_cols:
        df_joined['group_id'] = df_joined[interleave_cols].astype(str).agg('-'.join, axis=1)
        if sort_order: df_joined = df_joined.sort_values(by=sort_order)
        groups = [group for _, group in df_joined.groupby('group_id', sort=False)]
        interleaved = []
        max_len = max(len(g) for g in groups)
        for i in range(max_len):
            for g in groups:
                if i < len(g): interleaved.append(g.iloc[i])
        sorted_list = interleaved
    else:
        if sort_order: df_joined = df_joined.sort_values(by=sort_order)
        sorted_list = [row for _, row in df_joined.iterrows()]

    # --- PHYSICAL ALLOCATION ---
    final_plan = []; s_idx = 0; seat_counter = 0
    for _, hall in df_h.iterrows():
        for r in range(1, int(hall['rows']) + 1):
            for c in range(1, int(hall['cols']) + 1):
                for b in range(1, int(hall['b_cap']) + 1):
                    if s_idx < len(sorted_list):
                        if gap_mode and (seat_counter % 2 != 0):
                            seat_counter += 1
                            continue
                        
                        s = sorted_list[s_idx]
                        final_plan.append({
                            'exam_identifier': exam_name, 'exam_date': target_date,
                            'regd_id': s['regd_id'], 'student_name': s['name'],
                            'hall_name': hall['hall_name'], 'seat_label': f"R{r}-C{c}-B{b}",
                            'display_id': f"{s['stream']} | Sem {s['semester']} | Sec {s['section']} | Roll {s['roll_no']}",
                            'subject': f"{s['sub_code']} - {s['sub_name']}"
                        })
                        s_idx += 1
                        seat_counter += 1
    return final_plan

def batch_allocate_full_schedule(students_raw, halls_raw, schedule_raw, sort_order, interleave_cols, gap_mode=False):
    """
    Loop logic to process every unique exam date found in the schedule.
    """
    df_sch = pd.DataFrame(schedule_raw, columns=['ex_id', 'ex_date', 'sem', 'stream', 'sub_code', 'sub_name'])
    df_sch['ex_date'] = pd.to_datetime(df_sch['ex_date']).dt.date
    
    # Identify all unique exam events (Date + Name combo)
    unique_exams = df_sch[['ex_date', 'ex_id']].drop_duplicates().values.tolist()
    
    full_master_plan = []
    
    for exam_date, exam_name in unique_exams:
        day_plan = allocate_seats(students_raw, halls_raw, schedule_raw, sort_order, interleave_cols, exam_date, exam_name, gap_mode)
        if day_plan:
            full_master_plan.extend(day_plan)
            
    return full_master_plan