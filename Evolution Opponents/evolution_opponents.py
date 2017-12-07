import shutil
import os
import wrapper_opponents as wrapper
import time
from evolution_nn import make_childs_new, make_childs_opponent
import numpy as np
import random
population = 20
counter = 0
start_model = 'opponent_model.h5'
model_one = 'one.h5'
model_two = 'two.h5'
model_three = 'three.h5'
model_four = 'four.h5'
loc = 'EVO_models'
loc2 = 'Opponent_models'
noise = 0.001
if __name__ == "__main__":
    if not os.path.exists(loc):
        os.makedirs(loc)
    make_childs_opponent([start_model, start_model, start_model, start_model], population, loc, noise)
    open('laptimes.txt', 'w') #delete old results

while counter < 20:
    for i in range(population):
        filename = 'EVO'+str(i)+'.h5'
        shutil.copy(os.path.join(loc, filename), os.path.join('EVO_opponent_model.h5'))
        for track_id in range(0,5):
            circuit_name  = wrapper.train(track_id)
            time.sleep(15)
            os.system('pkill xterm')
            print ('trained',filename,'on',circuit_name)

            laptimes = open('laptimes.txt', 'r')
            lap_times = laptimes.readlines()
            lap_times = [x.strip() for x in lap_times]
            print(lap_times)
            lines = len(lap_times)
            if lines < i*5+track_id+1:
                print("Child did not finish, adding DNF")
                with open('laptimes.txt', 'a') as laptimes:
                    laptimes.write("DNF DNF DNF DNF\n")
                    laptimes.close()

    data = open('laptimes.txt', 'r')
    data_lines = data.readlines()
    data_lines = [x.strip() for x in data_lines]
    fitnesses_track = []
    for line in data_lines:
        if line == "DNF DNF DNF DNF":
            fitnesses_track.append(300000)
        else:
            data_points = line.split(' ')
            fitness = 10*float(data_points[0])+100*float(data_points[1])+100*float(data_points[3])
            fitnesses_track.append(fitness)
    fitnesses = []
    for child in range(population):
        fitnesses.append(np.average(fitnesses_track[child*5:child*5+5]))
    print(fitnesses)
    with open('fitnesses.txt', 'a') as fit_text:
        fit_text.write(str(min(fitnesses))+"\n")
    four_idx = [fitnesses.index(x) for x in sorted(fitnesses, reverse=False)[:4]]
    print("The fastest childs were numbers: ", four_idx)
    shutil.copy(os.path.join(loc,  'EVO'+str(four_idx[0])+'.h5'), os.path.join('one.h5'))
    shutil.copy(os.path.join(loc,  'EVO'+str(four_idx[1])+'.h5'), os.path.join('two.h5'))
    shutil.copy(os.path.join(loc,  'EVO'+str(four_idx[2])+'.h5'), os.path.join('three.h5'))
    shutil.copy(os.path.join(loc,  'EVO'+str(four_idx[3])+'.h5'), os.path.join('four.h5'))
    filename2 = 'opponent_model_generation_'+str(counter)+'.h5'
    counter += 1
    shutil.copy(os.path.join(loc, 'EVO'+str(four_idx[0])+'.h5'), os.path.join(loc2,filename2))
    make_childs_opponent([model_one, model_two, model_three, model_four], population, loc, noise)
    open('laptimes.txt', 'w') #delete results for new generation
