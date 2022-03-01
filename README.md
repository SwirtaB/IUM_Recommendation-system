# Recommendation-system
#### Authors: Bartosz Świrta, Radosław Radziukiewicz

Project within the subject Machine Learning Engineering (IUM). 
The scope of this project is to create a recommendation system for the fictional 
company named ***"eSzoppping"***. The recommendation system should benefit the 
company marketing and sales strategy.

## Motivation

<p align="justify">
In this project we play the role of an analyst working in the company <b><i>"eSzoppping"</i></b> - an
online store with electronics and computer games. Working on this position is not easy - the task we 
get in the form of enigmatic description and it is up to us to specify the details so that they can 
be implemented. This, of course, requires understanding the problem, analyzing data, sometimes negotiating 
with the boss. Apart from analyzing the issue and training the models, we have to prepare them for production 
implementation - assuming that in the future there will be new versions, with which we will experiment.
</p>


## Exact task

Some people come to our website and can't decide which products to take a closer look at. 
Maybe we could give them some recommendation?


## Problem analysis

The problem analysis can be found in notebook called ***"problem_analysis.ipynb"***.
Unfortunately, it is available only in Polish version.


## Data analysis

The data analysis can be found in notebook called ***"data_analysis.ipynb"***.
Unfortunately, it is available only in Polish version.


## Prepared models

As the solution to the problem, we have implemented 2 models serving the recommendations
to the users. <br><br>

**Model number 1** is a simple model, serving recommendations 
based on products metric score. Metric used is similar to the one used by IMDB 
recommendation systems.<br><br>

**Model number 2** is more advanced model. It is based on the collaborative filtering 
and grouping method. It groups users based on their interests and for each 
group it serves most popular products within this group.


## Tests

Models have been tested with the usage of custom testing method.
The method is based on session splitting and predicting the 
outcomes of next user activity. Metric used for testing purposes
is the accuracy. <br><br>

Model 1 results: **40%** of accuracy. <br>
Model 2 results: **74%** of accuracy.


## Micro-service

Models can be released to production with the usage of prepared micro-service.
Micro-service implementation uses Flask-restful framework.
The service API is available in the JSON form.


## Final documentation

The final documentation of the project contains many more useful and 
exhausting side-notes. Unfortunately, it is available only in Polish version.
