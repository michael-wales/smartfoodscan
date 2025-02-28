from fastapi import FastAPI
import pickle

app = FastAPI()

@app.get('/')
def root():
    return {'greeting': "hello"}


@app.get('/predict')
def predict(data):
    with open('../models/best_model.pkl', 'rb') as file:
        model = pickle.load(file)

    prediction = model.predict(data)

    return prediction
