
import os
import collections



def line_count(path_molecule):
    '''
    Counts the number of lines in the line files used by LBLRTM
    '''
    dir_linesbymolecule = '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/aer_v_3.2/line_files_By_Molecule'
    
    linecount = collections.Counter()
    
    if path_molecule in linecount:
        return linecount[path_molecule]
    else:
        with open(os.path.join(dir_linesbymolecule, \
                               path_molecule, path_molecule), \
                  mode = 'r', encoding = 'utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(' '):
                    linecount[path_molecule] += 1
        return linecount[path_molecule]

    
    

