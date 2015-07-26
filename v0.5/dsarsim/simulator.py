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


import math, numpy
import sys,copy

from .common.image import image


class simulator:
    """ Base class for pseudo-SAR simulation. Note: the actual simulation is carried out in a function that is not
    a method of the class. This choice is only due to some limitations of the multiprocessing library, which
    seems not to be able to use the function map with methods belonging to the same class of the calling function. """
        
    def __init__(self,ia=30,aa=0,d='w',img=None,st=0.25,lt=0.25,opsize=(0,0),sp=1,debug_mode=False,rb=False):

        self.debug_mode=debug_mode

        self.n_hist_bins=100            #~ TODO: set by user or calculated automatically?
        self.n_subprocesses=sp
        self.rotate_back=rb

        self.input_image=None
        self.input_working_image=None
        self.output_image=None
        self.isize=None
        self.ipsize=None
        self.user_opsize=opsize
        
        self.row_sim_parameters=row_sim_parameters()        #~ simulation parameters to be used later on
        self.row_sim_parameters.shadow_tol=st
        
        self.layover_tol=lt
        self.direction=None
        self.aa=None
        self.aa_rad=None
        self.setAngles(ia,aa,d)
        if img is not None:
            self.setInputImage(img)


    def setAngles(self,ia,aa,d):
        """ Sets the viewing parameters of the pseudo-simulation. If such parameters are different 
        from those already stored in the class, it resets the current calculated output image (if any) """

        if self.direction!=d or self.aa!=aa or self.row_sim_parameters.ia!=ia:
            self.direction=d
            self.aa=aa
            self.aa_rad=aa*math.pi/180.
            self.row_sim_parameters.setIA(ia)
            self.resetOutputImage()


    def setInputImage(self,img):
        """ Sets the input DTM/DSM image and calculates some parameters based on the image characteristics.
        A working copy of the input image is created and will be used later on for the simulation. """
        
        self.resetOutputImage()
        self.input_image=img
        self.input_working_image=copy.deepcopy(img)
        
        rsp=self.row_sim_parameters
        
        self.isize, self.ipsize=self.input_image.getImageInfo()
        rsp.iwpsize=self.ipsize
        rsp.owpsize=(rsp.iwpsize[0],rsp.iwpsize[1]*rsp.sin_ia)
        
        self._updateWorkingImageSizes(self.isize)

        rsp.s_angular_factor=rsp.iwpsize[1]/rsp.tan_ia
        l_angular_factor=rsp.iwpsize[1]*rsp.tan_ia
        rsp.d_h_lo_min=l_angular_factor*(1-self.layover_tol)            
        rsp.nodatav=img.nodatav

        
    def resetOutputImage(self):
        self.output_image=None
    

    def _updateWorkingImageSizes(self,ws):
        rsp=self.row_sim_parameters
        rsp.iwsize=ws
        rsp.owsize=ws


    def calculateOutputImageOffset(self):
        """ Calculates the X offset in pixels that makes the pseudo-simulation "centered" on the areas
            with the most frequent height values """
            
        
        if self.output_image is None:
        
            if self.debug_mode:
                print("INFO: Calculating working output image offset...")
            
            rsp=self.row_sim_parameters
            
            
            #~ retrieves the most frequent height value into the DTM/DSM and uses it as reference. The nodata value is not taken into account
            hist,bin_edges=numpy.histogram(self.input_working_image.image[self.input_working_image.image!=rsp.nodatav],self.n_hist_bins)
            bin_max=numpy.argmax(hist)
            h_ref=(bin_edges[bin_max]+bin_edges[bin_max+1])/2.
            d=h_ref*rsp.cos_ia
            x_offset=-int(round(d/rsp.owpsize[1]))
            rsp.output_working_image_offset=x_offset
            
            if self.debug_mode:
                print("INFO: Reference height [m]                      = "+str(h_ref))
                print("INFO: Output image offset [pixels]              = "+str(rsp.output_working_image_offset))
                print("INFO: Working output slant range pixel size [m] = "+str(rsp.owpsize[1]))

 
    def simulate(self):
        """ Applies a rotation to the input working image, if necessary; allocates the output image and prepares
        the input data to be processed by the actual pseudo-simulation external function, which is called through
        multiprocessing.map. The results are then recomposed to form the output image. If the user manually set
        azimuth and/or range spacing, the output image is scaled accordingly.
        Rotations are used to simulate different aspect angles and/or viewing directions. This avoids to take 
        these effects into account in the actual simulation code, which is kept as simple as possible. """
        
        if self.input_working_image is not None:
        
            rsp=self.row_sim_parameters
            
            if self.aa!=0 or self.direction!='w':
                aa_tmp=(0 if self.direction=='w' else -180)+self.aa
                if self.debug_mode:
                    print("INFO: Rotating input DEM by "+str(aa_tmp)+" degrees to simulate aspect angle+direction...")
                if self.input_working_image.rotate(aa_tmp,True,rsp.nodatav)==0:
                    self._updateWorkingImageSizes(self.input_working_image.size)
                else:
                    print("WARNING: Problem during DEM rotation. Using not rotated DEM, and thus aspect angle = 0 degrees.")
                        

            self.calculateOutputImageOffset()

            if self.debug_mode:
                print("INFO: Creating output working image...")         
            self.output_image=image(rsp.owsize,rsp.owpsize,0)
            
            
            if self.debug_mode:
                print("INFO: Preparing input data for multiprocessing...")              
            map_list=list()
            for iY in range(0,rsp.iwsize[0]):
                map_list.append((self.input_working_image.image[iY],rsp))


            self.multiprocessing_enabled=True
            try:
                from multiprocessing import Pool
            except:
                self.multiprocessing_enabled=False


            results=None
            if self.multiprocessing_enabled:
                if self.debug_mode:
                    print("INFO: Simulating with "+str(self.n_subprocesses)+" subprocesses...")
                pool=Pool(self.n_subprocesses)
                results=pool.map(sim_row,map_list)
            else:
                print("WARNING: Multiprocessing not possible on this machine. Simulating with 1 process.")
                results=list(map(sim_row,map_list))
            
            if self.debug_mode:
                print("INFO: Reassembling results into one single image...")            
            for iY in range(0,rsp.iwsize[0]):
                self.output_image.image[iY]=numpy.array(results[iY])


            if self.user_opsize[0]!=0 or self.user_opsize[1]!=0:
                scale_factors=[rsp.owpsize[i_psize]/self.user_opsize[i_psize] if self.user_opsize[i_psize]!=0 else 1 for i_psize in range(0,2)]

                if self.debug_mode:
                    print("INFO: Resizing output image in order to simulate user defined pixel spacing.")
                if self.output_image.resize(scale_factors,0)!=0:
                    print("ERROR: Problem during image resizing. Using not resized image.")


            if self.direction=='e':
                if self.debug_mode:
                    print("INFO: Rotating by 180 degrees to restore North position...")
                if(self.output_image.rotate(180,True,0,0)!=0):
                    print("ERROR: Problem during output image rotation. Using not rotated output.")

                    
            if self.rotate_back and self.aa!=0:
                if self.debug_mode:
                    print("INFO: Rotating back output image...")                
                if(self.output_image.rotate(-self.aa,True,0,0)!=0):
                    print("ERROR: Problem during output image rotation. Using not rotated output.")
                osize_tmp=self.output_image.getImageInfo()[0]
                tl_corner=(int(osize_tmp[0]/2)-int(self.isize[0]/2),int(osize_tmp[1]/2)-int(self.isize[1]/2))
                if self.debug_mode:
                    print("INFO: Cropping output image...")                  
                if self.output_image.crop(tl_corner,self.isize)!=0:
                    print("ERROR: Problem during output image cropping. Using not cropped output.")
                    
            return 0
        else:
            print("ERROR: No input image has been selected.")
            return -1

    
    def getOutputImage(self):
        return self.output_image
        


class row_sim_parameters:
    """ Support class used to pass parameters from the simulator.simulate function to the sim_row function. """
    
    def __init__(self,ia=0,iws=(0,0),iwps=(0,0),ows=(0,0),owps=(0,0),dv=0,io=0,saf=0,st=0,dl=0):
        
        self.ia=None
        self.ia_rad=None
        self.tan_ia=None
        self.cos_ia=None
        self.sin_ia=None
        
        self.iwsize=iws
        self.iwpsize=iwps
        self.owsize=ows
        self.owpsize=owps
        self.nodatav=dv
        self.output_working_image_offset=io

        self.s_angular_factor=saf
        self.shadow_tol=st
        self.d_h_lo_min=dl
        
        self.setIA(ia)
        

    def setIA(self,ia):
        if ia!=self.ia:
            self.ia, self.ia_rad=ia, ia*math.pi/180.
            self.tan_ia=math.tan(self.ia_rad)
            self.sin_ia=math.sin(self.ia_rad)
            self.cos_ia=math.cos(self.ia_rad)



def sim_row(row_data):
    """ Performs the pseudo-simulation of one single row of the input image.
    The simulation is always carried out considering the sensor viewing from
    left to right. """
    
    row=row_data[0]
    rsp=row_data[1]

    #~ set support arrays to min/max possible value for convenience
    row_sh=[numpy.finfo('d').min for iX in range(0,rsp.iwsize[1])]
    row_d=[numpy.finfo('d').max for iX in range(0,rsp.iwsize[1])]
    
    #~ the output array is set to 0
    row_result=numpy.zeros((rsp.owsize[1],),dtype=numpy.float32)

    h_prev=numpy.finfo('d').max
    
    #~ for each column of the input row...
    for iX in range(0,rsp.iwsize[1]):
        h=row[iX]
        if h != rsp.nodatav:
            if row_sh[iX]<numpy.finfo('d').max:   #~ position is not shadowed
                d=h*rsp.cos_ia      #~ position of the current point in the slant range image [m]

                #~ actual position on the output image [pixels], that is also the beginning of a possible layover area
                x_start_layover=int(round(iX*rsp.iwpsize[1]*rsp.sin_ia/rsp.owpsize[1]-d/rsp.owpsize[1]-rsp.output_working_image_offset))
                row_d[iX]=x_start_layover

                #~ update output image at the corrisponding position (if contained in the image itself)
                if x_start_layover>=0 and x_start_layover<rsp.owsize[1]:
                    row_result[x_start_layover]+=1
                else:
                    if x_start_layover<rsp.owsize[1]:
                        x_start_layover=0
                    else:
                        x_start_layover=-1
                
                #~ compares the heights of all the pixels on the right of the current one to the current height
                #~ to determine whether those pixels are shadowed. The check stops when one position is not shadowed
                iSh=iX+1
                shadowed=True
                while iSh<rsp.iwsize[1] and shadowed==True:
                    h_sh=row[iSh]
                    d_h=h-h_sh
                    d_h_min=rsp.s_angular_factor*(iSh-iX-rsp.shadow_tol)
                    if d_h>=d_h_min:
                        row_sh[iSh]=numpy.finfo('d').max        # position iSh (ground range, on input DTM/DSM) is shadowed
                        iSh+=1
                    else:
                        shadowed=False
                        row_sh[iSh]=h-d_h_min     #~ the slope/facade is anyway shadowed until this height (used in layover calculations)
                
                #~ check whether the current position generates a layover area
                if x_start_layover>=0:
                    iLo=iX-1
                    layovered=True
                    if iLo>=0:
                        h_lo_sh=row_sh[iX]
                        
                        h_lo_prev=row[iLo]
                        if h_lo_sh>h_lo_prev:   #~ cut layover: part of the slope/facade is shadowed
                            d_h=h-h_lo_sh
                            if d_h>=rsp.d_h_lo_min:
                                d_end_layover=h_lo_sh*rsp.cos_ia
                                x_end_layover=int(round((iX*rsp.iwpsize[1]*rsp.sin_ia-d_end_layover)/rsp.owpsize[1]))-rsp.output_working_image_offset
                                if x_end_layover>=x_start_layover:
                                    if x_end_layover>=rsp.owsize[1]:
                                        x_end_layover=rsp.owsize[1]-2
                                    row_result[x_start_layover:x_end_layover+1]+=1          #~ update output image
                                    
                        else:                   #~ full layover: the whole slope/facade generates layover
                            d_h=h-h_lo_prev
                            if d_h>=rsp.d_h_lo_min and row_d[iLo]>=x_start_layover and row_d[iLo]!=numpy.finfo('d').max:
                                x_end_layover=row_d[iLo]
                                if x_end_layover>=rsp.owsize[1]:
                                    x_end_layover=rsp.owsize[1]-2
                                row_result[x_start_layover:x_end_layover+1]+=1              #~ update output image
            h_prev=h
        else:
            h_prev=numpy.finfo('d').max

    return row_result
