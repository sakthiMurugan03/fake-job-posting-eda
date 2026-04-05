import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("ggplot")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("fake_job_postings.csv")

print("Shape:", df.shape)
print(df.head())
print(df.info())

# =========================
# BASIC CLEANING
# =========================
df["description"] = df["description"].astype(str)
df["company_profile"] = df["company_profile"].astype(str)
df["requirements"] = df["requirements"].astype(str)
df["benefits"] = df["benefits"].astype(str)

# =========================
# FEATURE ENGINEERING
# =========================
df["desc_len"] = df["description"].apply(len)
df["company_len"] = df["company_profile"].apply(len)
df["req_len"] = df["requirements"].apply(len)
df["benefits_len"] = df["benefits"].apply(len)

df["desc_words"] = df["description"].apply(lambda x: len(x.split()))
df["title_words"] = df["title"].astype(str).apply(lambda x: len(x.split()))

df["has_salary"] = df["salary_range"].notnull().astype(int)

# =========================
# TARGET DISTRIBUTION
# =========================
plt.figure(figsize=(6,4))
sns.countplot(x="fraudulent", data=df)
plt.title("Real vs Fake Job Posts")
plt.show()

fraud_pct = df["fraudulent"].value_counts(normalize=True) * 100
print("\nFraud Percentage:\n", fraud_pct)

# =========================
# DESCRIPTION LENGTH
# =========================
plt.figure(figsize=(8,5))
sns.histplot(df["desc_len"], bins=60)
plt.title("Description Length Distribution")
plt.show()

plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="desc_len", data=df)
plt.title("Fake vs Real — Description Length")
plt.show()

# =========================
# COMPANY PROFILE ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="company_len", data=df)
plt.title("Company Profile Length vs Fraud")
plt.show()

# =========================
# REQUIREMENTS ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="req_len", data=df)
plt.title("Requirements Length vs Fraud")
plt.show()

# =========================
# BENEFITS ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="benefits_len", data=df)
plt.title("Benefits Length vs Fraud")
plt.show()

# =========================
# REMOTE JOB ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.countplot(x="telecommuting", hue="fraudulent", data=df)
plt.title("Remote Jobs vs Fake")
plt.show()

# =========================
# COMPANY LOGO ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.countplot(x="has_company_logo", hue="fraudulent", data=df)
plt.title("Company Logo vs Fake")
plt.show()

# =========================
# QUESTIONS ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.countplot(x="has_questions", hue="fraudulent", data=df)
plt.title("Questions vs Fake Jobs")
plt.show()

# =========================
# WORD COUNT ANALYSIS
# =========================
plt.figure(figsize=(6,4))
sns.boxplot(x="fraudulent", y="desc_words", data=df)
plt.title("Word Count vs Fraud")
plt.show()

# =========================
# TOP FAKE JOB TITLES
# =========================
fake_titles = df[df["fraudulent"]==1]["title"].value_counts().head(10)

plt.figure(figsize=(8,5))
fake_titles.plot(kind="bar")
plt.title("Most Common Fake Job Titles")
plt.show()

print("\nTop Fake Job Titles:")
print(fake_titles)

# =========================
# CORRELATION HEATMAP
# =========================
plt.figure(figsize=(12,8))
sns.heatmap(
    df.select_dtypes(include=np.number).corr(),
    annot=True,
    cmap="coolwarm"
)
plt.title("Correlation Matrix")
plt.show()

# =========================
# FRAUD RATE BY FEATURE
# =========================
print("\nFraud Rate by Remote:")
print(df.groupby("telecommuting")["fraudulent"].mean())

print("\nFraud Rate by Logo:")
print(df.groupby("has_company_logo")["fraudulent"].mean())

print("\nFraud Rate by Questions:")
print(df.groupby("has_questions")["fraudulent"].mean())

# =========================
# SUSPICIOUS JOB SCORE
# =========================
df["suspicious_score"] = (
    (df["desc_len"] < 200).astype(int) +
    (df["company_len"] < 50).astype(int) +
    (df["req_len"] < 50).astype(int) +
    (df["has_company_logo"] == 0).astype(int) +
    (df["telecommuting"] == 1).astype(int)
)

suspicious = df.sort_values("suspicious_score", ascending=False)

print("\nMost Suspicious Jobs:")
print(
    suspicious[
        ["title","location","suspicious_score","fraudulent"]
    ].head(10)
)

# =========================
# PAIRPLOT (ADVANCED)
# =========================
sns.pairplot(
    df[
        ["desc_len","company_len","req_len","benefits_len","fraudulent"]
    ].sample(1000),
    hue="fraudulent"
)
plt.show()

# =========================
# FINAL INSIGHTS
# =========================
print("\n===== FINAL INSIGHTS =====")
print("Fake jobs tend to have:")
print("- Short descriptions")
print("- No company profile")
print("- No requirements")
print("- Remote work")
print("- No company logo")
print("- Minimal benefits")