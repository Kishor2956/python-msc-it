number = int(input("Enter Size of List : "))
duplicate = []

for i in range(number):
    val=int(input())
    duplicate.append(val)

print("Duplicate Number : ")
for i in range(number-1):
    if duplicate[i] == duplicate[i+1]:
        print(duplicate[i])
    