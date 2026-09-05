import joblib 
import numpy as np
from src.data_logger import accumulating_new_data
import pandas as pd

def predict(features):
    '''
    predicting the iris species based on the measurments and add the data to the database 
        args:
            features : a dictionary of features of the iris flower
        output:
            prediction : predicted iris species given by the model
            prediction_id : the Id of db line of the data related to the input measures its predicted specie
            
    '''
    pipline=joblib.load('piplines/pipline.pkl')
    features_df = pd.DataFrame([features])
    prediction=pipline.predict(features_df)[0]
    prediction_id=accumulating_new_data(features,prediction)
    return prediction,prediction_id
