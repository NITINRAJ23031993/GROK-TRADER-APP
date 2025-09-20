import os, joblib, numpy as np
from src.utils.logger import info
MODEL_PATH = 'models/model.pkl'

def load_model(path=MODEL_PATH):
    if os.path.exists('models'):
        models = [f for f in os.listdir('models') if f.startswith('model_') and f.endswith('.pkl')]
        if models:
            latest = max(models, key=lambda x: os.path.getctime(os.path.join('models', x)))
            path = os.path.join('models', latest)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return joblib.load(path)

def predict_proba(model, X_df):
    try:
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(X_df)[:, 1]
        else:
            return model.predict(X_df)
    except Exception as e:
        info(f'Predict error: {e}')
        return np.zeros(len(X_df))