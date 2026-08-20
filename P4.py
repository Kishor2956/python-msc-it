from collections import Counter
paragraph = input("Enter a Paragraph : ")

word = paragraph.split()
word_count = Counter(word)

print("Number Appears in the Paragraph : ", paragraph.count("word"))
print("Number of Unique Words : ", len(word_count))
print("Words in List : " , word)
print("Number of Words : ", len(word))
print("Number of Characters : ", len(paragraph))

characters_without_spaces = sum(1 for ch in paragraph if ch != " ")
print("Number of Characters Without Spaces : ", characters_without_spaces)

longest = ""
shortest = word[0]

for w in word:
    if len(word) > len(longest):
        longest = word
    if len(word) < len(shortest):
        shortest = word

print("Longest Word : ", longest)
print("Shortest Word : ", shortest)

repeated = []
for word, count in word_count.items():
    if count > 1:
        repeated.append(word)

print("Repeated Words : ", repeated)
print("The Original Paragraph : ", paragraph)
