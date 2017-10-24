## Using the Catchment Tool

### Software Requirements
* Catchment Tools
* ArcGIS 10.1, SP1
* Spatial Analyst
* Python 2.7.2
* GNAT (optional)

### ArcGIS Geoprocessing Recommendations
* We recommend this tool be run with 64-bit python geoprocessing enabled.
* All inputs, including vector and raster data, are assumed to be in the same coordinate system and projection. 
* Remove M and Z values from the shape field of the input stream network feature class.

## Recommended Processing Workflow
### Data Preprocessing
1. Download the **Catchment Tool**, and unzip into a local directory
2. Add the **Catchment Tool** toolbox into ArcGIS using `ArcToolbox > Add Toolbox`
2. Project all input data (raster and vector) into the same projected coordinate system. Make sure the M and Z values 
are removed from the shape field.
3. Review stream network dataset (and edit if necessary):
    * connectivity of all stream reaches
    * correct flow direction
    * identify and remove all braids
    * (optional) segment the stream network, if desired, using the GNAT Segment Stream Network tool.

### Delineate Catchments Tool input/output
##### *Inputs*

* **Drainage area polygon**: Polygon feature class representing a single watershed or hydrologic unit (HUC) area encompassing the analysis area. *Required input*.

* **DEM**: Unprocessed DEM representing topography for the analysis area. This raster will be “reconditioned” using the stream network and (optionally) the bankfull polygon. *Required input*.

* **Stream network with a Branch ID**: Polyline feature class representing the stream network for the analysis area. This should be the stream network that is produced by the pre-processing workflow outlined above, which should include a Branch ID attribute field. *Required input*.

* **Segmented stream network**: Polyline feature class, output from the Segment Stream Network tool. *Required input*.

* **Stream area polygon**: Polygon feature class representing bankfull or open water stream areas. Can be used (in conjunction with the stream network dataset) to created a raster version of the stream network, which is then burned into the DEM as part of the reconditioning process. *Required input*.

* **Output file geodatabase**: The file geodatabase which will store the resulting catchment area polygons.

* **Upstream (i.e. overlapping) catchments?**: Indicates whether the entire drainage area upstream of each pour point will be delineated as the catchment,
 or if only the immediate reach catchment areas (non-overlapping) will be delineated.

##### *Outputs*

* **catch_final**: The delineated catchment area polygon feature class.
  * Fields Added:
    * OIDtmp: the original ObjectID value of the point record which served as a pour point for the catchment area.
    * sqkm: the calculated area value of the polygon, in square kilometers.
    * error_code: code indicating that an error occurred with the delineation process, most likely due to sub-optimal pour point placement. 
      * **1** = catchment area is too small
      * **2** = catchment area is too thin

* **endpoints**: The point feature class representing stream segment endpoints. These are recommended for use as the pour points feature class input in the Delineate Catchments Tool.
  * Fields Added:
    * LineOID: the ObjectID of the stream segment from which the point was derived. This field can be used to join the endpoints feature class back to the segments feature class.

* **dem_recond**: Reconditioned DEM raster dataset. Provided for context.

### Known Issues
* **Sub-optimal pour point placement**: Unless the stream network that was used to generate pour points was directly derived from the DEM, there will inevitably be stream
segments (and their associated pour point) that will not spatially coincide precisely with areas of highest flow accumulation in the DEM.  This results in delineated catchments 
that are too small, and do not represent the full upstream drainage area.  Currently the Catchment Tool attempts to recondition the DEM by "burning in" the linear stream network and open stream area polygons
so that the DEM more closely conforms to the stream network.  Catchment area polygons with an area value below an arbitrarily chosen threshold
are tagged with an error code, to inform the user that these catchment areas may be suspect.

_Typical problem areas_:
  * Main stems / wide flood plains
  * Areas with dense stream networks
  
* **Long run time**: Selecting the upstream catchment option results in drastically longer processing times.
