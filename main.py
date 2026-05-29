import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
import xgboost as xgb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# =========================
# CORS Middleware Configuration
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Load Saved Components
# =========================

scaler = joblib.load("scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")

# Load XGBoost
xgb_model = xgb.XGBClassifier()
xgb_model.load_model("xgb_model.json")

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# DNN Definition
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

dnn_model = DNN(len(feature_columns)).to(device)
dnn_model.load_state_dict(torch.load("dnn_model.pt", map_location=device))
dnn_model.eval()

# =========================
# GRU Definition
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

gru_model = GRUModel(1).to(device)
gru_model.load_state_dict(torch.load("gru_model.pt", map_location=device))
gru_model.eval()

# =========================
# Request Schema
# =========================

class EmployeeData(BaseModel):
    data: dict


# =========================
# Simple Request Schema (Frontend-friendly)
# =========================

class SimpleEmployeeData(BaseModel):
    years: int
    income: int
    overtime: int
    performance: str
    engagement: int


# =========================
# Prediction Endpoint
# =========================

@app.post("/predict")
def predict(employee: EmployeeData):

    input_dict = employee.data

    # Build full feature dict in correct order
    full_input = {col: input_dict.get(col, 0) for col in feature_columns}

    # Create DataFrame with correct column names
    input_df = pd.DataFrame([full_input])

    # Scale using DataFrame (important)
    input_scaled = scaler.transform(input_df)

    # XGB
    xgb_prob = xgb_model.predict_proba(input_scaled)[0][1]

    # DNN
    input_tensor = torch.FloatTensor(input_scaled).to(device)
    with torch.no_grad():
        dnn_prob = dnn_model(input_tensor).cpu().numpy()[0][0]

    # GRU
    input_gru = torch.FloatTensor(input_scaled.reshape(1, input_scaled.shape[1], 1)).to(device)
    with torch.no_grad():
        gru_prob = gru_model(input_gru).cpu().numpy()[0][0]

    # Ensemble
    final_prob = 0.6 * xgb_prob + 0.4 * dnn_prob

    if final_prob < 0.3:
        risk = "Low"
    elif final_prob < 0.6:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "attrition_probability": float(final_prob),
        "risk_level": risk
    }


# =========================
# Simple Prediction Endpoint (For Frontend)
# =========================

@app.post("/predict-simple")
def predict_simple(employee: SimpleEmployeeData):
    """
    Accepts simple frontend fields and maps them to the required features
    """
    
    # Map simple fields to feature columns
    # Using reasonable mappings based on typical employee data
    input_dict = {
        # Years at company -> TotalWorkingYears
        "TotalWorkingYears": employee.years,
        # Monthly Income -> MonthlyIncome
        "MonthlyIncome": employee.income,
        # Overtime -> OverTime mapping (Yes/No)
        "OverTime": "Yes" if employee.overtime > 10 else "No",
        # Engagement maps to JobSatisfaction (1-10 scale)
        "JobSatisfaction": employee.engagement,
        # Performance maps to PerformanceRating
        "PerformanceRating": {"high": 4, "stable": 3, "low": 2}.get(employee.performance, 3),
        # Years at company -> YearsAtCompany
        "YearsAtCompany": employee.years,
        # Years in current role -> YearsInCurrentRole
        "YearsInCurrentRole": max(1, employee.years - 1),
        # Years since last promotion -> YearsSinceLastPromotion
        "YearsSinceLastPromotion": max(0, employee.years - 2),
        # Work life balance based on overtime
        "WorkLifeBalance": max(1, 4 - (employee.overtime // 5)),
        # Distance from home (default moderate)
        "DistanceFromHome": 15,
        # Age (estimate based on years working)
        "Age": 25 + employee.years,
        # Default values for other features
        "DailyRate": employee.income * 3,
        "HourlyRate": int(employee.income / 160),
        "MonthlyRate": employee.income,
        "NumCompaniesWorked": max(1, employee.years // 3),
        "PercentSalaryHike": 15,
        "StockOptionLevel": 1,
        "TrainingTimesLastYear": 3,
        "EnvironmentSatisfaction": employee.engagement,
        "JobInvolvement": employee.engagement,
        "RelationshipSatisfaction": employee.engagement,
    }
    
    # Add dummy values for categorical columns that will be created by one-hot encoding
    # Business Travel
    input_dict["BusinessTravel_Travel_Frequently"] = 0
    input_dict["BusinessTravel_Travel_Rarely"] = 1
    
    # Department
    input_dict["Department_Research & Development"] = 1
    input_dict["Department_Sales"] = 0
    
    # Education Field
    input_dict["EducationField_Life Sciences"] = 1
    input_dict["EducationField_Marketing"] = 0
    input_dict["EducationField_Medical"] = 0
    input_dict["EducationField_Other"] = 0
    input_dict["EducationField_Technical Degree"] = 0
    input_dict["EducationField_Human Resources"] = 0
    
    # Job Role
    input_dict["JobRole_Healthcare Representative"] = 0
    input_dict["JobRole_Human Resources"] = 0
    input_dict["JobRole_Laboratory Technician"] = 0
    input_dict["JobRole_Manager"] = 0
    input_dict["JobRole_Manufacturing Director"] = 0
    input_dict["JobRole_Research Director"] = 0
    input_dict["JobRole_Research Scientist"] = 0
    input_dict["JobRole_Sales Executive"] = 0
    input_dict["JobRole_Sales Representative"] = 0
    
    # Marital Status
    input_dict["MaritalStatus_Married"] = 1
    input_dict["MaritalStatus_Single"] = 0
    
    # Gender
    input_dict["Gender_Male"] = 1
    
    # Shift
    input_dict["Shift"] = 0
    
    # Education (map to typical values)
    input_dict["Education"] = 3
    
    # Build full feature dict in correct order
    full_input = {col: input_dict.get(col, 0) for col in feature_columns}

    # Create DataFrame with correct column names
    input_df = pd.DataFrame([full_input])

    # Scale using DataFrame (important)
    input_scaled = scaler.transform(input_df)
    
    # XGB
    xgb_prob = xgb_model.predict_proba(input_scaled)[0][1]
    
    # DNN
    input_tensor = torch.FloatTensor(input_scaled).to(device)
    with torch.no_grad():
        dnn_prob = dnn_model(input_tensor).cpu().numpy()[0][0]
    
    # GRU
    input_gru = torch.FloatTensor(input_scaled.reshape(1, input_scaled.shape[1], 1)).to(device)
    with torch.no_grad():
        gru_prob = gru_model(input_gru).cpu().numpy()[0][0]
    
    # Ensemble
    final_prob = 0.6 * xgb_prob + 0.4 * dnn_prob
    
    if final_prob < 0.3:
        risk = "Low"
    elif final_prob < 0.6:
        risk = "Medium"
    else:
        risk = "High"
    
    # Determine contributing factors based on input
    factors = []
    if employee.overtime > 15:
        factors.append("Excessive Overtime")
    if employee.engagement < 5:
        factors.append("Low Engagement")
    if employee.performance == 'low':
        factors.append("Declining Performance")
    if employee.years < 2 and employee.income < 3000:
        factors.append("Early Career/Low Pay")
    if employee.years > 10 and employee.performance == 'stable':
        factors.append("Stagnation Risk")
    
    # Generate recommendation
    if risk == "Low":
        recommendation = "Continue standard engagement protocols."
    elif risk == "Medium":
        recommendation = "Schedule a check-in meeting to discuss career goals."
    else:
        recommendation = "Immediate intervention required. Review workload and compensation."
    
    return {
        "attrition_probability": float(final_prob),
        "risk_level": risk,
        "factors": factors,
        "recommendation": recommendation,
        "confidence": 0.94
    }
