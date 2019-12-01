import myutils

vals = myutils.myrd("day1input.txt")

def myfunc(x):
    return x//3-2

# part 1
total = 0
for x in vals:
    total += myfunc(int(x))
print(total)

# part 2
def myfunc2(x):
    total = myfunc(x)
    q = total
    while q > 0:
         tmp = myfunc(q)
         if tmp > 0:         
             total += tmp
         q = tmp
    return total

vals = myutils.myrd("day1input.txt")
total = 0
for x in vals:
    total += myfunc2(int(x))
print(total)
