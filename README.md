# dSARsim - Dummy Synthetic Aperture Radar Simulator

dSARsim is a dummy Synthetic Aperture Radar (SAR) simulator which is suited for DIDACTIC PURPOSES. This software is not intended for research applications.

The pseudo-simulation is carried out taking in account only the scene geometry using a simple rule. Radiometry is NOT simulated. The result is a grayscale scene where it is possible to visually discriminate the typical geometrical effects seen in SAR images, e.g. layover, shadowing and foreshortening.

The software takes as input a Digital Terrain Model (DTM) or a Digital Surface Model (DSM) and returns as output a pseudo-SAR scene in slant range geometry. The main parameters that can be varied are:

  - Incidence angle;
  - Aspect angle;
  - Viewing direction;
  - Azimuth pixel spacing;
  - Slant range pixel spacing.

For further details on the pseudo-simulation principles please have a look at the related documentation, when it will be available... until then try to understand the comments within the code! :)

### Current version
0.5

