# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name:        Catchment Tool                                                 #
# Purpose:     Tool for delineating upstream catchments and reach catchment   #
#              area (RCA) polygons.                                           #
#                                                                             #
# Author:      Jesse Langdon                                                  #
#              South Fork Research, Inc. (SFR)                                #
#              Seattle, Washington                                            #
#                                                                             #
# Published:   2016-Oct-4                                                     #
# Version:     1.0                                                            #
# Copyright:   (c) SFR 2016                                                   #
# License:     Simple BSD                                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#!/usr/bin/env python

# Import modules
import arcpy
from util.drainage import delineate_catch as catch

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Catchment Tool"
        self.alias = "catchment"
        # List of tool classes associated with this toolbox
        self.tools = [DelineateCatchments]


# Delineate Catchments tool
class DelineateCatchments(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Delineate Catchments"
        self.description = "Requires a DEM, stream network polyline feature class, and stream segment point" + \
				            "feature class, and delineates catchment areas as polygons for each stream" + \
				            "segment endpoint. The script requires a watershed/HUC polygon defining the" + \
				            "analysis area, DEM raster, stream network, pour points, and an existing file" + \
				            "geodatabase for processing output data. A bankfull polygon is an option input," + \
				            "which can improve  the results of the DEM reconditioning process. The user can" + \
				            "optionally choose to delineate upstream (i.e. overlapping) catchments."
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName='Watershed polygon feature class',
            name='huc_input',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Input')

        param1 = arcpy.Parameter(
            displayName='DEM raster',
            name='elev_input',
            datatype='DERasterDataset',
            parameterType='Required',
            direction='Input')

        param2 = arcpy.Parameter(
            displayName='Stream network polyline feature class dissolved by branch ID',
            name='strm_input',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Input')

        param3 = arcpy.Parameter(
            displayName='Segmented stream network polyline feature class',
            name='strm_seg',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Input')

        param4 = arcpy.Parameter(
            displayName='Bankfull (or stream area) polygon feature class',
            name='bf_input',
            datatype='DEFeatureClass',
            parameterType='Optional',
            direction='Input')

        param5 = arcpy.Parameter(
            displayName='Output file geodatabase',
            name='outFGB',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')

        param6 = arcpy.Parameter(
            displayName='Upstream (i.e. overlapping) catchments?',
            name='upstream_bool',
            datatype='GPBoolean',
            parameterType='Optional',
            direction='Input',
            enabled='true')

        params = [param0, param1, param2, param3, param4, param5, param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        catch.main(parameters[0].valueAsText,
                parameters[1].valueAsText,
                parameters[2].valueAsText,
                parameters[3].valueAsText,
                parameters[4].valueAsText,
                parameters[5].valueAsText,
                parameters[6].valueAsText)

        return

# def main():
#     tbx = Toolbox()
#     tool = DelineateCatchments()
#     tool.execute(tool.getParameterInfo(), None)
#
# if __name__ == "__main__":
#     main()