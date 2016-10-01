"""simple script to reorder the data by columns rather than lines:



A1
A2
A3
B1
B2
B3


becomes

A1
B1
A2
B2
A3
B3


"""


df = pd.read_csv("summary_filtered.csv", sep=";")
index = list(range(96))
reorder = list(flatten([index[i::12] for i in range(0,12)]))


df = df.ix[reorder]
df.to_csv("test.csv", index=False)


