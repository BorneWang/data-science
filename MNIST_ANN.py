# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#-----------------------------head-----------------------------------------
import numpy as np
from sklearn.datasets import load_iris
from sklearn.cross_validation import train_test_split
import matplotlib.pyplot as plt
iris = load_iris()

#-------------------------train_test_split---------------------------------
x_train1,x_test1,y_train1,y_test1 = train_test_split(iris.data[0:50],
                                                     iris.target[0:50],
                                                     test_size=0.5,
                                                     random_state=1)
x_train2,x_test2,y_train2,y_test2 = train_test_split(iris.data[50:100],
                                                     iris.target[50:100],
                                                     test_size=0.5,
                                                     random_state=1)
x_train3,x_test3,y_train3,y_test3 = train_test_split(iris.data[100:150],
                                                     iris.target[100:150],
                                                     test_size=0.5,
                                                     random_state=1)
x_train = np.array([x_train1,x_train2,x_train3]).reshape(75,4)
y_train = np.array([y_train1,y_train2,y_train3]).reshape(75)
x_test = np.array([x_test1,x_test2,x_test3]).reshape(75,4)
y_test = np.array([y_test1,y_test2,y_test3]).reshape(75)

#-------------------------AdaBoostClassifier--------------------------------
from sklearn.ensemble import AdaBoostClassifier
clf = AdaBoostClassifier(random_state=1,n_estimators=100)
clf.fit(x_train,y_train)

#---------------------------result------------------------------------------
clf.predict(x_train)
clf.score(x_train,y_train)
clf.predict(x_test)
clf.score(x_test,y_test)
fi = clf.feature_importances_
  