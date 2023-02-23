import dxchange
import numpy as np
import tomovector as pt
import time
import scipy.ndimage as ndimage 
if __name__ == "__main__":

    # Load object
    ux = dxchange.read_tiff('rec/ux.tiff')#[170:170+64]
    uy = dxchange.read_tiff('rec/uy.tiff')#[170:170+64]
    uz = dxchange.read_tiff('rec/uz.tiff')#[170:170+64]
    u = np.zeros([3,*ux.shape],dtype='float32')
    u[0] = ux
    u[1] = uy
    u[2] = uz
    u = u[:,::2,::2,::2]
    u = ndimage.gaussian_filter(u, sigma=1)
    
    dxchange.write_tiff(u[0],'rec/ux.tiff',overwrite=True)
    dxchange.write_tiff(u[1],'rec/uy.tiff',overwrite=True)
    dxchange.write_tiff(u[2],'rec/uz.tiff',overwrite=True)
    # exit()
    print(u.shape)
    # Init sizes and parameters                    
    nz = u.shape[1] # vertical size
    n = u.shape[2] # horizontal size
    ntheta = n # number of projection angles         
    ngpus = 1 # number of gpus
    pnz = nz # chunk size to fit gpu memory
    niter = 257 # number of iterations
    method = 'fourierrec' # method for fwd and adj Radon transforms (fourierrec, linerec)
    dbg = True # show convergence
    
    p = np.zeros([3,ntheta,1],dtype='float32')
    # init angles
    theta = np.linspace(0,np.pi,ntheta).astype('float32')
        
    p[0] = np.cos(theta)[np.newaxis,:,np.newaxis]
    p[1] = -np.sin(theta)[np.newaxis,:,np.newaxis]
    p[2] = 0
        
    with pt.SolverTomo(theta, p, ntheta, nz, n, pnz, n/2, method, ngpus) as slv:
        # generate data        
        data = slv.fwd_tomo_batch(u)
        # noise = np.abs(data)-np.random.poisson(np.abs(data))
        dxchange.write_tiff(data,  f'rec/data{method}', overwrite=True)
        # exit()
        # data[:]+=noise
        # dxchange.write_tiff(data,  f'rec/datanoise{method}', overwrite=True)
        # exit()
        # CG sovler
        t = time.time()
        ur = slv.cg_tomo(data, u*0, niter, dbg)
        print(f'Rec time {time.time()-t}s')
    # save results
    dxchange.write_tiff(ur[0],  f'rec/urx_2_{method}', overwrite=True)
    dxchange.write_tiff(ur[1],  f'rec/ury_2_{method}', overwrite=True)
    dxchange.write_tiff(ur[2],  f'rec/urz_2_{method}', overwrite=True)
    