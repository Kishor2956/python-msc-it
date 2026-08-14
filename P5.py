print("Student Rank Processing Engine. \n")
      
number_of_students = int(input("Enter The Number of Students: "))

Student_Details = []

number_of_subjects = 5

for i in range(number_of_students):

    print("\n Enter Student Details")
    print("----------------------------------------")

    Roll_number = input("Enter Roll Number: ")
    Name = input("Enter Name: ")

    Marks = []

    Subjects = ["Data Structure", "Linux System Administration", "Python", "Networking", "Java"]

    for j in range(number_of_subjects):
        Mark = int(input(f"Enter Marks For {Subjects[j]}: "))
        if(Mark >= 0 and Mark <= 100):
            Marks.append(Mark)
        else:
            print("Entered Number of Marks is not valid.")
            

    Student = { "Roll Number" : Roll_number, "Name" : Name, "Marks" : Marks }

    Student_Details.append(Student)    

print("\n Student Details")

for Student in Student_Details:
    print("----------------------------------------")
    for key, value in Student.items():

        print(f"{key}: {value}")
        if(key == "Marks"):
            total = sum(value)
            print("Total Marks :", total)
            percentage = total / number_of_subjects
            print("Percentage Marks :", percentage,"%")
            if(percentage >= 90 and percentage <= 100):
                print("Grade : A")
            elif(percentage >= 80 and percentage < 90):
                print("Grade : B")
            elif(percentage >= 70 and percentage < 80):
                print("Grade : C")
            elif(percentage >= 60 and percentage < 70):
                print("Grade : D")
            else:
                print("Grade : F")


    print("\n Student Rank")
    print("----------------------------------------")

for student in Student_Details:
    student["Total"] = sum(student["Marks"])
    student["Percentage"] = student["Total"] / number_of_subjects


Student_Details.sort(key=lambda student: student["Percentage"], reverse=True)


previous_percentage = None
rank = 0

for student in Student_Details:
    percentage = student["Percentage"]

    if previous_percentage is None or percentage < previous_percentage:
        rank += 1

    print(rank, student["Name"], percentage)

    previous_percentage = percentage
