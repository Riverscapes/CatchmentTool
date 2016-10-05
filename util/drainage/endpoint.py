# file name:	endpoint.py
# description:	The purpose of this script is to plot points at the downstream end of stream segments. The point that
#               is the furthest downstream on a stream branch is plotted so that is slightly upstream of the final vertex.
#               The end point for all other stream segments is then plotted at the same coordinates as the ending vertex.
#               The main function in this script is called by the by the main function in seg_network.py.
# author:		Jesse Langdon
# dependencies:	ESRI arcpy package

import arcpy

arcpy.env.overwriteOutput = True

def plot_branch(in_strm_dslv, in_strm_seg, in_fields, cellSize):
    arcpy.AddMessage("    ...for stream branches.")
    # select segment furthest downstream on a stream branch
    branch_end_vrtx = arcpy.FeatureVerticesToPoints_management(in_strm_dslv, r"in_memory\branch_end_vrtx", "END")
    end_seg = arcpy.SelectLayerByLocation_management(in_strm_seg, "INTERSECT", branch_end_vrtx, "#", "NEW_SELECTION")
    # create new point feature class to store segment endpoints
    endpoint_branch = arcpy.CreateFeatureclass_management("in_memory", "endpoint_branch", "POINT", "", "DISABLED", "DISABLED",
                                                    in_strm_seg)
    arcpy.AddField_management(endpoint_branch, "LineOID", "DOUBLE")
    arcpy.AddField_management(endpoint_branch, "Value", "DOUBLE")
    # plot points at end of stream branches (upstream of end vertex at 85% of length)
    with arcpy.da.SearchCursor(end_seg, (in_fields)) as search_end:
        with arcpy.da.InsertCursor(endpoint_branch, ("SHAPE@", "LineOID", "Value")) as insert_end:
            for row_end in search_end:
                try:
                    line_geom = row_end[0]
                    length = float(line_geom.length)
                    oid = str(row_end[1])
                    start = arcpy.PointGeometry(line_geom.firstPoint)
                    prct_end = line_geom.positionAlongLine(length - (cellSize * 4), False).firstPoint
                    insert_end.insertRow((prct_end, oid, str(length)))
                except Exception as e:
                    print e.message
    return endpoint_branch

def plot_other(in_strm_seg, endpoint_branch, in_fields, cellSize):
    arcpy.AddMessage("    ...for all other stream segments.")
    # plot points at end of all other remaining stream segments
    other_seg = arcpy.SelectLayerByAttribute_management(in_strm_seg, "SWITCH_SELECTION")
    other_end_vrtx = arcpy.CreateFeatureclass_management("in_memory", "other_end_vrtx", "POINT", "", "DISABLED",
                                                          "DISABLED",
                                                          in_strm_seg)
    arcpy.AddField_management(other_end_vrtx, "LineOID", "DOUBLE")
    arcpy.AddField_management(other_end_vrtx, "Value", "DOUBLE")
    with arcpy.da.SearchCursor(other_seg, (in_fields)) as search_other:
        with arcpy.da.InsertCursor(other_end_vrtx, ("SHAPE@", "LineOID", "Value")) as insert_other:
            for row_other in search_other:
                try:
                    line_geom = row_other[0]
                    length = float(line_geom.length)
                    oid = str(row_other[1])
                    start = arcpy.PointGeometry(line_geom.firstPoint)
                    seg_end = line_geom.positionAlongLine(length - (cellSize * 2), False).firstPoint
                    insert_other.insertRow((seg_end, oid, str(length)))
                except Exception as e:
                    print e.message
    # append end points from other stream segments to branch end points
    endpoint_all = arcpy.Append_management(other_end_vrtx, endpoint_branch, "NO_TEST")
    return endpoint_all

def main(in_strm_dslv, in_strm_seg, cellSize):
    # call the other two functions and return final endpoints to the seg_network.py module
    arcpy.MakeFeatureLayer_management(in_strm_dslv, "in_strm_dslv_lyr")
    arcpy.MakeFeatureLayer_management(in_strm_seg, "in_strm_seg_lyr")
    fields = ["SHAPE@", "LineOID"]
    endpoints_branch = plot_branch("in_strm_dslv_lyr", "in_strm_seg_lyr", fields, cellSize)
    endpoints_final = plot_other("in_strm_seg_lyr", endpoints_branch, fields, cellSize)
    return endpoints_final