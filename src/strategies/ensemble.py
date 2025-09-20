from src.strategies.base_strategy import StrategyBase
from src.strategies.trend_following import TrendFollowing
from src.strategies.mean_reversion import MeanReversion
import pandas as pd
import numpy as np
from src.models.predict import load_model, MODEL_PATH
import torch
from torch import nn, optim
import os

class RLAgent(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 3)  # buy, hold, sell

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        return torch.softmax(self.fc2(x), dim=-1)

class Ensemble(StrategyBase):
    def __init__(self, weights={'ml': 0.5, 'trend': 0.3, 'reversion': 0.2}):
        super().__init__('ensemble')
        self.trend = TrendFollowing()
        self.reversion = MeanReversion()
        self.weights = weights
        self.model = load_model()
        self.features = ['ret_1','ret_5','atr_14','rsi_14','ema_8','ema_21','ema_55','boll_w','vol_z','macd','stoch_k','session_asia','session_london','session_ny']
        self.rl_agent = RLAgent(len(self.features))
        self.optimizer = optim.Adam(self.rl_agent.parameters(), lr=0.001)
        self.gamma = 0.99
        self.load_rl_state()

    def generate_signals(self, df):
        trend_sig = self.trend.generate_signals(df)
        rev_sig = self.reversion.generate_signals(df)
        X = df[self.features].fillna(0)
        ml_proba = self.model.predict_proba(X.values)[:, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(X.values)
        ml_sig = pd.Series(np.where(ml_proba > 0.7, 1, np.where(ml_proba < 0.3, -1, 0)), index=df.index)
        
        state = torch.tensor(X.iloc[-1].values, dtype=torch.float32).unsqueeze(0)
        action_probs = self.rl_agent(state)[0]
        rl_adjust = (torch.argmax(action_probs).item() - 1) * 0.2  # -0.2 to 0.2 adjust
        
        ensemble_sig = (self.weights['ml'] * ml_sig + self.weights['trend'] * trend_sig + self.weights['reversion'] * rev_sig) + rl_adjust
        sig = np.where(ensemble_sig > 0.3, 1, np.where(ensemble_sig < -0.3, -1, 0))
        return pd.Series(sig, index=df.index).fillna(0)

    def update_rl(self, state, action, reward, next_state):
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        next_state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
        q_values = self.rl_agent(state)
        next_q = self.rl_agent(next_state).max(1)[0].item()
        target = reward + self.gamma * next_q
        action_idx = action + 1  # shift to 0-2
        loss = nn.MSELoss()(q_values[0, action_idx], torch.tensor(target, dtype=torch.float32))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.save_rl_state()

    def save_rl_state(self):
        torch.save(self.rl_agent.state_dict(), 'models/rl_agent.pth')

    def load_rl_state(self):
        if os.path.exists('models/rl_agent.pth'):
            self.rl_agent.load_state_dict(torch.load('models/rl_agent.pth'))