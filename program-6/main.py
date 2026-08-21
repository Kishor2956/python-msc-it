from student import get_students, save_csv
from ranking import rank_students
from report import display_students, save_ranked_csv


try:

    students = get_students()

    if students:

        save_csv(students)

        students = rank_students(students)

        display_students(students)

        save_ranked_csv(students)

        print("\nCSV Files Created Successfully")

except ValueError:

    print("Please Enter Valid Data!")

except FileNotFoundError:

    print("File Not Found!")
