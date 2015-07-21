import os
import sys
import argparse
import multiprocessing
from multiprocessing.pool import ThreadPool
import numpy as np
import pyfits
import re
import matplotlib
import matplotlib.pyplot as plt

def MasterObject(bias_data):
    biasData_idx = pyfits.getdata("%s" % bias_data)
    
    return biasData_idx

def main():

    print("Starting Combination and Correction")

    dt = np.dtype((str, 32))

    bias_list = np.zeros(25, dtype=dt)
    flat_list = np.zeros(40, dtype=dt)
    data_list = np.zeros(40, dtype=dt)

    bias_counter = 0
    flat_counter = 0
    data_counter = 0

    #bias_search = re.compile('(.\d+.\d+b\d+.fits)')    
    for root, subdirs, files in os.walk('.'):
        for f in files:
            if f.endswith('b00.fits'):
                bias_list[bias_counter] = os.path.join(root, f)
                bias_counter += 1
            elif f.endswith('f00.fits'):
                flat_list[flat_counter] = os.path.join(root,f)
                flat_counter += 1
            elif f.endswith('o00.fits'):
                data_list[data_counter] = os.path.join(root,f)
                data_counter += 1

#    for i, bias in enumerate(bias_list):
#        print(bias, i)

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2   # arbitrary default
    
    pool = ThreadPool(processes=cpus)

    biasData = pool.map(MasterObject, [bias_list[idx] for idx, _ in enumerate(bias_list)])
    print len(biasData)

    master_bias = np.median(biasData)
    print master_bias

if __name__ == '__main__':
    sys.exit(main())

