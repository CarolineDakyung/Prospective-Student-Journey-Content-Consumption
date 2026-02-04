import pandas as pd
import numpy as np


# Load Excel file exported from Google Analytics (UCLA internal data)
# NOTE: Raw data is not publicly available due to privacy restrictions.
# Replace 'msba_only2.xlsx' with your own exported file if reproducing.

DATA_PATH = "msba_only2.xlsx"

df = pd.read_excel(DATA_PATH, header=1)


df.columns = [
    'DateHour',         # Date + hour (YYYYMMDDHH)
    'PagePath',         # Page path + query string
    'UserType',         # New / established
    'Source',           # Session source
    'Sessions',    # Sessions (MSBA Only)
    'EngRate',     # Engagement rate (MSBA Only)
    'KeyEvents',      # Key events (MSBA Only)
    'EngTime',     # Engagement Time (MSBA Only)
    'Sessions1',   # Sessions (Totals)
    'EngRate1',    # Engagement rate (Totals)
    'KeyEvents1',     # Key events (Totals)
    'EngTime1'     # Engagement Time (Totals)
]

df.head()


are_identical = df['EngRate'].equals(df['EngRate1'])
print(f"EngRate columns are identical: {are_identical}")

are_identical = df['KeyEvents'].equals(df['KeyEvents1'])
print(f"KeyEvents columns are identical: {are_identical}")

are_identical = df['EngTime'].equals(df['EngTime1'])
print(f"EngTime columns are identical: {are_identical}")

are_identical = df['Sessions'].equals(df['Sessions1'])
print(f"EngTime columns are identical: {are_identical}")


df = df.drop(columns = ['EngRate1', 'KeyEvents1', 'EngTime1', 'Sessions1'])


import statsmodels.formula.api as smf

# 1. Define Funnel Stages
def get_funnel_stage(path):
    path = str(path).lower()
    if 'apply' in path: return 'Bottom'
    if any(x in path for x in ['career', 'finance', 'admissions']): return 'Middle'
    return 'Top'

df['FunnelStage'] = df['PagePath'].apply(get_funnel_stage)

# 2. Run Regression (Scrapped 'Hour', added 'FunnelStage')
# Interpreting: "How much extra engagement does moving to the next funnel stage drive?"
model_time = smf.ols('EngTime ~ C(FunnelStage) + C(UserType)', data=df).fit()

model_rate = model_rate = smf.ols(
    formula='EngRate ~ C(FunnelStage, Treatment(reference="Top")) * C(UserType)', 
    data=df
).fit()

print(model_time.summary())

print(model_rate.summary())


def categorize_refined(path):
    path = str(path).lower()
    # High Intent (Bottom)
    if 'apply' in path: return 'Application'
    
    # Consideration (Middle)
    if any(x in path for x in ['career', 'placement', 'outcomes']): return 'Career'
    if any(x in path for x in ['financing', 'tuition', 'fellows', 'fees']): return 'Finance'
    if any(x in path for x in ['admissions', 'prerequisites', 'requirements', 'faq']): return 'Admissions'
    if any(x in path for x in ['academics', 'curriculum', 'capstone']): return 'Academics'
    
    # New Categories (Refining "General")
    if 'mba' in path or 'financial-engineering' in path or 'phd' in path: return 'Competitor Program'
    if 'faculty' in path or 'team' in path: return 'Faculty'
    if 'company' in path or 'companies' in path: return 'Corporate'
    if path == '/' or path == '/degrees/master-of-science-in-business-analytics-msba': return 'Homepage'
    
    return 'General Info'

df['Category'] = df['PagePath'].apply(categorize_refined)

# Update Funnel Mapping
def define_funnel_refined(category):
    if category == 'Application': return 'Bottom'
    if category in ['Admissions', 'Finance', 'Career', 'Faculty', 'Corporate']: return 'Middle'
    if category in ['Competitor Program']: return 'Cross-Shopping' # Interesting new segment!
    return 'Top'

df['FunnelStage'] = df['Category'].apply(define_funnel_refined)

# --- FIX 2: HANDLE OUTLIERS (CAPPING) ---
# Cap EngTime at the 99th percentile (approx 30 mins) to remove "sleepers"
cap_value = df['EngTime'].quantile(0.99)
df['EngTime_Capped'] = np.where(df['EngTime'] > cap_value, cap_value, df['EngTime'])

# --- FIX 3: CREATE "ACTIVE" DATASET ---
# For the "Time" regression, only look at non-zero sessions
df_active = df[df['EngTime'] > 0].copy()


model_time2 = smf.ols('EngTime_Capped ~ C(FunnelStage) + C(UserType)', data=df_active).fit()

model_rate2 = model_rate = smf.ols(
    formula='EngRate ~ C(FunnelStage, Treatment(reference="Top")) * C(UserType)', 
    data=df
).fit()

print(model_time2.summary())

print(model_rate2.summary())


pivot_rate = df_active.pivot_table(
    index='FunnelStage', 
    columns='UserType', 
    values='EngRate', 
    aggfunc='mean'
)

# Metric 2: The "Effort" Metric (High Depth)
# We want to show they are working hard (spending time) when they ARE there.
pivot_time = df_active.pivot_table(
    index='FunnelStage', 
    columns='UserType', 
    values='EngTime_Capped', 
    aggfunc='mean'
)

print("--- QUANTIFYING THE GAP ---")
print("Engagement Rate (Stickiness):")
print(pivot_rate)
print("\nEngagement Time (Effort):")
print(pivot_time)

# Calculate the "Frustration Index" for New Users
# Frustration = High Effort (Time) / Low Success (Rate)
# This is a custom metric you can present to answer "In what way are they underserved?"
frustration_score = pivot_time['new'] / (pivot_rate['new'] * 1000) # Scaled
print("\n--- Frustration Index (New Users) ---")
print(frustration_score)


# ---------------------------------------------------------
# ANALYSIS 2: DIFFERENT FUNNELS FOR DIFFERENT USERS
# Instructor Question: "Are there different funnels?"
# ---------------------------------------------------------

# We need to see the volume flow.
# Do New Users get stuck at the top more than Established users?
pivot_vol = df.pivot_table(
    index='FunnelStage', 
    columns='UserType', 
    values='Sessions', 
    aggfunc='sum'
)

# Calculate % of traffic at each stage (The Funnel Shape)
funnel_shape = pivot_vol.div(pivot_vol.sum(axis=0), axis=1)
print("\n--- Funnel Shape (% of Traffic) ---")
print(funnel_shape)


df_clean = df[
    (df['FunnelStage'] != 'Cross-Shopping') & 
    (df['UserType'] != '(not set)')
]

# Create the Funnel Shape
pivot = df_clean.pivot_table(
    index='FunnelStage', 
    columns='UserType', 
    values='Sessions', 
    aggfunc='sum'
)

# Sort and Normalize
pivot = pivot.reindex(['Top', 'Middle', 'Bottom'])
funnel_shape = pivot.div(pivot.sum(axis=0), axis=1)

print(funnel_shape.applymap(lambda x: f"{x:.1%}"))

