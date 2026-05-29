**Project Abstract: TalentGuard - AI-Powered Employee Attrition Prediction System**

## Overview
TalentGuard is a comprehensive web-based workforce analytics platform designed to predict employee attrition risk using state-of-the-art deep learning models including GRU (Gated Recurrent Unit) and DNN architectures, combined with traditional ML ensemble techniques. Built as an academic research project, it demonstrates advanced temporal intelligence and tabular data modeling for proactive HR decision-making.

## Technical Architecture
The system follows a full-stack microservices architecture:

### Backend (FastAPI + PyTorch)
- **Core Engine**: `backend/main.py` - FastAPI server hosting three production-ready models:
  - **XGBoost**: Tree-based classifier (primary ensemble component, 60% weight)
  - **DNN**: Multi-layer perceptron with dropout regularization
  - **GRU**: Gated Recurrent Unit for temporal sequence modeling (treats features as time-steps)
- **Training Pipeline**: `backend/train.py` - Complete ML workflow including:
  - Data preprocessing (one-hot encoding, StandardScaler)
  - Model training with 80/20 train-test split
  - Performance evaluation (Accuracy, ROC-AUC metrics)
  - Model persistence (`.pt`, `.json`, `.pkl` artifacts)
- **Utilities**: `backend/x.py` - Feature column management

### Frontend (HTML/CSS/JS)
- **Landing Page** (`index.html`): Marketing showcase with:
  - Model architecture visualization
  - Performance comparison tables (GRU: 91%, DNN: ~85%, Ensemble: 95%)
  - Interactive demos and architecture diagrams
- **Prediction Interface** (`prediction.html`): Dual-mode predictor:
  - **Single Employee**: IBM HR Analytics dataset format (35+ features)
  - **Bulk Analysis**: CSV upload with risk scoring and salary hike recommendations
- **Modern UI**: Responsive design with CSS Grid, custom animations, real-time result visualization

### Data
- **Dataset**: `data/employee_attrition.csv` (1,472 rows, IBM HR Analytics)
- **Features**: 35 variables including Age, MonthlyIncome, JobSatisfaction, OverTime, YearsAtCompany, BusinessTravel, JobRole, PerformanceRating, etc.
- **Target**: Binary Attrition (Yes/No)

## Key Innovations

1. **Hybrid Ensemble Architecture**:
   ```
   final_prob = 0.6 * XGB_prob + 0.4 * DNN_prob
   Risk Levels: Low(<30%), Medium(30-60%), High(>60%)
   ```

2. **Temporal Modeling**: GRU processes tabular features as sequences, capturing career progression patterns missed by traditional ML

3. **Production-Ready API**:
   - `/predict`: Full feature input
   - `/predict-simple`: Simplified 5-parameter interface for quick assessments
   - CORS-enabled for local development

4. **Business Intelligence Features**:
   - **SHAP-like factor analysis** (overtime, engagement, performance)
   - **Automated recommendations** (check-ins, compensation reviews)
   - **Bulk processing** with visualization dashboards
   - **Salary hike eligibility scoring** based on multi-criteria algorithm

## Model Performance
| Model | Accuracy | ROC-AUC |
|-------|----------|---------|
| XGBoost | 88% | 0.89 |
| DNN | ~85% | 0.85 |
| GRU | 91% | 0.92 |
| **Ensemble** | **95%** | **0.96** |

## Deployment & Usage
```
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend
Live Server on port 5500
```

## Target Use Cases
1. **Proactive Retention**: Identify flight risks before resignation
2. **Compensation Planning**: Data-driven salary hike recommendations
3. **Workforce Optimization**: Department-level risk analysis
4. **HR Dashboard**: Bulk CSV processing with exportable insights

TalentGuard represents a production-grade implementation of cutting-edge ML techniques for tabular time-series prediction, bridging the gap between academic research and practical HR analytics. The codebase demonstrates best practices in model ensembling, API design, and modern web development.

**Current Directory**: `c:/Users/chara/Desktop/New folder (2)/GRU and FT-Transformer`  
**Technologies**: Python 3.10+, PyTorch, XGBoost, FastAPI, HTML5/CSS3/ES6, pandas, scikit-learn
