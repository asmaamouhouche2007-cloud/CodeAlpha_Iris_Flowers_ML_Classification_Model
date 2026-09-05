import sqlite3
from src.config import DB_NAME
def accumulating_new_data(features,predicted_species):
    """Soring new data to the database. 
          args:
               features : a dataframe containing columns of sepal and petal measurments 
               predicted_species : the output given by the model when using predict (string)
          output:
               row_id : which is the Id of the data recently added to the database in order to be passed 
               to the html page which will handle the process of adding user feedback to this row .
    """
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute('''INSERT INTO inferences
    (SepalLengthCm,SepalWidthCm,PetalLengthCm, PetalWidthCm, predicted_species)
    VALUES (?,?,?,?,?)
    ''',(features['SepalLengthCm'],features['SepalWidthCm'],features['PetalLengthCm'],features['PetalWidthCm'],\
         predicted_species))
    conn.commit()
    row_id=cursor.lastrowid
    conn.close()
    print("✅ New inference data logged.")
    return row_id
