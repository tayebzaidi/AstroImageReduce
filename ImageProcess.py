import os
import sys
import argparse
import numpy as np
import pyfits
import matplotlib
import matplotlib.pyplot as plt



if __name__ == '__main__':
    print("Starting Combination and Correction")
    bias_list = []
    for root, subdirs, files in os.walk('.'):
        print root, subdirs, files
            
