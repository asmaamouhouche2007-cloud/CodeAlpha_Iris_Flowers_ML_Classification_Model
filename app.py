from flask import Flask,render_template,request,flash,url_for,redirect
import pandas as pd
from src.predict import predict
from src.retrain import retrain
import sqlite3
from src.config import SECRET_KEY,DB_NAME
app=Flask(__name__)
app.config['SECRET_KEY']=SECRET_KEY

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/predict',methods=('POST',))
def make_prediction():
    try:
        new_data={ 'SepalLengthCm':float(request.form['Sepal_length'])
                  ,'SepalWidthCm':float(request.form['Sepal_width'])
                  ,'PetalLengthCm':float(request.form['Petal_length'])
                  ,'PetalWidthCm':float(request.form['Petal_width'])
        }
        prediction,prediction_id=predict(new_data)
        return render_template('result.html',\
        prediction=prediction\
        ,prediction_id=prediction_id)
    except Exception as e:
        flash(f"Error in making prediction :{e}",'danger')
        return redirect(url_for('home'))
@app.route('/feedback/<int:prediction_id>')
def show_feedback_form(prediction_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT predicted_species FROM inferences WHERE id = ?", (prediction_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        flash("Prediction not found.", "danger")
        return redirect(url_for('home'))
    return render_template('feedback.html', prediction_id=prediction_id, predicted_species=row[0])
@app.route('/feedback',methods=('POST',))
def add_user_feedback():
    # taking the feedback
    prediction_id=request.form['prediction_id']
    feedback=request.form['feedback']
    # update the specific row in the database 
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("UPDATE inferences SET  user_feedback = ?  WHERE id = ?",(feedback,prediction_id))
    conn.commit()
    conn.close()
    flash(f"Thanks for your feedback! Your response was: {feedback}", "success")
    retrain()
    return redirect(url_for('home'))
if __name__=='__main__':
    app.run(port=5003)   
