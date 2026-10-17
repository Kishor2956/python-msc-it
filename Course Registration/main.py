from datetime import datetime


class Course:
    def __init__(self, code, day, start, end):
        self.code = code
        self.day = day
        self.start = start
        self.end = end

    def __str__(self):
        return (f"{self.code} | {self.day} | "
                f"{self.start} - {self.end}")


class Student:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

    def detect_conflicts(self):
        conflicts = []

        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                c1 = self.courses[i]
                c2 = self.courses[j]

                if (c1.day == c2.day and
                    c1.start < c2.end and
                    c2.start < c1.end):
                    conflicts.append((c1, c2))

        return conflicts

    def __str__(self):
        return (f"Student ID: {self.sid}\n"
                f"Student Name: {self.name}\n"
                f"Total Courses: {len(self.courses)}")


def get_time(prompt):
    while True:
        try:
            time_str = input(prompt).strip()
            return datetime.strptime(
                time_str, "%H:%M"
            ).strftime("%H:%M")
        except ValueError:
            print("Invalid time! Enter in HH:MM format (e.g. 09:30).")


def get_day():
    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    while True:
        day = input("Enter day: ").strip().capitalize()

        if day in days:
            return day
        print("Invalid day! Enter a valid weekday.")


def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("Enter a number greater than zero.")
        except ValueError:
            print("Invalid input! Enter an integer.")


def main():
    students = []
    n = get_positive_int("Enter number of students: ")

    for i in range(n):
        print(f"\n--- Student {i + 1} ---")

        while True:
            sid = input("Enter Student ID: ").strip()
            if sid:
                break
            print("Student ID cannot be empty.")

        while True:
            name = input("Enter Student Name: ").strip()
            if name and all(ch.isalpha() or ch.isspace()
                            for ch in name):
                break
            print("Name must contain only letters and spaces.")

        student = Student(sid, name)
        count = get_positive_int("Enter number of courses: ")

        for j in range(count):
            print(f"\nCourse {j + 1}")

            while True:
                code = input("Enter Course Code: ").strip().upper()
                if code:
                    break
                print("Course code cannot be empty.")

            day = get_day()

            while True:
                start = get_time("Enter Start Time (HH:MM): ")
                end = get_time("Enter End Time (HH:MM): ")

                if start < end:
                    break
                print("End time must be later than start time.")

            course = Course(code, day, start, end)
            student.add_course(course)

        students.append(student)

    print("\n========== STUDENT TIMETABLES ==========")

    for student in students:
        print("\n" + str(student))
        conflicts = student.detect_conflicts()

        if conflicts:
            print("Conflicting Course Pairs:")
            for c1, c2 in conflicts:
                print(f"{c1.code} ({c1.day}, "
                      f"{c1.start}-{c1.end}) overlaps with "
                      f"{c2.code} ({c2.day}, "
                      f"{c2.start}-{c2.end})")
        else:
            print("No conflicts. Timetable:")
            for course in student.courses:
                print(course)


if __name__ == "__main__":
    main()
