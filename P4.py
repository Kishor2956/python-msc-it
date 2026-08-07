paragraph = input("Enter a Paragraph : ")

words = paragraph.split()
word_count = Counter(words)

print("Number Appears in the Paragraph :", paragraph.count("word"))
print("Number of Unique words :", len(word_count))
print("Words in list :", words)
print("Number of words :", len(words))
print("Number of characters :", len(paragraph))

characters_without_spaces = sum(1 for ch in paragraph if ch != " ")
print("Number of characters without spaces :", characters_without_spaces)

longest = ""
shortest = words[0]

for word in words:
    if len(word) > len(longest):
        longest = word
    if len(word) < len(shortest):
        shortest = word

print("Longest word :", longest)
print("Shortest word :", shortest)

repeated = []
for word, count in word_count.items():
    if count > 1:
        repeated.append(word)

print("Repeated words :", repeated)
print("The original paragraph :", paragraph)
