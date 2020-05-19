# Script to extract all .ibw images in a directory and dump a load of png files showing height, phase or conductance info and some metadata


# Alex Summerfield, 15/03/2017



# importing libraries

import numpy as np
import ARFuncs as AR # ARFuncs library
from matplotlib import pyplot as plt
import glob
import os
import fnmatch


# defining the ARdump function to open and process all data channels

def ARdump(ARFileObject,filename):



    channels = ARFileObject.data['Image'].keys() # gets the names of the available data channels

    # sort channels alphabetically

    channels.sort()

    # perform plane correction on height channels

    i = 1

    plt.figure()

    plt.suptitle(filename)

    # calculating the shape of the export grid

    splotSize = np.ceil(np.sqrt(len(channels))) # rounding up to nearest number to make grid for subplots

    for channel in channels:

        plt.subplot(splotSize,splotSize,i) # defining the subplot to use

        i += 1 # iterating plot number

        # Converting and performing corrections for each type of data

        if fnmatch.fnmatch(channel,'*Height*'):

            try:
                ARFileObject.planeLevel(channel) # first-order plane correction on each channel
            except:
                print 'could not plane level: ' + channel
            try:
                ARFileObject.lineMedian(channel) # performing line median correction on the height values
            except:
                print 'could not line median level: ' + channel
            try:
                ARFileObject.zeroHeight(channel) # zeroing the bottom height value
            except:
                print 'could not zero height of: ' + channel

            colorMapToUse = 'afmhot' # use gray colourmap for height data

        if fnmatch.fnmatch(channel,'*Phase*'): # correct phase channels

            try:
                ARFileObject.lineMedian(channel) # performing line median correction on the height values
            except:
                print 'could not line median level: ' + channel

            colorMapToUse = 'seismic' # use gray colourmap for height data

        if fnmatch.fnmatch(channel,'*Current*'): # if a current channel then convert to conductivity

            ARFileObject.Current2Cond(channel)

            colorMapToUse = 'hot' # use gray colourmap for height data

        if fnmatch.fnmatch(channel,'*Deflection*'): # if deflection channel

            try:
                ARFileObject.lineMedian(channel) # performing line median correction on the height values
            except:
                print 'could not line median level: ' + channel

            colorMapToUse = 'hsv'

        if fnmatch.fnmatch(channel,'*Amplitude*'): # if amplitude channel

            try:
                ARFileObject.lineMedian(channel) # performing line median correction on the height values
            except:
                print 'could not line median level: ' + channel

            colorMapToUse = 'gray'

        # rotating the image by 90 degrees for display

        ARFileObject.rotateChannel(channel)

        # arranging the data into a grid and plotting

        plt.imshow(ARFileObject.data['Image'][channel],cmap=colorMapToUse)

        plt.title(channel)
        plt.axis('off')

        # stripping filename of .ibw extension for saving as image

    exportName = filename[:-4]

    plt.savefig(exportName+'.png')

    plt.close()




 # getting .ibw files in current directory

fnames = glob.glob('*.ibw')

for fname in fnames: # for every file

    print 'Dumping File: ' + fname
    dataFile = AR.ARfile() # creating Asylum file instance
    dataFile.load(fname) # loading in file
    ARdump(dataFile,fname) # performing data dump operation
    print 'Dumped'

#plt.show()

# end of script
