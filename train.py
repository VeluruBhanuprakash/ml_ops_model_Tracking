import pandas as pd 
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.model_selection import train_test_split
import json
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import plotly.graph_objects as go

import pickle

appModel = Flask(__name__) # initializing a flask app

@appModel.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    prediction = trainmodel()
    print('prediction is', prediction)
    # showing the prediction results in a UI
    return render_template('results.html', prediction=prediction)
    #return render_template("index.html")


def trainmodel():
        df = pd.read_csv("data_processed.csv")
        #### Get features ready to model! 
        y = df.pop("cons_general").to_numpy()
        y[y< 4] = 0
        y[y>= 4] = 1
        X = df.to_numpy()
        X = preprocessing.scale(X) # Is standard
        # Impute NaNs
        imp = SimpleImputer(missing_values=np.nan, strategy='mean')
        imp.fit(X)
        X = imp.transform(X)
        # Linear model
        clf = LogisticRegression()
        yhat = cross_val_predict(clf, X, y, cv=15)
        acc = np.mean(yhat==y)
        tn, fp, fn, tp = confusion_matrix(y, yhat).ravel()
        specificity = tn / (tn+fp)
        sensitivity = tp / (tp + fn)
        # Now print to file
        with open("metrics.json", 'w') as outfile:
                json.dump({ "accuracy": acc, "specificity": specificity, "sensitivity":sensitivity}, outfile)

        # Let's visualize within several slices of the dataset
        score = yhat == y
        score_int = [int(s) for s in score]
        df['pred_accuracy'] = score_int

        # Bar plot by region

        '''sns.set_color_codes("dark")
        ax = sns.barplot(x="region", y="pred_accuracy", data=df, palette = "Greens_d")
        ax.set(xlabel="Region", ylabel = "Model accuracy")
        plt.savefig("by_region.png", dpi=80)'''
        fig = fig = go.Figure([go.Bar(x=df["region"], y=df["pred_accuracy"])])
        fig.write_image("by_region.png")
        return { "accuracy": acc, "specificity": specificity, "sensitivity":sensitivity}

if __name__ == "__main__":
	appModel.run(debug=True) # running the app

