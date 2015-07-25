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
    flat_list = np.zeros(36, dtype=dt)
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
        master_bias = pyfits.getdata('master_bias.fits')
    except:
        try:
            cpus = multiprocessing.cpu_count()
        except NotImplementedError:
            cpus = 2   # arbitrary default
        
        pool = ThreadPool(processes=cpus)

        biasData = pool.map(MasterObject, [bias_list[idx] for idx, _ in enumerate(bias_list)])
        print(len(biasData))

        #biasData = np.array([pyfits.getdata("%s" % name) for name in bias_list])

        master_bias = np.median(biasData, axis=0)
        print(master_bias)
        print(len(master_bias))
        hdu = pyfits.PrimaryHDU(master_bias)
        hdu.header.add_comment("Median of all bias exposures")
        pyfits.writeto("master_bias.fits", master_bias)

    #Begin flat fielding
    print("Beginning Flat Fielding")
    flat_data = {}
    b_flats = []
    v_flats = []
    r_flats = []
    i_flats = []

    #Band information is in header dict at entry
    #'CMMTOBS'.  Change here if necessary
    for idx,_ in enumerate(flat_list):
        dataHdr = pyfits.getheader(flat_list[idx])
        if('B' or 'b') in dataHdr['CMMTOBS']:
            print(dataHdr['CMMTOBS'])
            b_flats.append(flat_list[idx])
        elif('R' or 'r') in dataHdr['CMMTOBS']:
            r_flats.append(flat_list[idx])
            print(dataHdr['CMMTOBS'])
        elif 'V' in dataHdr['CMMTOBS']:
            v_flats.append(flat_list[idx])
            print(dataHdr['CMMTOBS'])
        elif 'I' in dataHdr['CMMTOBS']:
            i_flats.append(flat_list[idx])
            print(dataHdr['CMMTOBS'])

    flat_data['b_flats'] = b_flats
    flat_data['v_flats'] = v_flats
    flat_data['r_flats'] = r_flats
    flat_data['i_flats'] = i_flats

    print(flat_data)
    
    for key, value in flat_data:
        pyfits.getdata(

    print("Beginning data correction")
    for idx, _ in enumerate(data_list):
        dataHdr = pyfits.getheader(data_list[idx])
        print(dataHdr['CMMTOBS'])



if __name__ == '__main__':
    sys.exit(main())

