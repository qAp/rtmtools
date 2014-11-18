import os


[os.remove(file) for file in ('TAPE3', 'TAPE5', 'lblrtm', 'IN_RADSUM', 'radsum') if os.path.isfile(file)]
#link to TAPE3
os.symlink('../../lblrtm/run_examples/TAPE3_files/TAPE3_aer_v_3.2_ex_little_endian', 'TAPE3')
#link to TAPE5
os.symlink('../../utils/TAPE5', 'TAPE5')
#link to lblrtm
os.symlink('../../lblrtm/lblrtm_v12.2_linux_intel_dbl', 'lblrtm')
#link to IN_RADSUM
os.symlink('../../radsum/run_examples/IN_RADSUM', 'IN_RADSUM')
#link to radsum
os.symlink('../../radsum/radsum_v2.6_linux_intel_dbl', 'radsum')


#run lblrtm
print('Running LBLRTM')
os.system('lblrtm')

#run radsum
print('RADSUM')
os.system('radsum')







