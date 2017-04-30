import pandas as pd

df = pd.DataFrame.from_csv("fake.csv")
df = df[df["language"] == 'english']
print("English: " + str(df.shape[0]))
df = df[["text"]]

# Make all classes as Fake
df["class"] = "Fake"
df.to_csv("kaggle-fake-news.csv", index=False)
