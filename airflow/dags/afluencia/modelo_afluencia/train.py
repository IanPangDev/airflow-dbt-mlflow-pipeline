import mlflow
import mlflow.sklearn
import pandas as pd
from .preprocessing import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def train_and_log(df: pd.DataFrame):
    experiment_name = "afluencia_forecasting_randomforest"
    
    # Crea o recupera experimento
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id
    
    df_train_lags = preprocessing(df)
    
    X = df_train_lags.drop(columns=['fecha', 'afluencia_tren_ligero'])
    y = df_train_lags['afluencia_tren_ligero']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    n_estimators = 200
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test.values, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test.values, y_pred))
    r2 = r2_score(y_test.values, y_pred)

    # Registro de ejecución y modelo
    with mlflow.start_run(
        experiment_id=experiment_id,
        run_name=f"RandomForest_{n_estimators}_trees_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    ):
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="RandomForestAfluencia"
        )