from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Загрузка моделей для каждой страны (предполагается, что модели загружены так же)
try:
    model_france_bundle = joblib.load("models/model_france.pkl")
    model_spain_bundle = joblib.load("models/model_spain.pkl")
    model_germany_bundle = joblib.load("models/model_germany.pkl")
except Exception as e:
    raise RuntimeError(f"Ошибка загрузки моделей: {e}")

model_france = model_france_bundle["model"]
threshold_france = model_france_bundle["threshold"]

model_spain = model_spain_bundle["model"]
threshold_spain = model_spain_bundle["threshold"]

model_germany = model_germany_bundle["model"]
threshold_germany = model_germany_bundle["threshold"]


def validate_and_preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    if 'Gender_Male' not in df.columns and 'Gender' in df.columns:
        df['Gender_Male'] = df['Gender'].apply(lambda x: 1 if str(x).strip().lower() == 'male' else 0).astype(int)
    elif 'Gender_Male' in df.columns:
        df['Gender_Male'] = pd.to_numeric(df['Gender_Male'], errors='coerce').fillna(0).astype(int)

    model_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
                      'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Gender_Male']

    missing_features = [col for col in model_features if col not in df.columns]
    if missing_features:
        raise ValueError(f"Отсутствуют обязательные признаки: {missing_features}")

    X = df[model_features].copy()
    return X


class ClientData(BaseModel):
    CustomerId: int
    Geography: str
    CreditScore: float
    Age: float
    Tenure: float
    Balance: float
    NumOfProducts: float
    HasCrCard: int
    IsActiveMember: int
    EstimatedSalary: float
    Gender: str = None
    Gender_Male: int = None


# Новая модель для пакетной обработки:
class ClientsData(BaseModel):
    clients: List[ClientData]


@app.post("/predict_batch")
def predict_batch(data: ClientsData):
    # Преобразуем входные данные в DataFrame
    df = pd.DataFrame([client.dict() for client in data.clients])

    # Группируем по Geography, чтобы для каждой группы использовать нужную модель
    results = []
    for geography, group in df.groupby('Geography'):
        try:
            X = validate_and_preprocess_input(group)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if geography == "France":
            pipeline = model_france
            threshold = threshold_france
        elif geography == "Spain":
            pipeline = model_spain
            threshold = threshold_spain
        elif geography == "Germany":
            pipeline = model_germany
            threshold = threshold_germany
        else:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый Geography: {geography}")

        try:
            probs = pipeline.predict_proba(X)[:, 1]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {e}")

        preds = (probs >= threshold).astype(int)
        group_result = pd.DataFrame({
            "CustomerId": group["CustomerId"],
            "Geography": geography,
            "prediction": preds,
            "churn_probability": [round(prob, 4) for prob in probs]
        })
        results.append(group_result)

    if results:
        final_results = pd.concat(results, ignore_index=True)
        return final_results.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="Нет данных для предсказания")


@app.get("/feature_importances")
def get_feature_importances(country: str = "France"):
    if country == "France":
        model_bundle = model_france_bundle
    elif country == "Spain":
        model_bundle = model_spain_bundle
    elif country == "Germany":
        model_bundle = model_germany_bundle
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемая страна")

    model = model_bundle["model"]
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "named_steps"):
        for step in model.named_steps.values():
            if hasattr(step, "feature_importances_"):
                importances = step.feature_importances_
                break
        else:
            raise HTTPException(status_code=500, detail="Модель не поддерживает feature_importances")
    else:
        raise HTTPException(status_code=500, detail="Модель не поддерживает feature_importances")

    features = ['Кредитный рейтинг', 'Возраст', 'Стаж (лет)', 'Баланс',
                'Кол-во продуктов', 'Наличие кредитной карты', 'Активность', 'Оценочная зарплата', 'Пол']
    fi = dict(zip(features, importances))

    # Приводим каждое значение к float
    fi = {k: float(v) for k, v in fi.items()}
    return fi

