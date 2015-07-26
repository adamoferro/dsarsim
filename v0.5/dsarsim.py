#!/usr/bin/python3

#   Copyright 2015 Adamo Ferro
#
#   This file is part of dSARsim.
#
#   dSARsim is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   dSARsim is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with dSARsim. If not, see <http://www.gnu.org/licenses/>.


import sys,argparse
from dsarsim.simulator import simulator
from dsarsim.common.image import image

STATE_OK=0
STATE_ERROR=1

def main(argv=None):

    if argv is None:
        argv=sys.argv

    debug_mode=False
    input_filename=""
    output_filename=""

    parser=argparse.ArgumentParser(description='Generates a pseudo-SAR image starting from a DTM/DSM.')
    parser.add_argument('-i','--input',required=True,help='input DTM/DSM image (32 bit floating-point GeoTIFF image).')
    parser.add_argument('-o','--output',required=True,help='output image (same format as input).')
    parser.add_argument('-ai','--incidenceAngle',default='30',type=float,help='SAR incidence angle in degrees. Default is 30.')
    parser.add_argument('-aa','--aspectAngle',default='0',type=float,help='angle wrt the North-South axis. aspect angle > 0 = clockwise. Default is 0.')
    parser.add_argument('-pa','--azimuthPixelSpacing',type=float,default='0',help="spacing between azimuth pixels in the output image in meters, or 0 if automatically set as the same spacing of the input DTM/DSM. Default is 0.")
    parser.add_argument('-pr','--slantRangePixelSpacing',type=float,default='0',help="spacing between slant range pixels in the output image in meters, or 0 if automatically calculated in order to obtain a flat-terrain-'ground range' simulation. Default is 0.")
    parser.add_argument('-d','--direction',default='w',choices=['w','e'],help="direction of view of the sensor. 'w' = West to East, 'e' = East to West (assuming the sensor going from North to South with aspect angle = 0). Default is 'w'.")
    parser.add_argument('-n','--noDataValue',type=float,default='-9999',help="no data value used in the DTM/DSM image, if any. Default is -9999.")
    parser.add_argument('-r','--rotateBack',default=False,action='store_true',help='if aspect angle != 0, rotate back output image by -aspect angle degrees. Use only if azimuthPixelSpacing and slantRangePixelSpacing are not set by user in order to get simulations directly comparable to input DTM/DSM. Default is not set.')
    parser.add_argument('-s','--subprocesses',default='1',type=int,help="number of concurrent threads to be run (works only if the module multiprocessing is installed). Default is 1.")
    parser.add_argument('--debug',action='store_true',default=False,help='debug mode. Default is not set.')
    parser.add_argument('-v','--version',action='version',version='%(prog)s 0.5')
    try:
        args=parser.parse_args()
    except:
        return STATE_ERROR
        
    debug_mode=args.debug
    input_filename=args.input
    output_filename=args.output
    incidence_angle=args.incidenceAngle
    direction=args.direction
    aspect_angle=args.aspectAngle
    azimuth_pixel_spacing=args.azimuthPixelSpacing
    slant_range_pixel_spacing=args.slantRangePixelSpacing
    nodatav=args.noDataValue
    rotate_back=args.rotateBack
    n_subprocesses=args.subprocesses
    
    img=image(nodatav=nodatav)
    
    if img.read(input_filename)==0:
        
        if debug_mode:
            ii=img.getImageInfo()
            print("INFO: Input image size [pixels] and pixel spacing [m]: "+str(ii[0])+", "+str(ii[1]))
        
        sarsim=simulator(ia=incidence_angle,aa=aspect_angle,d=direction,img=img,opsize=(azimuth_pixel_spacing,slant_range_pixel_spacing),rb=rotate_back,sp=n_subprocesses,debug_mode=debug_mode)
        
        if sarsim.simulate()==0:
            if debug_mode:
                print("INFO: Simulation successful.")
            if sarsim.getOutputImage().write(output_filename)==0:
                if debug_mode:
                    print("INFO: Output written.")
                return STATE_OK
            else:
                print("ERROR: Problem during output writing.")            
        else:
            print("ERROR: Problem during simulation.")
    else:
        print("ERROR: Input image reading problem.")
    
    return STATE_ERROR

    
    
if __name__ == "__main__":
    sys.exit(main())


