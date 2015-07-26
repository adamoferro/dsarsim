# dSARsim - Dummy Synthetic Aperture Radar Simulator

dSARsim is a dummy Synthetic Aperture Radar (SAR) simulator written in python v3 which is suited for didactic purposes.

The pseudo-simulation is carried out taking in account only the scene geometry using a simple rule. Radiometry is NOT simulated. The result is a grayscale scene where it is possible to visually discriminate the typical geometrical effects seen in SAR images, e.g. layover, shadowing and foreshortening.

The software takes as input a Digital Terrain Model (DTM) or a Digital Surface Model (DSM) and returns as output a pseudo-SAR scene in slant range geometry. The main parameters that can be varied are:

  - Incidence angle;
  - Aspect angle;
  - Viewing direction;
  - Azimuth pixel spacing;
  - Slant range pixel spacing.

For further details on the pseudo-simulation principles please have a look at the related documentation, when it will be available... until then try to understand the comments within the code! :)

### Usage

`-h, --help`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; show help message and exit.
 
`-i INPUT, --input INPUT`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; input DTM/DSM image (32 bit floating-point GeoTIFF image). If the image does not contain pixel size information, dSARsim assumes the pixel spacing is equal to 1 m.

`-o OUTPUT, --output OUTPUT`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; output image (same format as input).

`-ai INCIDENCEANGLE, --incidenceAngle INCIDENCEANGLE`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SAR incidence angle in degrees. Default is 30.

`-aa ASPECTANGLE, --aspectAngle ASPECTANGLE`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; angle wrt the North-South axis. aspect angle > 0 = clockwise. Default is 0.

`-pa AZIMUTHPIXELSPACING, --azimuthPixelSpacing AZIMUTHPIXELSPACING`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; spacing between azimuth pixels in the output image in meters, or 0 if automatically set as the same spacing of the input DTM/DSM. Default is 0.

`-pr SLANTRANGEPIXELSPACING, --slantRangePixelSpacing SLANTRANGEPIXELSPACING`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; spacing between slant range pixels in the output image in meters, or 0 if automatically calculated in order to obtain a flat-terrain-'ground range' simulation. Default is 0.

`-d {w,e}, --direction {w,e}`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; direction of view of the sensor. 'w' = West to East, 'e' = East to West (assuming the sensor going from North to South with aspect angle = 0). Default is 'w'.

`-n NODATAVALUE, --noDataValue NODATAVALUE`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; no data value used in the DTM/DSM image, if any. Default is -9999.

`-r, --rotateBack`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; if aspect angle != 0, rotate back output image by -aspect angle degrees. Use only if azimuthPixelSpacing and slantRangePixelSpacing are not set by user in order to get simulations directly comparable to input DTM/DSM. Default is not set.

`-s SUBPROCESSES, --subprocesses SUBPROCESSES`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; number of concurrent threads to be run (works only if the module multiprocessing is installed). Default is 1.

`--debug`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; debug mode. Default is not set.

`-v, --version`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; show program's version number and exit.

### Dependencies

dSARsim is written in python v3.x. Thus, in order to execute it you need a python v3.x environment. The following libraries are needed:

  - sys
  - math
  - copy
  - argparse
  - numpy
  - scipy.ndimage
  - osgeo.gdal
  - multiprocessing.Pool (not necessary but needed for parallel computation)
  

### Current version
0.5

### Disclaimer

The author does not guarantee that this software will always provide correct results nor that it will not crash your hardware. As mentioned above, dSARsim is intended for didactic purposes. Any use outside this scope is discouraged. In any case, any use of dSARsim is ONLY user responsibility.
