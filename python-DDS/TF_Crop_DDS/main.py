# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:22:42 2018
@author: admin
"""

import argparse
from server import Server
from client import Client

def main():
    parser = argparse.ArgumentParser(description='client and server',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--src', type=str, help='base network')
    parser.add_argument('--logic', type=str, help='logic')
    parser.add_argument('--modelpath', type=str, default='/home/bowen/model/faster', help='CNN model')
    srcargs = parser.parse_args()
   
    Srv = Server(srcargs)
    Clt = Client(srcargs,Srv)
    
    Clt.Run()
    
    
if __name__ == '__main__':
    main()
