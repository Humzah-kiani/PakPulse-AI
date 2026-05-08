# 🔍 Prediction Explainability with SHAP and LIME

## Overview

The **Prediction Explainability Dashboard** provides interpretable insights into your disease case predictions using two complementary techniques:

- **SHAP (SHapley Additive exPlanations)** - Game theory-based approach
- **LIME (Local Interpretable Model-agnostic Explanations)** - Local linear model approach

This ensures your predictions are not just accurate, but also understandable and trustworthy.

---

## Quick Start

### Access the Dashboard

1. Open the PakPulse AI application
2. Navigate to **"Prediction Explainability"** from the sidebar
3. Select a **District** and **Disease**
4. Explore visualizations and explanations

### Key Sections

- **SHAP Analysis Tab** - Feature importance using Shapley values
- **LIME Analysis Tab** - Local interpretability using perturbation
- **Feature Details Tab** - Individual feature values and categories

---

## Understanding SHAP Explanations

### What is SHAP?

SHAP (SHapley Additive exPlanations) uses game theory to calculate each feature's contribution to a prediction. Each feature is assigned a "contribution value" (SHAP value) that indicates how much it pushes the prediction up or down.

### Key Features

**Game Theory Foundation**
- Based on Shapley values from cooperative game theory
- Fair and theoretically sound approach
- Provides both local and global interpretations

**Visual Indicators**
- 🟢 **Green bars** = Features that increase predicted cases
- 🔴 **Red bars** = Features that decrease predicted cases
- **Bar length** = Magnitude of impact

### Example Interpretation

```
Feature: lag_1 (Previous week cases)
SHAP Value: +5.2

"This feature increases the prediction by 5.2 cases because
the previous week had high cases, indicating an ongoing trend"
```

### Advantages

✅ Theoretically sound (game theory-based)
✅ Consistent across all predictions
✅ Works with any model type
✅ Provides global and local explanations
✅ Single value per feature per prediction

---

## Understanding LIME Explanations

### What is LIME?

LIME (Local Interpretable Model-agnostic Explanations) explains individual predictions by fitting a simple local linear model around the prediction point. It perturbs the input data and learns what local patterns matter most.

### Key Features

**Local Focus**
- Explains how features locally affect this specific prediction
- Doesn't require understanding global model behavior
- Model-agnostic (works with any black-box model)

**Perturbation-Based**
- Slightly changes feature values
- Observes changes in predictions
- Learns local linear approximation

### Example Interpretation

```
Feature: temperature (Local range: 25-30°C)
Contribution: +3.8

"In the local neighborhood around 27°C, temperature positively
affects case predictions because higher temperatures correlate
with disease spread"
```

### Advantages

✅ Model-agnostic (works with any model)
✅ Intuitive local explanations
✅ Computationally efficient
✅ Easy to understand linear model
✅ Good for identifying local patterns

---

## Feature Categories Explained

### 1. Temporal Features
**What they are:** Time-based patterns

- `lag_1, lag_2, lag_3` - Previous week's, 2-week's, 3-week's cases
- `cases_roll_mean_N` - Rolling average of cases (3, 7, 14 days)
- `cases_roll_std_N` - Rolling standard deviation
- `month` - Month of year (seasonality)

**Why they matter:** Disease patterns often repeat based on time patterns and seasonality

### 2. Environmental Features
**What they are:** Weather and environmental conditions

- `temperature` - Average temperature
- `humidity` - Air humidity percentage
- `rainfall` - Precipitation levels

**Why they matter:** Environmental conditions significantly affect disease transmission rates

### 3. Demographic Features
**What they are:** Population and infrastructure metrics

- `population_density` - People per square kilometer
- `sanitation_index` - Infrastructure and sanitation quality

**Why they matter:** Disease spread depends on population density and sanitation conditions

### 4. Encoded Features
**What they are:** Categorical variables converted to numbers

- `district_enc` - Numerical encoding of district
- `disease_enc` - Numerical encoding of disease

**Why they matter:** Different districts and diseases have different transmission patterns

---

## Interpreting Predictions

### Prediction Components

Each prediction consists of:

1. **Base Value** - Model's baseline prediction (background)
2. **Feature Contributions** - How each feature adds/subtracts
3. **Final Prediction** - Sum of base + all contributions

### Calculation
```
Prediction = Base Value + SHAP(feature_1) + SHAP(feature_2) + ... + SHAP(feature_n)
             20 cases  +  (+5.2)        +  (-2.1)        +       (+3.4)         = 26.5 cases
```

### Risk Levels

- 🟢 **Low Risk** - Predicted cases ≤ Current × 1.1
- 🟡 **Medium Risk** - Predicted cases > Current × 1.1 AND ≤ Current × 1.5
- 🔴 **High Risk** - Predicted cases > Current × 1.5

---

## Best Practices

### When to Use SHAP

✅ Need theoretically-sound explanations
✅ Want consistent, fair feature importance
✅ Analyzing global model behavior
✅ Regulatory/compliance requirements
✅ Compare predictions across different inputs

### When to Use LIME

✅ Need fast, local explanations
✅ Explaining specific individual cases
✅ Model-agnostic interpretation needed
✅ Simpler, more intuitive explanations
✅ Resource-constrained environments

### Combined Approach

**Best Practice:** Use BOTH for comprehensive understanding

1. **SHAP** - Understand overall patterns and consistency
2. **LIME** - Understand this specific prediction's context
3. **Feature Details** - Verify individual feature values

---

## Technical Details

### Models Used

- **Regression Model:** LightGBM (predicts case counts)
- **Classification Model:** LightGBM (predicts outbreak status)
- **Scaler:** MinMax normalization

### Features Used (19 total)

```
Temporal (7):       lag_1, lag_2, lag_3, 
                    cases_roll_mean_3/7/14, cases_roll_std_3/7/14

Environmental (3):  temperature, humidity, rainfall

Demographic (2):    population_density, sanitation_index

Encoded (5):        district_enc, disease_enc, month, season_enc, cases

Control (1):        cases (current)
```

### Data Processing

1. **Feature Engineering** - Lag features, rolling statistics
2. **Encoding** - Categorical variables converted to numeric
3. **Scaling** - MinMax normalization (0-1 range)
4. **Prediction** - LightGBM model evaluates
5. **Explanation** - SHAP/LIME values calculated

---

## Common Questions

### Q: Why do SHAP and LIME values sometimes differ?
**A:** SHAP measures global feature importance while LIME focuses on local patterns. They often complement each other. SHAP is theoretically sound, LIME is computationally faster.

### Q: Which should I trust more?
**A:** SHAP is more theoretically grounded (game theory). However, both provide valid insights. Best practice is to use both together.

### Q: Can I use this to improve predictions?
**A:** Yes! The explanations show which features most impact predictions. If feature contributions seem wrong, it indicates potential data quality issues or model problems.

### Q: What if a feature has very small contributions?
**A:** Small contributions don't mean the feature isn't important. It might have low variance in your data. Check raw feature values in the Feature Details tab.

### Q: How do I interpret contradictory SHAP/LIME values?
**A:** This is expected. SHAP shows global contribution, LIME shows local. A feature might be globally negative but locally positive. Investigate the specific context.

---

## Troubleshooting

### Issue: "Models not available"
**Solution:** Ensure trained models exist in `models/` directory. Run training pipeline first.

### Issue: Features not scaled correctly
**Solution:** Clear cache and reload. Check that scaler file exists at `models/feature_minmax_scaler.joblib`.

### Issue: SHAP/LIME visualization empty
**Solution:** Check that data has sufficient records. Some visualizations need minimum data points.

### Issue: Slow visualization generation
**Solution:** This is normal for SHAP on large datasets. LIME is typically faster for individual explanations.

---

## Advanced Usage

### Using SHAP/LIME Programmatically

```python
from predict import load_artifacts, prepare_features
import shap

# Load models
scaler, reg_model, clf_model = load_artifacts()

# Prepare data
X, features = prepare_features(your_data, scaler)

# Generate SHAP explanations
explainer = shap.TreeExplainer(reg_model)
shap_values = explainer.shap_values(X)

# Plot
shap.summary_plot(shap_values, X)
```

### Batch Explanations

```python
for district in all_districts:
    for disease in all_diseases:
        data = get_data(district, disease)
        X, features = prepare_features(data, scaler)
        pred = reg_model.predict(X)
        explain(pred, X, features)
```

---

## References

- **SHAP Paper:** Lundberg & Lee (2017) - "A Unified Approach to Interpreting Model Predictions"
- **LIME Paper:** Ribeiro et al. (2016) - "Why Should I Trust You?"
- **SHAP Package:** [shap.readthedocs.io](https://shap.readthedocs.io/)
- **LIME Package:** [github.com/marcotcr/lime](https://github.com/marcotcr/lime)

---

## Support

For issues or questions about prediction explainability:

1. Check troubleshooting section above
2. Review feature categories to verify inputs
3. Compare predictions across similar cases
4. Check model training logs for issues
5. Verify data quality and completeness

---

**Last Updated:** March 30, 2026
**Version:** 1.0
**Status:** ✅ Production Ready
