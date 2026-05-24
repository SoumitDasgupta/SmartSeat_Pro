SELECT exam_schedule.exam_identifier, exam_schedule.exam_date, students.regd_id, students.name, exam_schedule.semester, exam_schedule.stream, exam_schedule.subject_code, exam_schedule.subject_name 
FROM students
JOIN exam_schedule
  ON students.semester = exam_schedule.semester AND students.stream = exam_schedule.stream;
