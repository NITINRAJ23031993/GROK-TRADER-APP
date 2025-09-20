import pandas as pd
import numpy as np
from src.models.predict import load_model, predict_proba
from src.strategies.base_strategy import StrategyBase
import torch
from collections import deque
import random

class DQN(torch.nn.Module):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.fc1 = torch.nn.Linear(state_size, 64)
        self.fc2 = torch.nn.Linear(64, 32)
        self.out = torch.nn.Linear(32, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.out(x)

class Ensemble(StrategyBase):
    def __init__(self):
        super().__init__('ensemble')
        self.model = load_model()
        self.features = ['ret_1','ret_5','atr_14','rsi_14','ema_8','ema_21','ema_55','boll_w','vol_z','macd','stoch_k','session_asia','session_london','session_ny', 'vwap', 'sentiment']
        # RL setup
        self.action_size = 3  # buy, hold, sell
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.dqn = DQN(len(self.features), self.action_size)
        self.optimizer = torch.optim.Adam(self.dqn.parameters(), lr=0.001)
        self.loss_fn = torch.nn.MSELoss()

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        X = df[self.features]
        proba_lgb = predict_proba(self.model['lgb'], X)
        proba_lstm = self.model['lstm'](torch.tensor(X.values).float().unsqueeze(1)).detach().numpy().squeeze()
        proba = (proba_lgb + proba_lstm) / 2
        signals = np.where(proba > 0.6, 1, np.where(proba < 0.4, -1, 0))
        return pd.Series(signals, index=df.index)

    def update_rl(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))
        if len(self.memory) > 32:
            batch = random.sample(self.memory, 32)
            states, actions, rewards, next_states = zip(*batch)
            states = torch.tensor(np.array(states)).float()
            next_states = torch.tensor(np.array(next_states)).float()
            actions = torch.tensor(actions).long()
            rewards = torch.tensor(rewards).float()
            q_values = self.dqn(states).gather(1, actions.unsqueeze(1)).squeeze()
            next_q = self.dqn(next_states).max(1)[0]
            target = rewards + self.gamma * next_q
            loss = self.loss_fn(q_values, target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)