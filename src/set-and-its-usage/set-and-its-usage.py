# With a given list [12,24,35,24,88,120,155,88,120,155], write a program to print this list after removing all duplicate values with original order reserved.
# Hint: Use set() to store a number of values without duplicates.


# ----------------Method - 1 ------------------
# seen = set()
# newlist = []
# for i in list:
#     if i not in seen:
#         newlist.append(i)
#         seen.add(i)

# print(newlist)

# ----------------Method - 2 ------------------a

list = [12,24,35,24,88,120,155,88,120,155]
seen = set()

for i in list:
    seen.add(i)

print(seen)
