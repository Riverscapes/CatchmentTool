# file name:	strm_ras.py
# description:	This function creates a stream raster, primarily for use with the DEM reconditioning
#				script (dem_rcnd.py). A stream network polyline feature class is required, and optionally
#				a bankful polygon can serve as an input.	  
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.2

import os, sys, arcpy
from arcpy.sa import *
	
# prep convert vector streams and bankful polygons to raster format
def convert_ras(in_huc, in_bf, in_strm):
	if in_bf:
		arcpy.AddMessage("Preparing the stream network...")
		arcpy.MakeFeatureLayer_management(in_strm, r"in_strm_lyr")
		arcpy.MakeFeatureLayer_management(in_bf, r"in_bf_lyr")
		arcpy.Clip_analysis("in_strm_lyr", in_huc, r"in_memory\strm_clip")
		arcpy.Clip_analysis("in_bf_lyr", in_huc, r"in_memory\bf_clip")
		arcpy.MakeFeatureLayer_management(r"in_memory\strm_clip", "strm_clip_lyr")
		arcpy.MakeFeatureLayer_management(r"in_memory\bf_clip", "bf_clip_lyr")

		cellSize = arcpy.env.cellSize

		# convert streams to a raster format
		arcpy.AddField_management("strm_clip_lyr", "VAL", "SHORT")
		arcpy.CalculateField_management("strm_clip_lyr", "VAL", "1", "PYTHON_9.3")
		arcpy.PolylineToRaster_conversion("strm_clip_lyr", "VAL", r"in_memory\strm_ras", "", "", cellSize)

		# convert bankful polygon
		arcpy.AddField_management("bf_clip_lyr", "VAL", "SHORT")
		arcpy.CalculateField_management("bf_clip_lyr", "VAL", "1", "PYTHON_9.3")
		arcpy.PolygonToRaster_conversion("bf_clip_lyr", "VAL", r"in_memory\bf_ras", "CELL_CENTER", "", cellSize)

		# Mosaic stream and bankful rasters
		strm_final = arcpy.MosaicToNewRaster_management(r"in_memory\bf_ras;in_memory\strm_ras", "in_memory", "strmMSC", "", "8_BIT_UNSIGNED", cellSize, 1, "LAST", "")
		return strm_final
	else:
		arcpy.AddMessage("Preparing the stream network...")
		arcpy.MakeFeatureLayer_management(in_strm, r"in_strm_lyr")
		arcpy.Clip_analysis("in_strm_lyr", in_huc, r"in_memory\strm_clip")
		arcpy.MakeFeatureLayer_management(r"in_memory\strm_clip", "strm_clip_lyr")

		#cellSize = arcpy.env.cellSize
		
		# convert streams to a raster format
		arcpy.AddField_management("strm_clip_lyr", "VAL", "SHORT")
		arcpy.CalculateField_management("strm_clip_lyr", "VAL", "1", "PYTHON_9.3")
		strm_final = arcpy.PolylineToRaster_conversion("strm_clip_lyr", "VAL", r"in_memory\strm_final")
		return strm_final