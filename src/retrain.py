from src.data_loader import input_output,load_data
from src.train import train
import sqlite3
import pandas as pd
from src.model import cross_validation
from src.config import DB_NAME

def retrain():
    conn=sqlite3.connect(DB_NAME)
    new_data=pd.read_sql_query("SELECT SepalLengthCm,SepalWidthCm,PetalLengthCm, PetalWidthCm,user_feedback as Species FROM inferences WHERE user_feedback IS NOT null",conn)
    if len(new_data)>0 and len(new_data)%20==0:
        old_data=load_data('dataset/Iris.csv')
        combined_data=pd.concat([old_data,new_data],ignore_index=True)
        model=train(combined_data)
        X,y=input_output(combined_data)
        print("The model's accuracy is :",cross_validation(model,X,y))
        conn.commit()
        conn.close()
        return True
    else:
        conn.commit()
        conn.close()
        print("not enought data to retrain")
        return False