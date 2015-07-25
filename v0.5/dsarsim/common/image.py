# 	Copyright 2015 Adamo Ferro
#
#	This file is part of dSARsim.
#
#   dSARsim is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
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


import sys,numpy,scipy.ndimage
from osgeo import gdal


class image:
    """ Support class used to store image data. It provides GeoTIFF I/O methods
    based on gdal and some image transformation methods: rotate, crop and resize """
    

    def __init__(self,size=(0,0),ps=(0,0),value=None,nodatav=-9999):
        
        gdal.UseExceptions()
        
        self.matrix_type=numpy.float32
        self.file_type=gdal.GDT_Float32

        self.image=None
        self.size=size
        self.pixel_size=ps
        self.nodatav=nodatav

        if value is not None:
            self.empty(value)            

        
    def getImageInfo(self):
        return (self.size,self.pixel_size)

                
    def empty(self,value=0):
        self.image=numpy.ones(self.size,dtype=self.matrix_type)*value

        
    def rotate(self,angle,rshp,nodatav):
        #~ angle > 0 means counterclockwise rotation
        try:
            tmp_img=scipy.ndimage.interpolation.rotate(self.image, angle, axes=(1, 0), reshape=rshp, output=None, order=3, mode='constant', cval=nodatav, prefilter=True)
        except:
            return -1
        self.image=tmp_img
        self.size=self.image.shape
        return 0
        
        
    def crop(self,tl_corner,size):
        try:
            tmp_img=self.image[tl_corner[0]:tl_corner[0]+size[0],tl_corner[1]:tl_corner[1]+size[1]]
        except:
            return -1
        self.image=tmp_img
        self.size=self.image.shape
        return 0


    def resize(self,scale_factors,order):
        try:
            tmp_img=scipy.ndimage.zoom(self.image,scale_factors,order=order)
        except:
            return -1
        self.image=tmp_img
        self.pixel_size=[self.pixel_size[i_psize]/scale_factors[i_psize] for i_psize in range(0,2)]
        self.size=self.image.shape
        return 0
        

    def write(self,filename):
        if self.size[0]==0 or self.size[1]==0:
            return -1
      
        try:
            driver = gdal.GetDriverByName('GTiff')

            ds = driver.Create(filename,self.size[1],self.size[0],1,self.file_type)

            ds.SetGeoTransform((
                0,                      # 0: x_min
                self.pixel_size[1],     # 1: pixel_size_x
                0,                      # 2: 0
                self.size[0],           # 3: y_max
                0,                      # 4: 0
                -self.pixel_size[0]))   # 5: -pixel_size_y

            ds.GetRasterBand(1).WriteArray(self.image)
            ds.FlushCache()  # write to disk.
        except:
            return -1
        return 0

        
    def read(self,filename):
        try:
            ds = gdal.Open(filename)
            b = ds.GetRasterBand(1)
            self.image = b.ReadAsArray()
            self.size = (ds.RasterYSize,ds.RasterXSize)
            gt = ds.GetGeoTransform()
            self.pixel_size = (-gt[5],gt[1])
        except:
            return -1
        return 0
