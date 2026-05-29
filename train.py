import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

# =========================
# 1. LOAD DATA
# =========================

df = pd.read_csv("../data/employee_attrition.csv")

df["Attrition"] = df["Attrition"].map({"Yes":1, "No":0})

df = df.drop(["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"], axis=1)

df = pd.get_dummies(df, drop_first=True)

X = df.drop("Attrition", axis=1)
y = df["Attrition"]

# Save feature names
joblib.dump(X.columns.tolist(), "feature_columns.pkl")

# =========================
# 2. TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 3. SCALING
# =========================

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

joblib.dump(scaler, "scaler.pkl")

# =========================
# 4. XGBOOST
# =========================

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05
)

xgb_model.fit(X_train, y_train)

xgb_pred = xgb_model.predict(X_test)

print("\nXGBOOST RESULTS")
print("Accuracy:", accuracy_score(y_test, xgb_pred))
print("ROC-AUC:", roc_auc_score(y_test, xgb_pred))

xgb_model.save_model("xgb_model.json")

# =========================
# 5. DNN MODEL
# =========================

class DNN(nn.Module):
    def __init__(self, input_dim):
        super(DNN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

X_train_tensor = torch.FloatTensor(X_train).to(device)
y_train_tensor = torch.FloatTensor(y_train.values).unsqueeze(1).to(device)

X_test_tensor = torch.FloatTensor(X_test).to(device)

dnn_model = DNN(X_train.shape[1]).to(device)
criterion = nn.BCELoss()
optimizer = optim.Adam(dnn_model.parameters(), lr=0.001)

# Training loop
for epoch in range(50):
    dnn_model.train()
    optimizer.zero_grad()
    outputs = dnn_model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()

# Evaluation
dnn_model.eval()
with torch.no_grad():
    dnn_pred = dnn_model(X_test_tensor)
    dnn_pred_class = (dnn_pred.cpu().numpy() > 0.5).astype(int)

print("\nDNN RESULTS")
print("Accuracy:", accuracy_score(y_test, dnn_pred_class))
print("ROC-AUC:", roc_auc_score(y_test, dnn_pred_class))

torch.save(dnn_model.state_dict(), "dnn_model.pt")

# =========================
# 6. GRU MODEL
# =========================

class GRUModel(nn.Module):
    def __init__(self, input_dim):
        super(GRUModel, self).__init__()
        self.gru = nn.GRU(input_dim, 64, batch_first=True)
        self.fc = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.gru(x)
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

# Reshape for GRU (treat features as time steps)
X_train_gru = torch.FloatTensor(X_train.reshape(-1, X_train.shape[1], 1)).to(device)
X_test_gru = torch.FloatTensor(X_test.reshape(-1, X_test.shape[1], 1)).to(device)

gru_model = GRUModel(1).to(device)
optimizer = optim.Adam(gru_model.parameters(), lr=0.001)

for epoch in range(50):
    gru_model.train()
    optimizer.zero_grad()
    outputs = gru_model(X_train_gru)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()

gru_model.eval()
with torch.no_grad():
    gru_pred = gru_model(X_test_gru)
    gru_pred_class = (gru_pred.cpu().numpy() > 0.5).astype(int)

print("\nGRU RESULTS")
print("Accuracy:", accuracy_score(y_test, gru_pred_class))
print("ROC-AUC:", roc_auc_score(y_test, gru_pred_class))

torch.save(gru_model.state_dict(), "gru_model.pt")

# =========================
# 7. ENSEMBLE
# =========================

ensemble = (
    0.4 * xgb_pred +
    0.3 * dnn_pred_class.flatten() +
    0.3 * gru_pred_class.flatten()
)

ensemble = (ensemble > 0.5).astype(int)

print("\nENSEMBLE RESULTS")
print("Accuracy:", accuracy_score(y_test, ensemble))
print("ROC-AUC:", roc_auc_score(y_test, ensemble))

print("\nTraining Complete.")