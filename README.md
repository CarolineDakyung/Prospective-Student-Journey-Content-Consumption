# Prospective Student Journey Analytics  
UCLA Anderson MSBA Website Funnel Analysis

---

## Project Overview

This project analyzes how prospective MSBA students interact with UCLA Anderson’s website across different stages of the admissions funnel. Using session-level web analytics data, the analysis examines how engagement patterns differ by funnel stage and user type (new vs. established users).

The goal is to identify where users experience friction in their decision journey and provide data-driven recommendations to improve content and navigation.

---

## Data Description

- Source: Internal Google Analytics data collected by UCLA Anderson (not publicly available)
- Granularity: Session-level data
- Sample Size: Approximately 100,000 sessions
- User Types:
  - New users
  - Established users
- Key Variables:
  - Page path
  - Traffic source
  - Sessions
  - Engagement rate
  - Engagement time
  - Key events

Due to data privacy and institutional policies, the raw dataset is not included in this repository.

---

## Methodology

### 1. Funnel Construction

Website pages were classified into funnel stages using URL patterns:

| Stage  | Description                                  |
|--------|----------------------------------------------|
| Top    | Program discovery and general information    |
| Middle | Career, finance, and admissions evaluation   |
| Bottom | Application-related pages                    |

A refined funnel classification introduced cross-shopping and category-level segmentation.

---

### 2. Data Processing

- Removed duplicated engagement metrics
- Filtered ambiguous user types (e.g., "not set")
- Capped extreme engagement time outliers (99th percentile)
- Created an active dataset for regression analysis

---

### 3. Feature Engineering

- Custom functions to:
  - Assign funnel stages
  - Categorize page intent
  - Map refined funnel paths
- Created pivot tables for engagement and volume analysis
- Developed a "Frustration Index" combining effort and success metrics

---

### 4. Statistical Modeling

OLS regression models were estimated using statsmodels:

1. Engagement Time Model
   
   ```python
   EngTime ~ FunnelStage + UserType

2. Engagement Rate Model
   
   ```python
   EngRate ~ FunnelStage * UserType

Additional models were estimated on capped and filtered datasets.

---

## Key Findings

- New users spend more time per session than established users.
- Engagement declines significantly in the middle funnel.
- Middle-funnel users exert high effort with lower engagement outcomes.
- Funnel structure is similar across user types.
- The Frustration Index highlights underserved new-user segments.

These results suggest structural friction in evaluative-stage content.

---

## Recommendations

- Improve clarity and depth of middle-funnel content
- Enhance website navigation and information hierarchy
- Apply A/B testing for funnel optimization
- Standardize engagement metrics across stages

---

## Pipeline Process

This project is implemented in a single script:
`analysis.py` – End-to-end data processing and modeling pipeline

Workflow:

1. Load raw Google Analytics data (Excel export)

2. Preprocess and clean engagement metrics

3. Construct funnel stages based on URL patterns

4. Engineer behavioral features

5. Fit regression models

6. Generate summary tables and figures

All steps are executed sequentially in a single script.

---

## How to Run

1. Install dependencies:
   ```bash
   pip install pandas numpy statsmodels

2. Place the Excel dataset in the project directory.
   
   Note: The dataset is derived from internal Google Analytics tracking data and is not publicly available.

3. Run:
   
   python analysis.py



