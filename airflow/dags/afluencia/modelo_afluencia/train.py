import mlflow
import mlflow.sklearn
import pandas as pd
from .preprocessing import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def train_and_log(df: pd.DataFrame):
    # Configura MLflow
    mlflow.set_tracking_uri("http://mlflow:8080")
    mlflow.set_experiment("afluencia_forecasting_randomforest")
    
    df_train_lags = preprocessing(df)
    
    X = df_train_lags.drop(columns=['fecha', 'afluencia_tren_ligero'])
    y = df_train_lags['afluencia_tren_ligero']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test.values, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test.values, y_pred))
    r2 = r2_score(y_test.values, y_pred)

    # Log en MLflow
    with mlflow.start_run():
        mlflow.log_param("n_estimators", 200)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(model, "model")