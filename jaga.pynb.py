import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


# 1. CREATE SIMPLE DATA

data = {
    "Study_Hours": [2, 4, 6, 8, 10, 3, 5, 7, 9, 1],
    "Internal_Marks": [35, 45, 55, 65, 75, 40, 50, 60, 70, 30],
    "Final_Marks": [40, 48, 58, 68, 78, 42, 52, 62, 72, 35]
}

df = pd.DataFrame(data)

df["Result"] = df["Final_Marks"].apply(lambda x: 1 if x >= 50 else 0)

df.head()

# 2. SIMPLE EDA
df.describe()

sns.heatmap(df.corr(), annot=True)
plt.show()

# 3. SIMPLE VISUALIZATION
plt.scatter(df["Study_Hours"], df["Final_Marks"])
plt.xlabel("Study Hours")
plt.ylabel("Final Marks")
plt.show()

# 4. MACHINE LEARNING MODEL
X = df[["Study_Hours", "Internal_Marks"]]
y = df["Result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

ml = LogisticRegression()
ml.fit(X_train, y_train)

y_pred = ml.predict(X_test)
print("ML Accuracy:", accuracy_score(y_test, y_pred))

# 5. DEEP LEARNING (ANN)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

ann = Sequential([
    Dense(8, activation="relu", input_shape=(2,)),
    Dense(1, activation="sigmoid")
])

ann.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
ann.fit(X_train, y_train, epochs=20, verbose=1)

