import pickle
from keras.utils import np_utils
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Flatten
import numpy as np

def make_childs_new(model, population, loc,noise):
    parent = load_model(model)
    for i in range(0,population):
        child = Sequential()
        child.add(Dense(100, input_dim=22,activation='tanh'))
        child.add(Dense(100, activation='tanh'))
        child.add(Dense(2,activation='tanh'))
        child.compile(loss='mean_squared_error', optimizer='adam')
        for lay in range(0,3):
            weights = parent.layers[lay].get_weights()
            weights[0] += np.random.normal(0,noise, size=weights[0].shape)
            child.layers[lay].set_weights(weights)
        name = './'+loc+'/EVO'+str(i)+'.h5'
        child.save(name)

def make_childs_opponent(model_list, population, loc,noise):
    counter = 0
    for model in model_list:
        parent = load_model(model)
        for i in range(0,int(population/len(model_list))):
            child = Sequential()
            child.add(Dense(40, input_dim=39,activation='tanh'))
            child.add(Dense(2,activation='tanh'))
            child.compile(loss='mean_squared_error', optimizer='adam')
            for lay in range(0,2):
                weights = parent.layers[lay].get_weights()
                weights[0] += np.random.normal(0,noise, size=weights[0].shape)
                child.layers[lay].set_weights(weights)
            name = './'+loc+'/EVO'+str(counter*5+i)+'.h5'
            child.save(name)
        counter += 1

#make_childs_new('Dense1001003.h5', 10, 'EVO_models')
#new_model = load_keras_model('MLPLALL4.h5')
#w,b = get_weights(new_model)
#make_childs(w,b)
