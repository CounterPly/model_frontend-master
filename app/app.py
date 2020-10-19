#!/usr/bin/env python
import base64
import io
import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
from flask import Flask, render_template, request, Markup

matplotlib.use('Agg')

# default traveler constants
default_building = 'Building 10'
default_publications = 20
default_conferences = 30
default_status = 'Fulltime'
default_title = 'Dr'
default_expertise = 'Infectious Diseases'
default_institute = 'NHLBI'
default_pfellows = 3
default_reports = 7

app = Flask(__name__)


@app.before_first_request
def startup():
    global average_reentry_rate
    average_reentry_rate = 39.2


@app.route("/", methods=['POST', 'GET'])
def submit_new_profile():
    model_results = ''
    if request.method == 'POST':
        selected_building = request.form['selected_building']
        selected_publication = request.form['selected_publication']
        selected_conferences = request.form['selected_conferences']
        selected_status = request.form['selected_status']
        selected_title = request.form['selected_title']
        selected_expertise = request.form['selected_expertise']
        selected_institute = request.form['selected_institute']
        selected_pfellows = request.form['selected_pfellows']
        selected_preports = request.form['selected_preports']

        # Prepare to send to backend
        building = selected_building
        num_publications = selected_publication
        num_conferences = selected_conferences
        status = selected_status
        title = selected_title
        expertise = selected_expertise
        institute = selected_institute
        num_postdocs = selected_pfellows
        num_reports = selected_preports

        x = ["building", "num_publications", "num_conferences", "status", "title", "expertise", "institute",
             "num_postdocs", "num_reports"]
        y = [building, num_publications, num_conferences, status, title, expertise, institute, num_postdocs,
             num_reports]
        data = {k: v for k, v in zip(x, y)}
        headers = {
            'Content-Type': 'application/json'
        }
        url = "http://modelbackend-env.eba-ph3ffryw.us-east-2.elasticbeanstalk.com/api/predict"

        # Retrieves the response from the backend
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))

        probability_of_reentering = round(float(response.text.encode('utf8')), 2)
        fig = plt.figure()
        objects = ('Average Re-Entry Rate', 'Fictional Employee')
        y_pos = np.arange(len(objects))
        performance = [average_reentry_rate, probability_of_reentering]

        ax = fig.add_subplot(111)
        colors = ['gray', '#8294AE']
        plt.bar(y_pos, performance, align='center', color=colors, alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.axhline(average_reentry_rate, color="r")
        plt.ylim([0, 100])
        plt.ylabel('Re-Entry Probability')
        plt.title(
            f'Will the employee return to work onsite?\n '
            f'There\'s a {str(round(probability_of_reentering, 2))}% chance that the employee will work onsite.'
        )
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return render_template('index.html',
                               model_results=model_results,
                               model_plot=Markup('<img src="data:image/png;base64,{}">'.format(plot_url)),
                               selected_building=selected_building,
                               selected_publication=selected_publication,
                               selected_conferences=selected_conferences,
                               selected_status=selected_status,
                               selected_title=selected_title,
                               selected_expertise=selected_expertise,
                               selected_institute=selected_institute,
                               selected_pfellows=selected_pfellows,
                               selected_preports=selected_preports)
    else:
        # set default employee settings
        return render_template('index.html',
                               model_results='',
                               model_plot='',
                               selected_building=default_building,
                               selected_publication=default_publications,
                               selected_conferences=default_conferences,
                               selected_status=default_status,
                               selected_title=default_title,
                               selected_expertise=default_expertise,
                               selected_institute=default_institute,
                               selected_pfellows=default_pfellows,
                               selected_preports=default_reports)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
