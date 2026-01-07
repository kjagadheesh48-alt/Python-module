import plotly.express as px
import pandas as pd
num_students = int(input("Enter number of students: "))
names = []
math_marks = []
science_marks = []
english_marks = []
for i in range(num_students):
    print(f"\nEnter details for student {i+1}:")
    name = input("Name: ")
    math = int(input("Math marks: "))
    science = int(input("Science marks: "))
    english = int(input("English marks: "))
    names.append(name)
    math_marks.append(math)
    science_marks.append(science)
    english_marks.append(english)
data = {
    "Name": names,
    "Math": math_marks,
    "Science": science_marks,
    "English": english_marks
}
df = pd.DataFrame(data)
print(df)
fig = px.line(df, x="Name", y="Math", title="Math Marks - Interactive Bar Chart")
fig.show()
