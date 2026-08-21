def rank_students(students):

    students.sort(key=lambda x: x[2], reverse=True)

    rank = 0
    last_marks = -1

    for student in students:

        if student[2] != last_marks:
            rank = rank + 1
            last_marks = student[2]

        student.append(rank)

    return students
