# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 21:22:42 2018
@author: admin
"""

import argparse
from server_tf import Server

def main():
    parser = argparse.ArgumentParser(description='client and server',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--src', type=str, help='base network')
    parser.add_argument('--logic', type=str, help='logic')
    parser.add_argument('--modelpath', type=str, default='resnet_voc0712-0010.params', help='CNN model')
    srcargs = parser.parse_args()
   
    Srv = Server(srcargs)
    Srv.RUNCNN(srcargs.src,0)
    
    
if __name__ == '__main__':
    main()
