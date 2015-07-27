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

def MasterObject(data):
    Data_idx = pyfits.getdata("%s" % data)    
    return Data_idx

def main():

    print("Starting Combination and Correction")

    dt = np.dtype((str, 32))

    bias_list = np.zeros(25, dtype=dt)
    flat_list = np.zeros(36, dtype=dt)
    data_list = np.zeros(32, dtype=dt)

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

        biasData = np.array(pool.map(MasterObject, [bias_list[idx] for idx, _ in enumerate(bias_list)]))
        print(biasData.shape)

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
            b_flats.append(flat_list[idx])
        elif('R' or 'r') in dataHdr['CMMTOBS']:
            r_flats.append(flat_list[idx])
        elif 'V' in dataHdr['CMMTOBS']:
            v_flats.append(flat_list[idx])
        elif 'I' in dataHdr['CMMTOBS']:
            i_flats.append(flat_list[idx])

    flat_data['b_flats'] = b_flats
    flat_data['v_flats'] = v_flats
    flat_data['r_flats'] = r_flats
    flat_data['i_flats'] = i_flats

    
    try:
        master_flats = {}
        for key, values in flat_data.items():
            filename = 'master_flat_{}.fits'.format(key[0])
            master_flats[key[0]] = pyfits.getdata(filename)
            print(key[0])
            print(master_flats[key[0]])
        print("Flat files have been read in")
    except:
        try:
            cpus = multiprocessing.cpu_count()
            print("CPU number acquired: {}".format(cpus))
        except NotImplementedError:
            cpus = 2   # arbitrary default
            
        for key, values in flat_data.items():
            print(key, values)
            pool = ThreadPool(processes=cpus)

            flatData_raw = np.array(pool.map(MasterObject, [values[idx] for idx, _ in enumerate(values)]))
            print(flatData_raw.shape)
            #make sure to debias the raw flat
            dbflat = flatData_raw - master_bias
            #take the median of the values
            flat = np.median(dbflat, axis=0)
            #normalize the flat values
            print(np.mean(np.reshape(flat, flat.size)))
            print("Size of flat: {}".format(flat.size))
            master_flat = flat / np.median(np.reshape(flat, flat.size))
            print("Median of flat is: {}".format(np.median(master_flat)))
            print("Mean of flat is: {}".format(np.mean(master_flat)))
            print(master_flat.shape)
            hdu = pyfits.PrimaryHDU(master_flat)
            hdu.header.add_comment("Median of all flat exposures for given band")
            print(key[0])
            filename = "master_flat_{0}.fits".format(key[0])
            print(filename)
            pyfits.writeto(filename, master_flat)

    print("Beginning image data correction")
    data_dict = {}
    b_data = []
    v_data = []
    r_data = []

    for idx, _ in enumerate(data_list):
        dataHdr = pyfits.getheader(data_list[idx])
        print(data_list[idx][13:15])
        if int(data_list[idx][13:15]) >= 21:
            if 'B' in dataHdr['CMMTOBS']:
                b_data.append(data_list[idx])
                print(data_list[idx], dataHdr['CMMTOBS'])
            elif 'V' in dataHdr['CMMTOBS']:
                v_data.append(data_list[idx])
                print(data_list[idx], dataHdr['CMMTOBS'])
            elif 'R' in dataHdr['CMMTOBS']:
                r_data.append(data_list[idx])
                print(data_list[idx], dataHdr['CMMTOBS'])

    data_dict['b_data'] = b_data
    data_dict['v_data'] = v_data
    data_dict['r_data'] = r_data

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2   # arbitrary default
        
    for key, values in data_dict.items():
        print(key, values)
        pool = ThreadPool(processes=cpus)

        data_raw = np.array(pool.map(MasterObject, [values[idx] for idx, _ in enumerate(values)]))
        
        #make sure to debias the raw data
        dbdata = data_raw - master_bias
        #normalize the data values according to the relevant master flat
        print(master_flats[key[0]])
        master_data = dbdata / master_flats[key[0]]
        master_data_median = np.median(master_data, axis=0)
        hdu = pyfits.PrimaryHDU(master_data_median)
        hdu.header.add_comment("Debiased and flat fielded image")
        filename = "master_data_{0}.fits".format(key[0])
        print(filename)
        pyfits.writeto(filename, master_data_median)
        



if __name__ == '__main__':
    sys.exit(main())

