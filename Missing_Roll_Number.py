nums = list(map(int, input("Enter Roll Numbers Separated by Spaces : ").split()))

for i in range(1, max(nums) + 1):
    if i not in nums:
        print("Missing Roll Number :", i)
