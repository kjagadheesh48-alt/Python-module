import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
data = {
    "Name": ["Arun", "Beena", "Charan", "Divya", "Esha"],
    "Math": [78, 66, 90, 55, 80],
    "Science": [85, 74, 88, 60, 72],
    "English": [92, 81, 95, 58, 77]
}

df = pd.DataFrame(data)

df_long = df.melt(id_vars="Name", var_name="Subject", value_name="Marks")

sns.barplot(data=df_long, x="Subject", y="Marks")
plt.title("Average Marks per Subject")
plt.show()
sns.countplot(data=df_long, x="Subject")
plt.title("Number of Marks Entries per Subject")
plt.show()
sns.boxplot(data=df_long, x="Subject", y="Marks")
plt.title("Marks Distribution per Subject")
plt.show()