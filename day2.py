op_dict = {1:lambda x,y: x+y, 2:lambda x,y: x*y}
current_pos = 0

with open("day2input.txt", "r") as f:
    content = f.read()

myls = [int(x) for x in content.split(",")]
myls[1] = 12
myls[2] = 2  # replacements from instructions

while True:
    opcode = myls[current_pos]
    if opcode == 99:
        break
    operation = op_dict[opcode]
    x = myls[myls[current_pos+1]]
    y = myls[myls[current_pos+2]]
    dest = myls[current_pos+3]
    answer = operation(x, y)
    myls[dest] = answer
    current_pos += 4

print(myls)
