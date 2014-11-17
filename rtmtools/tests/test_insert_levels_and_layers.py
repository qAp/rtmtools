import numpy as np
import aerutils






def test():
    xlevels = np.arange(0, 8., 2.)
    ylayers = np.arange(1, 7., 2.)
    
    print('xlevels = ', xlevels)
    print('ylayers = ', ylayers)
    print(aerutils.insert_levels_and_layers(xlevels))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], ))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], n = 1))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], n = 2))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], between_levels = (0, 1)))
    #print(insert_levels_and_layers(xlevels, xlayerss = [ylayers], between_levels = (0, 1), n = 1))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], between_levels = (1, 3)))
    #print(aerutils.insert_levels_and_layers(xlevels, xlayerss = [ylayers], between_levels = (1, 3), n = 2))
    
def test1():
    xlevels = np.arange(0, 13., 2)
    ylayers = np.arange(1, 12., 2)
    zlayers = 2 * np.arange(1, 12., 2.) - 1
    print('xlevels = ', xlevels)
    print('ylayers = ', ylayers)
    print('zlayers = ', zlayers)
    #print(aerutils.insert_levels_and_layers(xlevels))
    #print(aerutils.insert_levels_and_layers(xlevels, xlayerss=[ylayers]))
    #print(aerutils.insert_levels_and_layers(xlevels, xlayerss=[ylayers], n = 2))
    print(aerutils.insert_levels_and_layers(xlevels, xlayerss=[ylayers, zlayers], between_levels=(4, 5), n = 1))


if __name__ == '__main__':
    test()
    test1()
