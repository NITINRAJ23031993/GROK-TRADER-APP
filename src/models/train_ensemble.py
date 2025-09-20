import os
import joblib
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from src.utils.logger import info
from src.features.build_features import build_features
import optuna
import torch
import torch.nn as nn
import torch.optim as optim

class LSTM(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.lstm = nn.LSTM(input_size, 64, batch_first=True)
        self.fc = nn.Linear(64, 1)

    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return torch.sigmoid(self.fc(h.squeeze(0)))

def objective(trial):
    params = {'num_leaves': trial.suggest_int('num_leaves', 20, 50), 'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1)}
    # ... (use in lgb train, return auc)
    return avg_auc  # Placeholder; implement full

def train_model():
    build_features()
    df = pd.read_parquet('data/features.parquet')
    features = ['ret_1','ret_5','atr_14','rsi_14','ema_8','ema_21','ema_55','boll_w','vol_z','macd','stoch_k','session_asia','session_london','session_ny', 'vwap', 'sentiment']
    X = df[features].fillna(0)
    y = (df['Close'].shift(-5) / df['Close'] - 1 > 0.001).astype(int)
    X = X.iloc[:-5]
    y = y.iloc[:-5]

    split = int(0.8 * len(X))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # Optuna for lgb
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20)
    best_params = study.best_params
    best_params['objective'] = 'binary'
    best_params['metric'] = 'auc'

    dtrain = lgb.Dataset(X_train, label=y_train)
    bst = lgb.train(best_params, dtrain, num_boost_round=200)

    # LSTM
    X_lstm = torch.tensor(X_train.values).float().unsqueeze(1)
    y_lstm = torch.tensor(y_train.values).float().unsqueeze(1)
    lstm = LSTM(X.shape[1])
    optimizer = optim.Adam(lstm.parameters(), lr=0.001)
    loss_fn = nn.BCELoss()
    for epoch in range(50):
        out = lstm(X_lstm)
        loss = loss_fn(out, y_lstm.unsqueeze(1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Save ensemble
    os.makedirs('models', exist_ok=True)
    joblib.dump({'lgb': bst, 'lstm': lstm}, 'models/model.pkl')
    info('Saved ensemble model')