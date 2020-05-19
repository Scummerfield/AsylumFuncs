# module for converting ibw files to image objects for later analysis
# Alex Summerfield 16/08/2016


# loading required libraries

import numpy as np
import glob
import os
from igor import binarywave # for raw ibw import
import re
from matplotlib import pyplot as plt
import fnmatch

# defining Classes

class ARfile:

    kind = 'ARData'

    def __init__(self):

        # defining instance variables.

        self.data = [] # empty container for data
        self.type = "null" # string for the type of file, image or IV curve/spectra - initially null

    def load(self,fname):

        self.parseData(binarywave.load(fname)) # load the ibw file and parse data

    def parseData(self,rawData): # method for parsing data from raw import to self

        # adding raw data to image array

        channelNames = [j for j in rawData['wave']['labels'][2] if len(j)>0] # getting channel names


        parsedData = dict() # empty dict for parsed data
        parsedData['Image'] = dict() # Dict entry for raw image data.

        channelNo = 0 # iterator for each channel
        for name in channelNames: # for each channel name create appropriately named array

            parsedData['Image'][str(name)] = np.array(rawData['wave']['wData'][:,:,channelNo])
            channelNo += 1 # update iterator to next channelNo

        # Adding metadata to each object

        parsedData['meta'] = dict() # empty dictionary for metadata

        # splitting text into attribute pairs

        for j in re.split('\r',rawData['wave']['note']): # splitting the text up into rows using the appropriate line delimiters
            if len(re.split(':',j)) > 1: # checking for length of key value pair, ignore empty rows
                temp = re.split(':',j,1) # spitting the key:value pair
                temp[1] = temp[1].strip() # removing preceeding whitespace from meta
                parsedData['meta'][temp[0].replace(" ","")] = temp[1] # removing space from key names - easier for other things


        self.data = parsedData # assign parsed data to main object data array

    def dataType(self): # checking the type of the data - Image or spectra
        return self.type

    def lineMedian(self,channelName): # perform median line correction on the selected channel

        outData = [] # list for data values

        for i in range(np.shape(self.data['Image'][channelName])[1]): # for each line scan

            lineData = self.data['Image'][channelName][:,i] # each single line scan
            lineMedian = np.median(lineData) # find the median value of the scan
            lineData = np.subtract(lineData,lineMedian) # subtracting the median
            outData.append(lineData) # appending the data to new array

        self.data['Image'][channelName] = np.transpose(np.array(outData)) # writing outdata back to the channel

    def rotateChannel(self,channelName): # rotate channel by 90 degrees for display

        self.data['Image'][channelName] = np.rot90(self.data['Image'][channelName],k=1)

    def planeLevel(self,channelName): # performs a 1st order plane level correction to the specified data channel

        inputArray = np.array(self.data['Image'][channelName]) # creating input array to be flattened

        outData = [] # list for data values

        # Previous code ****************

        Y = inputArray.flatten()

        x_grid, y_grid = np.meshgrid(range(np.shape(inputArray)[0]),range(np.shape(inputArray)[1]))

        X = np.transpose(np.array([x_grid.flatten(),y_grid.flatten(),np.ones(np.size(x_grid))]))

        Xt = np.transpose(X) # transpose of X

        planeCoefficients = np.dot(np.dot(np.linalg.inv(np.dot(Xt,X)),Xt),Y) # calculating coefficients

        fitPlane = planeCoefficients[0]*x_grid + planeCoefficients[1]*y_grid + planeCoefficients[2] # generating z values of fit plane

        # performing plane levelling of the input image by subtracting from the original image

        outData = inputArray - fitPlane # subtracting fitted plane from input

        self.data['Image'][channelName] = np.array(outData) # writing outdata back to the channel

    def zeroHeight(self,channelName): # reduces the minimum value of the channel plane to zero

        inputArray = np.array(self.data['Image'][channelName]) # creating input array to be flattened

        outData = [] # list for data values

        #minVal = np.amin(inputArray.flatten()) # flattening the array and finding the minimum
        minVal = 0
        outData = inputArray - minVal

        self.data['Image'][channelName] = np.array(outData) # writing outdata back to the channel

    def Current2Cond(self,channelName): # Converts the current map to conductivity

        outData = [] # list for data values

        voltageRaw = self.data['meta']['SurfaceVoltage'] # surface voltage from metadata - may contain change


        # remove potential change from the
        if fnmatch.fnmatch(voltageRaw,"*@*"): # if the string for th
            surfaceVoltage = re.split(r"@",voltageRaw)[0] # extract beginning value
            surfaceVoltage = np.float(surfaceVoltage) # convert to float for mathematical manipulation
        else:

            surfaceVoltage = np.float(voltageRaw)

        outData = self.data['Image'][channelName] / surfaceVoltage # perform division to convert to conductivity

        self.data['Image'][channelName] = np.array(outData) # return the conducutance map as an array

    def RMSroughness(self,channelName): # perform RMS roughness calculations on an input matrix

        flattenedArray = self.data['Image'][channelName].flatten() # flattening the array into 1D

        meanHeight = np.mean(flattenedArray) # calculating mean

        y = flattenedArray - meanHeight # calculating difference of height from mean values

        RMS = np.sqrt(np.divide(np.sum(y**2),np.size(y))) # perform RMS roughness calculation

        return RMS # return RMS value

    def isSquare(self,channelName): # Check if the image is square to avoid processing half-finshed scans

        channelData = self.data['Image'][channelName]

        if np.shape(channelData)[0] == np.shape(channelData)[1]:
            imageIsSquare = 'True'
        else:
            imageIsSquare = 'False'

        return imageIsSquare # return logic value


# End of ARfile definition
