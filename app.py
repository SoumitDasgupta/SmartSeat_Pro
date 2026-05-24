import streamlit as st
import pandas as pd
import qrcode
import os
import io
import calendar as pycal
from fpdf import FPDF
from datetime import date
from database_manager import *
from engine import allocate_seats

# --- UI CONFIGURATION ---
st.set_page_config(page_title="SmartSeat AI Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #2e7d32; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #888; }
    .stTabs [data-baseweb="tab--active"] { color: #2e7d32 !important; border-bottom: 2px solid #2e7d32 !important; }
    .sticker-preview-card {
        background-color: #111111; border: 2px solid #2e7d32; padding: 15px; border-radius: 8px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATOR WITH QR ---
def generate_sticker_pdf(hall_data):
    pdf = FPDF(); pdf.set_auto_page_break(auto=True, margin=10); pdf.add_page(); pdf.set_font("Arial", size=10)
    
    for i, row in enumerate(hall_data.itertuples(index=False)):
        # Calculate grid position (2 columns, 5 rows per page)
        w, h = 90, 55; x = 10 + (i % 2) * 95; y = 10 + ((i // 2) % 5) * 60
        if i > 0 and i % 10 == 0: pdf.add_page()
        
        pdf.rect(x, y, w, h)
        pdf.set_xy(x, y+5); pdf.set_font("Arial", 'B', 10); pdf.cell(w, 5, "EXAM SEATING", ln=1, align='C')
        
        # Accessing by attribute name (requires explicit DataFrame columns)
        pdf.set_xy(x, y+15); pdf.set_font("Arial", 'B', 11)
        pdf.cell(w, 8, str(row.display_id), ln=1, align='C')
        
        pdf.set_xy(x, y+25); pdf.set_text_color(200, 0, 0); pdf.set_font("Arial", 'B', 24)
        pdf.cell(w, 12, str(row.seat_label), ln=1, align='C'); pdf.set_text_color(0, 0, 0)
        
        # QR Code Generation
        qr_data = f"STU_ID:{row.regd_id}"
        qr = qrcode.make(qr_data); qr_path = f"temp_{row.regd_id}.png"; qr.save(qr_path)
        pdf.image(qr_path, x + w - 18, y + h - 18, 15, 15)
        if os.path.exists(qr_path): os.remove(qr_path)
        
    return bytes(pdf.output())

# --- MAIN NAVIGATION ---
page = st.sidebar.radio("Navigation", ["🔍 Student Search", "🛡️ Admin Portal"])

if page == "🔍 Student Search":
    st.title("🎓 STUDENT PORTAL")
    regd_input = st.text_input("ENTER REGISTRATION ID").strip().upper()
    if regd_input:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT name FROM students WHERE regd_id = %s", (regd_input,))
        student = cur.fetchone()
        if student:
            st.success(f"Welcome, {student[0]}")
            cur.execute("SELECT exam_date, subject, hall_name, seat_label FROM final_allocations WHERE regd_id = %s", (regd_input,))
            results = cur.fetchall()
            if results:
                for ex in results:
                    with st.expander(f"📅 {ex[0]} — {ex[1]}", expanded=True):
                        st.write(f"**HALL:** {ex[2]} | **SEAT:** {ex[3]}")
            else: st.info("No seating found for upcoming exams.")
        else: st.error("ID NOT FOUND.")
        cur.close(); conn.close()

else:
    if "auth" not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.title("🛡️ ADMIN LOGIN")
        pwd = st.text_input("ENTER ACCESS KEY", type="password")
        if st.button("UNLOCK DASHBOARD"):
            if pwd == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied.")
    else:
        st.title("🛡️ ADMIN CONTROL CENTER")
        t1, t2, t3, t4 = st.tabs(["📁 DATA SYNC", "📅 SCHEDULE", "⚙️ ALLOCATION", "📊 MASTER PLAN"])
        
        with t1:
            st.subheader("Database Management")
            h_f = st.file_uploader("Upload Halls (.xlsx)", type=['xlsx'])
            s_f = st.file_uploader("Upload Students (.xlsx)", type=['xlsx'])
            if st.button("SYNC DATABASES"):
                if h_f and s_f:
                    upload_halls(pd.read_excel(h_f))
                    upload_students(pd.read_excel(s_f))
                    st.success("Infrastructure and Student data updated successfully.")

        with t2:
            st.subheader("Exam Scheduling")
            sch_f = st.file_uploader("Upload Master Schedule (.xlsx)", type=['xlsx'])
            if st.button("PUBLISH SCHEDULE"):
                if sch_f:
                    upload_schedule(pd.read_excel(sch_f))
                    st.success("Schedule live.")

        with t3:
            st.subheader("Seating Engine")
            c1, c2 = st.columns(2)
            d = c1.date_input("Target Date", value=date.today())
            name = c2.text_input("Exam Name (e.g., End-Sem)", "End-Sem 2026")
            mix = st.multiselect("Interleave (Mix) By", ["stream", "semester", "section"])
            gap = st.checkbox("Gap Seating (One seat distance)")
            
            if st.button("🚀 GENERATE ALLOCATION"):
                conn = get_connection(); cur = conn.cursor()
                cur.execute("SELECT regd_id, name, stream, year, semester, section, roll_no FROM students"); s = cur.fetchall()
                cur.execute("SELECT hall_name, total_rows, total_cols, bench_capacity FROM infrastructure"); h = cur.fetchall()
                cur.execute("SELECT exam_identifier, exam_date, semester, stream, subject_code, subject_name FROM exam_schedule"); sch = cur.fetchall()
                cur.close(); conn.close()
                
                plan = allocate_seats(s, h, sch, ["semester", "roll_no"], mix, d, name, gap)
                if plan:
                    st.session_state.current_plan = pd.DataFrame(plan)
                    st.dataframe(st.session_state.current_plan, use_container_width=True)
            
            if 'current_plan' in st.session_state:
                if st.button("💾 SAVE & PUBLISH"):
                    save_final_allocation(st.session_state.current_plan.to_dict('records'))
                    st.success("Allocation is now live on the Student Portal.")

        with t4:
            st.subheader("Master Plan & Downloads")
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT DISTINCT exam_date FROM final_allocations ORDER BY exam_date DESC")
            dates = [row[0] for row in cur.fetchall()]
            cur.close(); conn.close()
    
            sel_date = st.selectbox("Select Published Date", dates if dates else ["No allocations published"])
            if sel_date != "No allocations published":
                conn = get_connection(); cur = conn.cursor()
                cur.execute("""
                    SELECT exam_identifier, exam_date, regd_id, student_name, 
                           hall_name, seat_label, display_id, subject 
                    FROM final_allocations WHERE exam_date = %s
                """, (sel_date,))
        
                df_plan = pd.DataFrame(cur.fetchall(), columns=[
                    'exam_identifier', 'exam_date', 'regd_id', 'student_name', 
                    'hall_name', 'seat_label', 'display_id', 'subject'
                ])
                cur.close(); conn.close()

                # --- NEW FILTERING SECTION ---
                st.markdown("---")
                fi_col1, fi_col2 = st.columns([2, 1])
                
                # Global Text Search
                search_query = fi_col1.text_input("🔍 Search by Name, ID, or Hall", placeholder="Type to filter...")
                
                # Multi-select for Subjects/Streams
                available_subs = sorted(df_plan['subject'].unique())
                selected_subs = fi_col2.multiselect("Filter by Subject", available_subs)

                # Apply Filters to the dataframe
                filtered_df = df_plan.copy()
                if search_query:
                    filtered_df = filtered_df[
                        filtered_df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().str.cat(), axis=1)
                    ]
                if selected_subs:
                    filtered_df = filtered_df[filtered_df['subject'].isin(selected_subs)]

                # Display the filtered table
                st.dataframe(filtered_df, use_container_width=True)
                # -----------------------------
        
                st.write(f"### Download Stickers for {sel_date}")
                # We use the filtered_df here so downloads match your search
                halls = filtered_df['hall_name'].unique()
                
                if len(halls) == 0:
                    st.warning("No data matches your filters.")
                else:
                    cols = st.columns(3)
                    for i, h_name in enumerate(halls):
                        h_data = filtered_df[filtered_df['hall_name'] == h_name]
                        pdf_bytes = generate_sticker_pdf(h_data)
                        with cols[i % 3]:
                            st.download_button(
                                f"PDF: {h_name}", 
                                pdf_bytes, 
                                f"Stickers_{h_name}_{sel_date}.pdf", 
                                key=f"dl_{h_name}_{i}"
                            )