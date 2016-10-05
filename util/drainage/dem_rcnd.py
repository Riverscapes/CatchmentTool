# file name:	dem_rcnd.py
# description:	This function preprocesses elevation raster data, then reconditions
#				the elevation data using a vector stream network dataset.
#				The resulting raster datasets can serve as inputs for other tools that 
#				calculate drainage area, slope, and other raster-based metrics for a  
#				drainage basin. This tool uses the Whitebox GAT decay coefficient to
#				burn in streams.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension

import arcpy
from arcpy.sa import *

# DEM reconditioning
def dem_recnd(in_dem, in_huc, in_strm, outFGB):
    arcpy.AddMessage("Preprocessing the DEM...")
    # burn in stream raster
    desc = arcpy.Describe(in_dem)
    cell_size = round(desc.meanCellWidth)
    dem_burn = Raster(in_dem) - Power(Divide(cell_size, (cell_size + EucDistance(Raster(in_strm)))), 2 ) * 4
    dem_fill = Fill(dem_burn, "")
    dem_fill.save(outFGB + r"\dem_recond")
    return dem_fill