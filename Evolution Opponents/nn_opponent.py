import pickle
from keras.utils import np_utils
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Flatten
import numpy as np

def str_to_float_with_precision(item):
    precision = 2
    return round(float(item),2)

def generate_mlp():
    features = 39
    model = Sequential()
    model.add(Dense(40, input_dim=features,activation='tanh')) #word vector size 32
    #Add output layer with 1 node to output either 0 or 1
    model.add(Dense(2,activation='tanh'))
    model.compile(loss='mean_squared_error', optimizer='adam')
    for lay in range(0,2):
        weights = model.layers[lay].get_weights()
        weights[0] = np.zeros(shape=weights[0].shape)
        model.layers[lay].set_weights(weights)
    print(model.summary())
    model.save('opponent_model.h5')

def predict_opponent_output(model,input_data):
    input_data = np.reshape(input_data,(1,39))
    output = model.predict(input_data)
    return float(output[:,0]),float(output[:,1])

def load_keras_opponent_model(modelname):
    newmodel = load_model(modelname)
    return newmodel

generate_mlp()
