import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np

def crear_ventanas(df:pd.DataFrame, target_col:str, n_lags:int) -> pd.DataFrame:
    for lag in range(1, n_lags + 1):
        df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
    df = df.dropna()
    return df

def preprocessing(df: pd.DataFrame):
    codificador_dia_nombre = LabelEncoder()
    codificador_dia_nombre.fit(df.dia_nombre)
    
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    df_train = df[['fecha', 'afluencia_tren_ligero', 'dia_nombre', 'es_festivo']].copy()
    df_train['dia_nombre'] = codificador_dia_nombre.fit_transform(df.dia_nombre)
    df_train['es_festivo'] = df_train['es_festivo'].astype(int)
    df_train['year'] = df_train['fecha'].dt.year
    df_train['afluencia_tren_ligero'] = df_train['afluencia_tren_ligero'].astype(int)
    df_train['sin_dayofyear'] = np.sin(2 * np.pi * df['fecha'].dt.dayofyear / 365)
    df_train['cos_dayofyear'] = np.cos(2 * np.pi * df['fecha'].dt.dayofyear / 365)
    
    ventana = 5
    
    return crear_ventanas(df_train.copy(), 'afluencia_tren_ligero', n_lags=ventana)