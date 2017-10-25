# file name:	delineate_catch.py
# description:	This script takes a DEM raster, stream network polyline feature class, and stream
#				segment point feature class, and delineates catchment areas as polygons for each
#				stream segment endpoint. The script requires a watershed/HUC polygon defining the
#				analysis area, DEM raster, stream network, pour points, and an existing file geodatabase
#				processing output datasets. A bankfull polygon is an option input, which can improve
#				the results of the DEM reconditioning process. The user can optionally choose to
#				delineate  upstream (i.e. overlapping) catchments. If this option is not selected,
#				RCA polygons are delineated instead.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, custom functions

import arcpy
import sys
import os.path
import datetime
from util.metadata import Metadata
import strm_ras as sR
import dem_rcnd as dR
import endpoint as end
from arcpy.sa import *

def check_req(strm_input, elev_input):
    # check for M and Z-enabled geometry and projected spatial reference
    input_hasM = arcpy.Describe(strm_input).hasM
    input_hasZ = arcpy.Describe(strm_input).hasZ
    input_strm_sr = arcpy.Describe(strm_input).spatialReference
    input_elev_sr = arcpy.Describe(elev_input).spatialReference

    if input_hasM == True:
        arcpy.AddMessage("Geometry of the input stream network feature class is M-value enabled. "
                         "Please disable the M-value.")
    if input_hasZ == True:
        arcpy.AddMessage("Geometry of the input stream network feature class is Z-value enabled. "
                         "Please disable the Z-value.")
    if input_strm_sr.type != "Projected":
        arcpy.AddMessage("Input stream network feature class has a geographic spatial reference. "
                         "Please change to a projected spatial reference.")
    if input_elev_sr.type != "Projected":
        arcpy.AddMessage("Input elevation raster dataset has a geographic spatial reference. "
                         "Please change to a projected spatial reference.")

    if input_hasM == True \
            or input_hasZ == True \
            or input_strm_sr.type != "Projected" \
            or input_elev_sr.type != "Projected":
        sys.exit(0)


def main(huc_input, elev_input, strm_input, strm_seg, bf_input, outFGB, upstream_bool):
    # check data characteristics of input stream network for tool requirements
    check_req(strm_input, elev_input)

    # set environment parameters
    arcpy.AddMessage("Setting processing environment parameters...")
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = outFGB
    arcpy.env.outputCoordinateSystem = elev_input
    arcpy.env.extent = elev_input
    arcpy.env.snapRaster = elev_input
    arcpy.env.cellSize = elev_input
    arcpy.env.mask = elev_input
    cellSizeResult = arcpy.GetRasterProperties_management(elev_input, "CELLSIZEX")
    cellSize = float(cellSizeResult.getOutput(0))
    snap_dist = cellSize * 2

    # metadata
    mWriter = Metadata.MetadataWriter("Delineate Catchments", "0.3")
    mWriter.createRun()
    # input parameters for metadata file
    mWriter.currentRun.addParameter("Watershed polygon feature class", huc_input)
    mWriter.currentRun.addParameter("DEM raster", elev_input)
    mWriter.currentRun.addParameter("Stream network polyline feature class", strm_input)
    mWriter.currentRun.addParameter("Segmented stream network feature class", strm_seg)
    mWriter.currentRun.addParameter("Bankfull (or stream area) polygon feature class", bf_input)
    mWriter.currentRun.addParameter("Output file geodatabase", outFGB)
    mWriter.currentRun.addParameter("Upstream (i.e. overlapping) catchments?", upstream_bool)

    # check segmented stream network for LineOID field, and add if it's missing
    seg_oid = arcpy.Describe(strm_seg).OIDFieldName
    list_field = arcpy.ListFields(strm_seg, "LineOID")
    strm_seg_lyr = "strm_seg_lyr"
    arcpy.MakeFeatureLayer_management(strm_seg, strm_seg_lyr)
    if len(list_field) == 0:
        arcpy.AddField_management(strm_seg_lyr, "LineOID", "LONG")
        arcpy.CalculateField_management(strm_seg_lyr, "LineOID", "!" + seg_oid +"!", "PYTHON_9.3")

    # convert stream network to raster
    arcpy.AddMessage("Converting stream network to raster format...")
    strm_ras = sR.convert_ras(huc_input, bf_input, strm_input)

    # recondition DEM using stream network
    arcpy.AddMessage("Reconditioning DEM with stream network...")
    dem_rec = dR.dem_recnd(elev_input, huc_input, strm_ras, outFGB)

    # calculate flow direction and flow accumulation
    arcpy.AddMessage("Calculating flow direction and accumulation...")
    fd = FlowDirection(dem_rec, "NORMAL")
    fa = FlowAccumulation(fd, "", "FLOAT")

    # Plot segment endpoints as pour points
    arcpy.AddMessage("...plotting pour points.")
    seg_endpoints = end.main(strm_input, strm_seg, cellSize)
    arcpy.FeatureClassToFeatureClass_conversion(seg_endpoints, outFGB, "endpoints")

    # create blank polygon feature class to store catchments
    arcpy.AddMessage("Creating blank polygon feature class to store catchments...")
    arcpy.CreateFeatureclass_management(outFGB, "catch_ply", "POLYGON", seg_endpoints) #the coord. sys. for pnt_input is applied
    arcpy.MakeFeatureLayer_management(outFGB + "\\catch_ply", "catch_ply_lyr")

    arcpy.MakeFeatureLayer_management(seg_endpoints, "seg_endpoints_lyr")

    # create field mappings for pour points
    fm = arcpy.FieldMappings()
    fm.addTable(seg_endpoints)

    # set up counters
    total_cnt = arcpy.GetCount_management("seg_endpoints_lyr")

    # if upstream boolean is selected, iterate through each point
    arcpy.AddMessage("Delineating catchments for each pour point...")
    if upstream_bool == 'true':
        with arcpy.da.SearchCursor(seg_endpoints, ["SHAPE@", "LineOID"]) as cursor:
            for row in cursor:
                try:
                    arcpy.FeatureClassToFeatureClass_conversion(row[0], "in_memory", "pnt_tmp", "#", fm)
                    arcpy.MakeFeatureLayer_management("in_memory\\pnt_tmp", "pnt_tmp_lyr")
                    arcpy.CalculateField_management("pnt_tmp_lyr", "LineOID", row[1], "PYTHON_9.3")
                    pnt_snap = SnapPourPoint("pnt_tmp_lyr", fa, snap_dist, "LineOID")
                    wshd_ras = Watershed(fd, pnt_snap, "VALUE")
                    arcpy.RasterToPolygon_conversion(wshd_ras, "in_memory\\wshd_ply", "NO_SIMPLIFY", "VALUE")
                    arcpy.MakeFeatureLayer_management("in_memory\\wshd_ply", "wshd_ply_lyr")
                    arcpy.AddField_management("wshd_ply_lyr", "LineOID", "LONG")
                    arcpy.CalculateField_management("wshd_ply_lyr", "LineOID", row[1], "PYTHON_9.3")
                    arcpy.Append_management("wshd_ply_lyr", "catch_ply_lyr", "NO_TEST")
                    arcpy.AddMessage("Catchment delineated for " + str(round(row[1])) + " of " + str(total_cnt) + " records...")
                except:
                    arcpy.AddMessage("\nError delineating catchments for point #" + str(row[1]) + ": " + arcpy.GetMessages(2))
                    arcpy.AddMessage("Moving to next pour point...")
                    #raise Exception
                    continue
    # otherwise, create a "RCA-style" polygons
    else:
        arcpy.MakeFeatureLayer_management(seg_endpoints, "pnt_tmp_lyr")
        snap_dist = cellSize * 2
        pnt_snap = SnapPourPoint("pnt_tmp_lyr", fa, snap_dist, "LineOID")
        wshd_ras = Watershed(fd, pnt_snap, "Value")
        arcpy.RasterToPolygon_conversion(wshd_ras, "in_memory\\wshd_ply", "NO_SIMPLIFY", "Value")
        arcpy.MakeFeatureLayer_management("in_memory\\wshd_ply", "wshd_ply_lyr")
        arcpy.AddField_management("wshd_ply_lyr", "LineOID", "LONG")
        arcpy.CalculateField_management("wshd_ply_lyr", "LineOID", "!grid_code!", "PYTHON_9.3")
        arcpy.Append_management("wshd_ply_lyr", "catch_ply_lyr", "NO_TEST")

    # final clean up of upstream catchment polygons
    arcpy.AddMessage("Removing slivers and dissolving watershed polygons...")
    arcpy.AddField_management("catch_ply_lyr", "sqkm", "DOUBLE")
    arcpy.AddMessage("...calculating area of catchment polygons.")
    arcpy.CalculateField_management("catch_ply_lyr", "sqkm", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3")
    arcpy.AddMessage("...selecting sliver polygons.")
    arcpy.SelectLayerByAttribute_management("catch_ply_lyr", "NEW_SELECTION", """"sqkm" <= 0.0001""")
    arcpy.AddMessage("...merging sliver polygons with largest neighbors.")
    arcpy.Eliminate_management("catch_ply_lyr", "in_memory\\catch_eliminate", "LENGTH")
    arcpy.MakeFeatureLayer_management("in_memory\\catch_eliminate", "catch_elim_lyr")
    arcpy.AddMessage("...dissolving catchment polygons based on LineOID value.")
    arcpy.Dissolve_management("catch_elim_lyr", outFGB + "\\catch_final", "LineOID")
    arcpy.MakeFeatureLayer_management(outFGB + "\\catch_final", "catch_final_lyr")
    arcpy.Delete_management(outFGB + "\\catch_ply")

    # find errors
    arcpy.AddMessage("Adding error_code field...") ### TEMP
    arcpy.AddField_management("catch_final_lyr", "error_code", "SHORT")
    # error_code = 1; polygons are "too small"
    arcpy.AddField_management("catch_final_lyr", "sqkm", "DOUBLE")
    arcpy.CalculateField_management("catch_final_lyr", "sqkm", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("catch_final_lyr", "NEW_SELECTION", """"sqkm" <= 0.02 """)
    arcpy.CalculateField_management("catch_final_lyr", "error_code", "1", "PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("catch_final_lyr", "CLEAR_SELECTION")
    # error_code = 2; polygons are "too thin"
    arcpy.AddField_management("catch_final_lyr", "thinness", "DOUBLE")
    arcpy.CalculateField_management("catch_final_lyr", "thinness", """(4*3.14*!SHAPE.AREA!)/(math.pow(!SHAPE.LENGTH!,2))""", "PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("catch_final_lyr", "NEW_SELECTION", """"thinness" < 0.090""")
    arcpy.CalculateField_management("catch_final_lyr", "error_code", "2", "PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("catch_final_lyr", "CLEAR_SELECTION")
    arcpy.DeleteField_management("catch_final_lyr", "thinness")

    # Outputs and stop processing clock for metadata
    mWriter.currentRun.addOutput("Output catchment area polygons", outFGB + r"\catch_final")
    mWriter.currentRun.addOutput("Output endpoints", outFGB + "\endpoints")
    mWriter.currentRun.addOutput("Output reconditioned DEM", outFGB + r"\dem_recond")
    mWriter.finalizeRun()
    # Write the metadata file
    d = datetime.datetime.now()
    outPath = os.path.dirname(outFGB)
    metadataFile = "{0}{1}{2}{3}{4}{5}{6}{7}".format(outPath, r"\metadata_", d.year, d.month, d.day, d.hour, d.minute, ".xml")
    mWriter.writeMetadataFile(metadataFile)

    return