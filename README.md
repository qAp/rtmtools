# RTMTOOLS #

## LBLRTM longwave calculations ##

Start at script_flux_calculation.py.   

Specify concentration of gases under the section "Atmospheric profile".           
For example, 
```
#!python

lblrtmin.atmopro_mls75pro(outputfilename = filepath_atmpro,
                          lev0_temp = 294.,
                          H2O = 0,
                          O3 = 0,
                          CO2 = 0,
                          CH4 = aerutils.mixingratio_volume2mass(
substance_name = 'CH4', volume_mix = 1.8e-6),
                       up_to_level = 71)
```
In this case, there is no H2O, O3, nor CO2.  There is CH4 at 1.8e-6 [l/l] (or [parts per part by volume]), but since the function 
``` lblrtmin.atmopro_mls75pro```
takes in units of [g/g] for all gases (except for CO2 which it takes in in units of [l/l]), it is first converted to [g/g] using ```mixingratio_volume2mass```.   

You can run ```python script_flux_calculation.py``` first, which produces file mls75pro.dat containing the atmosphere profile that will be used in the calculation.  

```python scrip_flux_calculation.py --run``` will produce mls75pro.dat and then start the LBLRTM calculation, which will produce OUTPUT_RADSUM, containing the results of the calculation.

```python script_flux_calculation.py --clean``` will remove most of the binary files produced by LBLRTM, except OUTPUT_RADSUM, TAPE5 and TAPE6.  This cleans up the directory in which you have been running LBLRTM.