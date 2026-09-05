from database import get_all_evaluations

for row in get_all_evaluations():
    print(row)