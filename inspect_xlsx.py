import pandas as pd

# Load the Excel file
xlsx_path = 'data/Strivers.xlsx'
df = pd.read_excel(xlsx_path)

# Print the first few rows and the column names
print("Column names:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

# Count the number of problems per category
category_counts = df['Category'].value_counts()
print("\nProblems per category:")
print(category_counts)

# Count the number of problems per difficulty level
difficulty_counts = df['Level of Difficulty'].value_counts()
print("\nProblems per difficulty level:")
print(difficulty_counts)
