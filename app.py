from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_mailman import Mail, EmailMessage
import pickle
import joblib
import logging
from datadog import initialize, statsd

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
db = PyMongo(app).db
mail = Mail()
app.config['MAIL_SERVER']='smtp.fastmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='aditya346@fastmail.com'
app.config['MAIL_PASSWORD']='p3wxnjm6f5wwn655'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail.init_app(app)

# Initialize Datadog logging handler
options = {
    'api_key': '5a35a682fa9a1bbb99001a18e759c720',  # Replace with your Datadog API key
    'app_key': 'f232320030d3a2f0073cdbd7e9457402448f0164'   # Replace with your Datadog application key
}
initialize(**options)

# Configure root logger to send logs to Datadog
root_logger = logging.getLogger()
root_logger.addHandler(logging.StreamHandler())
root_logger.setLevel(logging.INFO)

randomForest_from_joblib = joblib.load('logisticRegression.pkl')  
myvectorizer = pickle.load(open("myVectorizer", 'rb')) 

@app.route("/")
def hello_world():
    return render_template("index.html")

# Function to send email message
def send_message(a):
    msg = EmailMessage(
        "Alert! Action Required",
        "ip address:" + a,
        "aditya346@fastmail.com",
        ["aditya346@fastmail.com"]
    )
    msg.send()

# Function to clean data
def clean_data(input_val):
    input_val = input_val.replace('\n', '')
    input_val = input_val.replace('%20', ' ')
    input_val = input_val.replace('=', ' = ')
    input_val = input_val.replace('((', ' (( ')
    input_val = input_val.replace('))', ' )) ')
    input_val = input_val.replace('(', ' ( ')
    input_val = input_val.replace(')', ' ) ')
    return input_val

@app.route('/predict', methods=['GET', 'POST'])
def predict_sql_data():
    input_val = request.form.get('textInput')
    input_val2 = request.form.get('pass13')
    db.inventory.insert_one({"Entered Username": input_val, "Entered Password": input_val2})
    input_val = clean_data(input_val)
    input_val2 = clean_data(input_val2)
    input_val = [input_val]
    input_val2 = [input_val2]
    input_val = myvectorizer.transform(input_val).toarray()
    result = randomForest_from_joblib.predict(input_val)
    input_val2 = myvectorizer.transform(input_val2).toarray()
    result2 = randomForest_from_joblib.predict(input_val2)
    
    # Get IP address
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        a = request.environ['REMOTE_ADDR']
    else:
        a = request.environ['HTTP_X_FORWARDED_FOR']
    
    # Log events and send message
    if result == 1 and result2 == 0:
        statsd.event("SQL Injection Attempt", "SQL Injection Attempt Detected", alert_type="error")
        send_message(a)
        logging.error("SQL Injection Attempt")
        return render_template('index.html', prediction_text="There is an attempt to Exploit the database")
    elif result == 0 and result2 == 1:
        statsd.event("SQL Injection Attempt", "SQL Injection Attempt Detected", alert_type="error")
        send_message(a)
        logging.error("SQL Injection Attempt")
        return render_template('index.html', prediction_text="There is an attempt to Exploit the database")
    elif result == 1 and result2 == 1:
        statsd.event("SQL Injection Attempt", "SQL Injection Attempt Detected", alert_type="error")
        send_message(a)
        logging.error("SQL Injection Attempt")
        return render_template('index.html', prediction_text="There is an attempt to Exploit the database")
    else:
        statsd.event("User Login Successful", "User Successfully Logged In", alert_type="success")
        logging.info("User Logged In Successfully")
        return render_template('dream.html', prediction_text='Login Successful')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)



