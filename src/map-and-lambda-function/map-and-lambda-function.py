#4. Write a program that can map() to make a list whose elements are squares of numbers between 1 and 20 (both included).
# Hints:
# Use map() to generate a list.
# Use Lambda to define anonymous functions

print (list(map(lambda x : x**2 , range(1,21))))