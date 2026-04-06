# ============================================
# FAKE JOB POSTING DETECTION - FULL EDA SCRIPT
# Includes:
# 1. Descriptive Statistics
# 2. Missing Value Handling
# 3. Data Merging
# 4. OLAP Operations
# 5. Data Representation
# 6. Time Variant (simulated)
# 7. Hypothesis Testing
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.style.use("ggplot")

# ============================================
# 1. LOAD DATASET
# ============================================
# Loads dataset into dataframe
df = pd.read_csv("fake_job_postings.csv")

print("Dataset Shape:", df.shape)
print(df.head())

# ============================================
# 2. DESCRIPTIVE STATISTICS
# ============================================
# Shows summary statistics of dataset
print("\nDescriptive Statistics")
print(df.describe())

print("\nColumn Information")
print(df.info())

# ============================================
# 3. MISSING VALUE HANDLING
# ============================================
print("\nMissing Values")
print(df.isnull().sum())

# Fill missing values for text columns
df["description"] = df["description"].fillna("")
df["company_profile"] = df["company_profile"].fillna("")
df["requirements"] = df["requirements"].fillna("")
df["benefits"] = df["benefits"].fillna("")

# ============================================
# 4. DATA MERGING 
# ============================================
# Creating dummy dataset and merging
temp = df[["title","fraudulent"]].copy()
merged_df = pd.merge(df, temp, on="title", how="left")

print("\nData merged successfully")

# ============================================
# 5. FEATURE ENGINEERING
# ============================================
df["desc_len"] = df["description"].apply(len)
df["company_len"] = df["company_profile"].apply(len)
df["req_len"] = df["requirements"].apply(len)
df["benefits_len"] = df["benefits"].apply(len)

df["desc_words"] = df["description"].apply(lambda x: len(x.split()))

# ============================================
# 6. OLAP OPERATIONS (GROUP BY ANALYSIS)
# ============================================
print("\nOLAP Analysis")

print("Fraud Rate by Remote")
print(df.groupby("telecommuting")["fraudulent"].mean())

print("Fraud Rate by Logo")
print(df.groupby("has_company_logo")["fraudulent"].mean())

print("Fraud Rate by Questions")
print(df.groupby("has_questions")["fraudulent"].mean())

# Pivot Table
pivot = pd.pivot_table(
    df,
    values="desc_len",
    index="has_company_logo",
    columns="fraudulent",
    aggfunc=np.mean
)

print("\nPivot Table")
print(pivot)

# ============================================
# 7. DATA REPRESENTATION (VISUALIZATION)
# ============================================

# Fake vs Real
plt.figure(figsize=(6,4))
sns.countplot(x="fraudulent", data=df)
plt.title("Fake vs Real Jobs")
plt.show()

# Description length
plt.figure(figsize=(6,4))
sns.histplot(df["desc_len"])
plt.title("Description Length")
plt.show()

# Boxplot
plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="desc_len", data=df)
plt.title("Fake vs Real Description Length")
plt.show()

# ============================================
# 8. TIME VARIANT ANALYSIS (SIMULATED)
# ============================================
# dataset has no time column, so create simulated time
df["index_time"] = np.arange(len(df))

plt.figure(figsize=(8,4))
plt.plot(df["index_time"], df["desc_len"])
plt.title("Time Variant Analysis")
plt.show()

# ============================================
# 9. HYPOTHESIS TESTING
# ============================================
# H0: Fake and real jobs have same description length
# H1: Fake jobs have different description length

fake = df[df["fraudulent"]==1]["desc_len"]
real = df[df["fraudulent"]==0]["desc_len"]

t_stat, p_value = stats.ttest_ind(fake, real)

print("\nHypothesis Testing")
print("T-statistic:", t_stat)
print("P-value:", p_value)

if p_value < 0.05:
    print("Reject Null Hypothesis")
else:
    print("Fail to Reject Null Hypothesis")

# ============================================
# 10. CORRELATION HEATMAP
# ============================================
plt.figure(figsize=(10,6))
sns.heatmap(
    df.select_dtypes(include=np.number).corr(),
    annot=True
)
plt.title("Correlation Heatmap")
plt.show()

# ============================================
# 11. SUSPICIOUS SCORE
# ============================================
df["suspicious_score"] = (
    (df["desc_len"] < 200).astype(int) +
    (df["company_len"] < 50).astype(int) +
    (df["req_len"] < 50).astype(int) +
    (df["has_company_logo"] == 0).astype(int)
)

suspicious = df.sort_values("suspicious_score", ascending=False)

print("\nMost Suspicious Jobs")
print(suspicious[["title","suspicious_score"]].head())

# ============================================
# FINAL INSIGHTS
# ============================================
print("\nFinal Insights")
print("Fake jobs tend to:")
print("Short descriptions")
print("No company logo")
print("Less requirements")
print("Minimal benefits")