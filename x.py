import joblib
features = joblib.load("feature_columns.pkl")
print(len(features))
print(features)