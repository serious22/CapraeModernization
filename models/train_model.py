import pandas as pd
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np



# --- Configuration ---
DATA_DIR = 'data'
MODELS_DIR = 'models'
ENRICHED_LEADS_FILE = 'enriched_leads.json'

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# --- 1. Load Data ---
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure the data files are in the '{DATA_DIR}' directory.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Check file format.")
        return []

print(f"Loading data from {os.path.join(DATA_DIR, ENRICHED_LEADS_FILE)}...")
enriched_leads = load_data(os.path.join(DATA_DIR, ENRICHED_LEADS_FILE))
if not enriched_leads:
    print("No enriched leads data loaded. Exiting training script.")
    exit()

df = pd.DataFrame(enriched_leads)
print(f"Loaded {len(df)} enriched leads.")

# --- 2. Feature Engineering and Target Creation ---
# Define a synthetic 'true_rank' based on features that indicate a "good" lead.
# This is crucial as we don't have explicit rank labels in your data.
# You would replace this with your actual target variable if you had labeled data.

# Convert relevant columns to numeric, coercing errors will turn non-numeric to NaN
df['Employees Count'] = pd.to_numeric(df['Employees Count'], errors='coerce')
# Remove '$' and ',' from Revenue and convert to numeric (millions)
df['Revenue_Numeric'] = df['Revenue'].replace({r'\$': '', r',': ''}, regex=True).astype(float) / 1_000_000
df['Hiring Activity'] = pd.to_numeric(df['Hiring Activity'], errors='coerce')
df['Recent Employee Growth %'] = pd.to_numeric(df['Recent Employee Growth %'], errors='coerce')

# Create a binary feature for funding presence
df['Is_Funded'] = df['Recent Funding / Investment'].apply(
    lambda x: 1 if pd.notna(x) and x not in ["None reported", "N/A", "", "none reported", "n/a"] else 0
)

# Fill NaNs for numerical features that will contribute to the rank
# Using mean for simplicity, consider more sophisticated imputation if needed.
df['Employees Count'].fillna(df['Employees Count'].mean(), inplace=True)
df['Revenue_Numeric'].fillna(df['Revenue_Numeric'].mean(), inplace=True)
df['Hiring Activity'].fillna(0, inplace=True) # Assume 0 if unknown
df['Recent Employee Growth %'].fillna(0, inplace=True) # Assume 0 if unknown

# Synthetic target variable (example formula - adjust weights as desired)
# The idea is to create a score from 0-100 that a "good" lead would have.
df['true_rank'] = (
    (df['Hiring Activity'] * 5) +                       # High hiring is good
    (df['Recent Employee Growth %'] * 3) +             # Good growth is good
    (df['Revenue_Numeric'] * 0.5) +                    # Higher revenue is good (scaled)
    (df['Is_Funded'] * 20)                             # Being funded is a strong positive
)

# Clip the synthetic rank to be between 0 and 100 for consistency
df['true_rank'] = df['true_rank'].clip(0, 100).astype(int)
print(f"Generated synthetic 'true_rank' for {len(df)} leads.")
print(f"True rank distribution (min, max, mean): {df['true_rank'].min()}, {df['true_rank'].max()}, {df['true_rank'].mean():.2f}")


# --- 3. Feature Selection and Preprocessing Pipeline ---
numerical_features = [
    'Employees Count',
    'Revenue_Numeric',
    'Hiring Activity',
    'Recent Employee Growth %',
    'Is_Funded'
]
categorical_features = [
    'Industry',
    'Product/Service Category',
    'Business Type (B2B, B2B2C)'
]

# Create preprocessor for numerical and categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='drop' # Drop columns not specified
)

# Prepare data for model training
X = df[numerical_features + categorical_features]
y = df['true_rank']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Data split: {len(X_train)} training, {len(X_test)} testing.")

# --- 4. Model Training (Scikit-learn RandomForestRegressor) ---
print("Training RandomForestRegressor model...")
model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))])

model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print(f"Model training complete. R-squared on test set: {score:.2f}")

# --- 5. Save the Model and Preprocessors ---
# The entire pipeline (preprocessor + regressor) can be saved
joblib.dump(model, os.path.join(MODELS_DIR, 'ranking_model.pkl'))
print(f"Trained model saved to {os.path.join(MODELS_DIR, 'ranking_model.pkl')}")
