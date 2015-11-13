# -*- coding: utf-8 -*-
"""
Created on Sun Nov 08 23:40:43 2015

@author: Ben
"""
import scipy.signal as signal
import numpy as np
# from threading import Thread
# import thread

def covConv(a,b, lags=20):
    ''' returns fft convolution result 
    assumes a, b to be same length 1-d numpy arrays
    '''
    result = signal.fftconvolve(a, b[::-1], mode='full')/(len(a)-1)
    start = len(a)-lags
    stop = len(a)-1+lags
    return result[start:stop]  
    
def getCovMatrix(I1, Q1, I2, Q2, lags=20, extended = True):
    ''' # Matrix index as follows:
    # 0: <I1I1>
    # 1: <Q1Q1>
    # 2: <I2I2>
    # 3: <Q2Q2>
    # 4: <I1Q1>
    # 5: <I2Q2>
    # 6: <I1I2>
    # 7: <Q1Q2>
    # 8: <I1Q2>
    # 9: <Q1I2> '''
    CovMat = np.zeros([11,lags*2-1])
    if extended is True :
        # these should simply show a single peak 
        # with a height of its covariance
        # CovMat[0,:] = thread.start_new_thread( covConv, (I1, I1, lags) )
        # thread.start_new_thread( print_time, ("Thread-2", 4, ) )
        CovMat[0,:] = covConv(I1, I1, lags)                 
        CovMat[1,:] = covConv(Q1, Q1, lags)
        CovMat[2,:] = covConv(I2, I2, lags)
        CovMat[3,:] = covConv(Q2, Q2, lags) 
        
    # and these one go to zero for non singlemode squeezed states
    CovMat[4,:] = covConv(I1, Q1, lags)
    CovMat[5,:] = covConv(I2, Q2, lags)
    # these ones are relevant for 2 mode squeezing  
    CovMat[6,:]= covConv(I1, I2, lags)
    CovMat[7,:]= covConv(Q1, Q2, lags)
    CovMat[8,:]= covConv(I1, Q2, lags)
    CovMat[9,:]= covConv(Q1, I2, lags)
    CovMat[10,:] = abs(1j*(CovMat[8,:]+CovMat[9,:]) + (CovMat[6,:] - CovMat[7,:]))
    return CovMat
    