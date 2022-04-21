
with open("eksempel_input.txt", "r", encoding="utf-8") as file:
    line_list = []
    for line in file:
        line_list = [x.strip() for x in line.split(",")]
        print(line_list)

