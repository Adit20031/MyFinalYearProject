import numpy as np 
import pandas as pd 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
# Random Forest model
from sklearn.ensemble import RandomForestClassifier
import nltk
import pickle
import joblib
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from sklearn.feature_extraction.text import CountVectorizer
data= pd.read_csv("C:\AdityaClassProject3\sqliv2.csv",encoding='utf-16')
data.head()
#create the transform
vectorizer = CountVectorizer(min_df=2, max_df=0.7, stop_words=stopwords.words('english')) 
# tokenize(fit) and build vocab 
vectorizer.fit(data['Sentence'].values.astype('U')) # .astype('U') -> convert to Unicode   
print(vectorizer.vocabulary_) 
#encode document(transform)
vector= vectorizer.transform(data['Sentence'].values.astype('U'))
posts= vector.toarray()
print(vector.shape)
print(type(vector))
print(posts) 
transformed_posts=pd.DataFrame(posts)
df=pd.concat([data,transformed_posts],axis=1)
X=df[df.columns[2:]]
y=df['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X.head()
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)
y_pred_log_reg=log_reg.predict(X_test)
#accuracy_score(y_test, y_pred_log_reg)
print(y_pred_log_reg)
joblib.dump(log_reg, 'logisticRegression.pkl') 
with open('myVectorizer', 'wb') as file:
    pickle.dump(vectorizer, file)


