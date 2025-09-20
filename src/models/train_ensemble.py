import os, joblib
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from src.utils.logger import info
from src.features.build_features import build_features

def train_model():
    build_features()
    df = pd.read_parquet('data/features.parquet')
    features = ['ret_1','ret_5','atr_14','rsi_14','ema_8','ema_21','ema_55','boll_w','vol_z','macd','stoch_k','session_asia','session_london','session_ny']
    X = df[features].fillna(0)
    y = (df['Close'].shift(-5) / df['Close'] - 1 > 0.001).astype(int)
    X = X.iloc[:-5]
    y = y.iloc[:-5]

    split = int(0.8 * len(X))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    tscv = TimeSeriesSplit(n_splits=5)
    params_grid = {'num_leaves': [31, 50], 'learning_rate': [0.05, 0.1]}
    best_auc = 0
    best_params = None
    for leaves in params_grid['num_leaves']:
        for lr in params_grid['learning_rate']:
            params = {'objective':'binary', 'metric':'auc', 'verbosity':-1, 'num_leaves':leaves, 'learning_rate':lr}
            auc_scores = []
            for train_idx, val_idx in tscv.split(X_train):
                dtrain = lgb.Dataset(X_train.iloc[train_idx], label=y_train.iloc[train_idx])
                dval = lgb.Dataset(X_train.iloc[val_idx], label=y_train.iloc[val_idx])
                bst = lgb.train(params, dtrain, num_boost_round=200, valid_sets=[dval])
                auc_scores.append(bst.best_score['valid_0']['auc'])
            avg_auc = np.mean(auc_scores)
            if avg_auc > best_auc:
                best_auc = avg_auc
                best_params = params

    dtrain = lgb.Dataset(X_train, label=y_train)
    bst = lgb.train(best_params, dtrain, num_boost_round=200)
    dtest = lgb.Dataset(X_test, label=y_test)
    test_auc = bst.eval(dtest, name='test')[0][2]
    info(f'CV AUC: {best_auc:.3f}, Test AUC: {test_auc:.3f}')

    os.makedirs('models', exist_ok=True)
    joblib.dump(bst, 'models/model.pkl')
    info('Saved model')

if __name__ == '__main__':
    train_model()