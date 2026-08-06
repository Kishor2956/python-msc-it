password = input("Enter a Password: ")
uppercase = False
lowercase = False
digit = False
special = False
repeated = False
special_characters = "!@#$%^&*()-_=+[]{}|\\/:;'<>,.?"

for i in range(len(password)):
    char = password[i]
    if char.isupper():
        uppercase = True
    if char.islower():
        lowercase = True
    if char.isdigit():
        digit = True
    if char in special_characters:
        special = True
    if i > 0 and password[i] == password[i - 1]:
        repeated = True

print("Password Strength Analysis:")
print(f"Uppercase Letters: {uppercase}")
print(f"Lowercase Letters: {lowercase}")
print(f"Digits: {digit}")
print(f"Special Characters: {special}")
print(f"Repeated Characters: {repeated}")

if uppercase and lowercase and digit and special and not repeated:
    print(" Your Password is Strong")
else:
    print(" Your Password is Weak")
