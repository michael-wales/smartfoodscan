from fastapi import FastAPI
import joblib
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Load the model once at startup to avoid reloading on every request
with open('../models/best_model.joblib', 'rb') as file:
    model = joblib.load(file)

# Define the expected JSON format using Pydantic
class NutrimentInput(BaseModel):
    energy-kcal_100g: float = 0.0
    saturated-fat_100g: float = 0.0
    trans-fat_100g: float = 0.0
    cholesterol_100g: float = 0.0
    sugars_100g: float = 0.0
    fiber_100g: float = 0.0
    proteins_100g: float = 0.0
    sodium_100g: float = 0.0
    calcium_100g: float = 0.0
    iron_100g: float = 0.0
    carbohydrates_100g: float = 0.0
    fat_100g: float = 0.0

@app.get('/')
def root():
    return {'greeting': "hello"}


@app.get('/predict')
def predict(data):
    with open('../models/best_model.pkl', 'rb') as file:
        model = joblib.load(file)

    prediction = model.predict(data)

    return prediction


@app.post('/predict')
def predict(nutriments: NutrimentInput):
    # Convert input JSON into a Pandas DataFrame
    data = {
        'energy-kcal_100g': [nutriments.energy-kcal_100g],
        'saturated-fat_100g': [nutriments.saturated-fat_100g],
        'trans-fat_100g': [nutriments.trans-fat_100g],
        'cholesterol_100g': [nutriments.cholesterol_100g],
        'sugars_100g': [nutriments.sugars_100g],
        'fiber_100g': [nutriments.fiber_100g],
        'proteins_100g': [nutriments.proteins_100g],
        'sodium_100g': [nutriments.sodium_100g],
        'calcium_100g': [nutriments.calcium_100g],
        'iron_100g': [nutriments.iron_100g],
        'other_carbohydrates_100g': [
            nutriments.carbohydrates_100g - nutriments.sugars_100g - nutriments.fiber_100g
        ],
        'other_fat_100g': [
            nutriments.fat_100g - nutriments.saturated-fat_100g - nutriments.trans-fat_100g
        ],
    }

    input_data = pd.DataFrame.from_dict(data)

    # Make a prediction
    prediction = model.predict(input_data)

    # Return as JSON
    return {"prediction": prediction.tolist()}
