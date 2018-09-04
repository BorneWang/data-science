# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:22:42 2018
@author: admin
"""

import argparse
from server_2 import Server
from client_3 import Client
import time

def main():
    tic0 = time.time()
    parser = argparse.ArgumentParser(description='client and server',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--src', type=str, help='base network')
    parser.add_argument('--logic', type=str, help='logic')
    parser.add_argument('--params', type=str, default='resnet_voc0712-0010.params', help='CNN model')
    srcargs = parser.parse_args()
   
    Srv = Server(srcargs)
    print("creat server success")
    Clt = Client(srcargs,Srv)
    
    Clt.Run()
    tic_end = time.time()
    print("the whold run time is", tic_end-tic0)
    
    
if __name__ == '__main__':
    main()
