import sys
import numpy as np
import surface as sr


def self_affine(saparams, power_of_two, seed=None):
    '''
    Generates a self affine rough surface using provided parameters, discretization size
    and random seed.

    >>> import surface_parameters as sp
    >>> saparams = sp.self_affine_default()
    >>> s = self_affine(saparams, 7, seed=0)
    >>> s.rms() == saparams.hrms
    True
    '''
    np.random.seed(seed)    
    lambda_L_over_lambda_0 = 1 if saparams.lambda_L_over_lambda_0 is None else saparams.lambda_L_over_lambda_0    
    lambda_L_over_lambda_1 = sys.maxsize if saparams.lambda_L_over_lambda_1 is None else saparams.lambda_L_over_lambda_1
    N, L = 2**power_of_two, saparams.dimensions[0]     
    power = -(saparams.hurst+1.) 
    q_L = 2*np.pi/L # q ... abs frequency
    f_L, f_d = 1.0/N, np.sqrt(2*0.5**2)  # f ... rel frequency
    f_0, f_1 = f_L*lambda_L_over_lambda_0, f_L*lambda_L_over_lambda_1  
    A = np.zeros((N,N), dtype=complex)
    rand_norm_1, rand_norm_2 = np.random.randn(N/2+1,N/2+1), np.random.randn(N/2+1,N/2+1)
    rand_unif_1, rand_unif_2 = np.random.rand(N/2+1,N/2+1), np.random.rand(N/2+1,N/2+1)
    for i in range(0, int(N/2+1)):
        for j in range(0, int(N/2+1)):
            phase = 2. * np.pi * rand_unif_1[i,j]                       
            rad = 0.
            f = np.sqrt((float(i)/N)**2 + (float(j)/N)**2)
            if i != 0 or j != 0:       
                f = f if f > f_0 else f_0 # hi pass for f_0 
                rad = rand_norm_1[i,j] * f**power
            if f > f_1:                   # lo pass for f_1 
                rad, phase = 0., 0.
            A[i , j] = rad*np.cos(phase) + rad*np.sin(phase)*1j
            i0 = 0 if i == 0 else N-i
            j0 = 0 if j == 0 else N-j
            A[i0,j0] = rad*np.cos(phase) - rad*np.sin(phase)*1j 
    A[N/2,0] = A[N/2,0].real + 0j
    A[0,N/2] = A[0,N/2].real + 0j
    A[N/2,N/2] = A[N/2,N/2].real + 0j
    for i in range(1, int(N/2)):
        for j in range(1, int(N/2)):
            phase = 2. * np.pi * rand_unif_2[i,j]
            f = np.sqrt((float(i)/N)**2 + (float(j)/N)**2)
            f = f if f > f_0 else f_0 # hi pass for f_0             
            rad = rand_norm_2[i,j] * f**power
            if f > f_1:               # lo pass for f_1 
                rad, phase = 0., 0.
            A[i,N-j] = rad*np.cos(phase) + rad*np.sin(phase)*1j
            A[N-i,j] = rad*np.cos(phase) - rad*np.sin(phase)*1j
    H = np.real(np.fft.ifft2((A)))
    s = sr.Surface(H, L/float(N))
    s.scale_to_property('rms', saparams.hrms)
    s.shift_to_zero_mean()
    return s


if __name__ == '__main__':
    import doctest
    doctest.testmod()