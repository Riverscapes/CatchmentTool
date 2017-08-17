## Catchment Tool
- Version: 1.0
- Revised 10-4-2016

### Summary
The **Catchment Tool** is an ArcGIS Python toolbox which currently includes one tool: 
*Delineate Catchments*. This tool was developed by [South Fork Research, Inc.](https://southforkresearch.org) 
to automate the process of delineating catchment area polygons for each stream reach 
or segment within a stream network. The catchment area polygons can then be used to 
calculate statistical values for geographically coincident spatial datasets representing
 environmental parameters.

Catchment areas represent all surfaces draining to a single point in a drainage basin 
(i.e. a pour point). Based on a set of pour points, the *Delineate Catchments* tool will
 delineate either upstream catchment area polygons (all areas upstream of a pour point 
 within the analysis area, producing overlapping polygons), or reach catchment areas 
 (all areas in the immediate vicinity, non-overlapping with adjacent drainage areas).  
 One of the key component in this process is the reconditioning of the digital elevation
  model (DEM) supplied by the user. The initial tool methods involved burning a stream 
  network polyline feature class into a DEM, but later development switched to burning 
  in a polygon representing open stream areas to recondition to better conform to the 
  stream network. The stream area polygons can be derived from the USGS National 
  Hydrography Dataset (NHD) [NHDArea](http://nhd.usgs.gov/userGuide/Robohelpfiles/NHD_User_Guide/Feature_Catalog/Hydrography_Dataset/NHDArea/NHD_Area.htm) 
  stream features, or a bankfull area polygon based on bankfull widths calculated for 
  the stream network. We recommend that the input stream network first be cleaned 
  and edited so that is topologically correct, and split into user-defined segments of 
  uniform length using the *Segment Stream Network* tool, which is part of the 
  **Geomorphic Network and Analysis Toolbox** ([GNAT](https://github.com/Riverscapes/arcGNAT)).

Although similar tools are available, such as ESRI's ArcHydro framework
 (Maidment, 2002) and the Multi-Watershed Delineation Tool (Chinnayakanahalli, K. et al., 2006), 
 these tools do not specifically allow overlapping, upstream catchment area delineation.
 
 #### Citations
* Chinnayakanahalli, K., C. Kroeber, R. Hill, J. Olson, D. G. Tarboton and C. Hawkins, (2006). Manual for Regional Watershed Analysis Using the Multi-Watershed Delineation Tool. Utah State University. 

* Maidment, D. R. (2002). Arc Hydro: GIS for water resources (Vol. 1). ESRI, Inc.
 
 ### Support
 
 The **Catchment Tool** is actively developed and maintained by [South Fork Research, Inc.](https://southforkresearch.org).