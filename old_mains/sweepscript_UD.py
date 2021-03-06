'''
Generic Sweep script
(currently setup for no more than 3 dims)

20/10/2015
- B
'''
from time import time, sleep
from parsers import copy_file
from ramp_mod import ramp
thisfile = __file__

filen_0 = 'S1_1008'
folder = 'data\\'
'''
Sweeping in I mode
Noticed that this changed my LP filtering
'''

# Driver
from dummydriver import instrument as dummy
from keithley2000 import instrument as key2000
from Yoko import instrument as yoko
from DataStorer import DataStoreSP


vm = key2000('GPIB0::29::INSTR')

iBias = yoko('GPIB0::1::INSTR',
           name = 'Yoko V R=(998.83+14.24)KOhm',
           start = -8e-6,
           stop = 8e-6,
           pt = 3201,
           sstep = 0.1e-6, # def max step it can take
           stime = 1e-6)
#iBias.prepare_v(vrange = 5)  # vrange =2 -- 10mV, 3 -- 100mV, 4 -- 1V, 5 -- 10V, 6 -- 30V
iBias.prepare_i(vrange = 4)  #  vrange =4 -- 1mA, 5 -- 10mA, 6 -- 100mA
iBias.UD = True

vMag = yoko('GPIB0::10::INSTR',
            name = 'Magnet V R=2.19KOhm',
            start = -600e-3,
            stop = 600e-3,
            pt = 401,
            sstep = 10e-3,
            stime = 1e-6)
vMag.prepare_v(vrange = 4)

PSG = dummy('GPIB0::11::INSTR',
           name = 'none',
           start = 0,
           stop = 1,
           pt = 1,
           sstep = 20e-3,
           stime = 1e-3)

iBias.sweep_par = 'iv'
vMag.sweep_par = 'iv'

dim_1= iBias
def sweep_dim_1(obj, value):
    ramp(obj, obj.sweep_par, value, obj.sstep, obj.stime)
    #obj.sweep_iv(value, 5)
    #sleep(5.1)

dim_2= vMag
def sweep_dim_2(obj, value):
    ramp(obj, obj.sweep_par, value, obj.sstep, obj.stime)

dim_3= PSG
def sweep_dim_3(obj, value):
    pass

# DS = DataStoreSP()
DS = DataStoreSP(folder, filen_0, dim_1, dim_2, dim_3, 'Voltage (V) x1k')
# DS.prepare_data_save(folder, filen_0, dim_1, dim_2, dim_3, 'Voltage (V) x1000')
DS.ask_overwrite()


copy_file(thisfile, filen_0, folder) #backup this script
print 'Executing sweep'
print 'req time (min):'+str(dim_3.pt*dim_2.pt*dim_1.pt*0.032/60)
t0 = time()
try:
    for kk in range(dim_3.pt):
        sweep_dim_3(dim_3,dim_3.lin[kk])
        sweep_dim_2(dim_2,dim_2.start)

        for jj in range(dim_2.pt):
            sweep_dim_2(dim_2,dim_2.lin[jj])
            sweep_dim_1(dim_1,dim_1.start)
            sleep(0.5)
            if dim_1.UD is True:
                print 'Up Trace'
                for ii in range(dim_1.pt):
                    dim_1.set_iv2(dim_1.lin[ii])
                    vdata = vm.get_val()
                    DS.record_data(vdata,kk,jj,ii)
                
                sweep_dim_1(dim_1,dim_1.stop)
                sleep(0.1)
                print 'Down Trace'
                for ii in range((dim_1.pt-1),-1,-1):
                    dim_1.set_iv2(dim_1.lin[ii])
                    vdata = vm.get_val()
                    DS.record_data2(vdata,kk,jj,ii)
            else:
                for ii in range(dim_1.pt):
                    dim_1.set_iv2(dim_1.lin[ii])
                    vdata = vm.get_val()
                    DS.record_data(vdata,kk,jj,ii)

            DS.save_data()
            t1 = time()
            remaining_time = ((t1-t0)/(jj+1)*dim_2.pt*dim_3.pt - (t1-t0))
            print 'req time (h):'+str(remaining_time/3600)
    print 'Measurement Finished'

except (KeyboardInterrupt):
    print '***** Keyboart Interupt *****'

finally:
    print 'Time used min:' +str((time()-t0)/60)
    print 'Yokos -> zero and switch off'
    iBias.sweep_iv(0, 5)
    vMag.sweep_iv(0, 5)
    sleep(5.2)
    iBias.output(0)
    vMag.output(0)
    print  'done'
