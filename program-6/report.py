import csv

def display_students(students):

    print("\n---Rank List---")

    for student in students:

        print("\nRank       :",student[5])
        print("Roll No    :",student[0])
        print("Name       :",student[1])
        print("Total      :",student[2])
        print("Percentage :",round(student[3], 2), "%")
        print("Grade      :",student[4])

def save_ranked_csv(students):

    with open("ranked_students.csv", "w", newline="") as file:

        writer = csv.writer(file)
        writer.writerow(["Roll No", "Name", "Total", "Percentage", "Grade", "Rank"])
        writer.writerows(students)
