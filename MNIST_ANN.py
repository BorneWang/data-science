# -*- coding: utf-8 -*-
"""
MNIST analysis using Bagging-ANN
王博文
1410069
信息与计算
"""

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

from sklearn.metrics import f1_score

import numpy as np

X_train = mnist.train.images
X_test = mnist.test.images

y_train = np.zeros(55000,dtype=int)
y_test = np.zeros(10000,dtype=int)
for i in range(55000):
    for j in range(9):
        if mnist.train.labels[i][j] == 1:
            y_train[i] = j
            
for i in range(10000):
    for j in range(9):
        if mnist.test.labels[i][j] == 1:
            y_test[i] = j
                        
#--------------------------NeuralNetwork----------------------------------
from sklearn.neural_network import MLPClassifier
 ANN = MLPClassifier(hidden_layer_sizes=(529,), solver='adam', 
                     activation='tanh')
ANN.fit(X_train,mnist.train.labels)
f1_score(mnist.test.labels,ANN.predict(X_test),average='macro')
f1_score(mnist.train.labels,ANN.predict(X_train),average='macro')  

 ANN = MLPClassifier(hidden_layer_sizes=(529,), solver='sgd', 
                     activation='tanh')
ANN.fit(X_train,mnist.train.labels)
f1_score(mnist.test.labels,ANN.predict(X_test),average='macro')
f1_score(mnist.train.labels,ANN.predict(X_train),average='macro') 

ANN_f1score = np.zeros(20)
for i in range(519,539):
     ANN = MLPClassifier(hidden_layer_sizes=(i,), solver='adam', 
                         activation='tanh')
    ANN_f1score[i-519]=f1_score(mnist.test.labels,ANN.predict(X_test), 
                               average='macro')

#----------------------------BaggingClassifier-------------------------------
from sklearn.ensemble import BaggingClassifier
BR = BaggingClassifier(base_estimator=ANN,n_estimators=10,n_jobs=5)
BR.fit(X_train,y_train)
BR.score(X_test,y_test)        
f1_score(y_test,BR.predict(X_test),average='macro')
f1_score(y_train,BR.predict(X_train),average='macro')
            
#------------------------------SVC-----------------------------------------
from sklearn.svm import SVC
svm = SVC()
svm.fit(X_train,y_train)
svm.score(X_test,y_test)
