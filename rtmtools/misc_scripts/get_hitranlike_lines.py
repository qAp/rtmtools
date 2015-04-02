

path_line = '01_H2O'
path_hitranlike = '01_H2O_hitranlike'

with open(path_line, mode = 'r', encoding = 'utf-8') as file:
    c = file.read()


lines = [line for line in c.split('%%%%%%%%')[-1].split('\n') \
         if line and line[2] not in [' ', '-']]

print('number of hitran-like lines:', len(lines))

with open(path_hitranlike, mode = 'w', encoding = 'utf-8') as file:
    file.write('\n'.join(lines))




