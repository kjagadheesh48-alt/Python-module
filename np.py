import pandas as pd
data = {
    "Name": ["Arun", "Beena", "Charan", "Divya", "Esha"],
    "Math": [78, 66, 90, 55, 80],
    "Science": [85, 74, 88, 60, 72],
    "English": [92, 81, 95, 58, 77]
}
df = pd.DataFrame(data)
df
print(df)
print("Shape:", df.shape)
print("Columns:", df.columns)
print(df["Math"])
print("class average(math)",df["Math"].mean())
print("High english score:",df["English"].max())
df["Average"] = df["Total"] / 3
df
print(df[df["average"]>=80])