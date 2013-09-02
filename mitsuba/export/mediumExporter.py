# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


            #Bytes 1-3    VOL in ASCII
            #Byte 4        File format version number (currently 3)
            #Bytes 5-8     Encoding identifier (32-bit integer).The following choices are available:
            #
            #            1. Dense float32-based representation
            #            2. Dense float16-based representation (currently not supported by this
            #            implementation)
            #            3. Dense uint8-based representation (The range 0..255 will be mapped
            #            to 0..1)
            #            4. Dense quantized directions. The directions are stored in spherical coordinates
            #            with a total storage cost of 16 bit per entry.
            #            
            #Bytes 9-12     Number of cells along the X axis (32 bit integer)
            #Bytes 13-16    Number of cells along the Y axis (32 bit integer)
            #Bytes 17-20    Number of cells along the Z axis (32 bit integer)
            #Bytes 21-24    Number of channels (32 bit integer, supported values: 1 or 3)
            #Bytes 25-48    Axis-aligned bounding box of the data stored in single precision (order:
            #               xmin, ymin, zmin, xmax, ymax, zmax)
            #Bytes 49-*     Binary data of the volume stored in the specified encoding. The data
            #               are ordered so that the following C-style indexing operationmakes sense
            #               after the file has been mapped into memory:
            #               data[((zpos*yres + ypos)*xres + xpos)*channels + chan]
            #               where (xpos, ypos, zpos, chan) denotes the lookup location.
            #
            #    Example : 
            #    56 4F 4C 33    01 00 00 00    10 00 00 00    10 00 00 00      ||  VOL3 1 3 3
            #    10 00 00 00    01 00 00 00    FF FF FF FF    FF FF FF FF      ||  3 1 -1 -1
            #    FF FF FF FF    01 00 00 00    01 00 00 00    01 00 00 00      ||  -1 1 1 1  
            #    -------------------------------------------------------------
            #     THE REST IS THE CONTENT  3*3*3 =  27 times
            #

import bpy
import struct

def smoke_convertion(report , filename , obj):
    # try if it has or not the smoke part 
    report({'INFO'}, 'OBJ = %s ' %str(obj))
    try :
        if obj.modifiers['Smoke'].type != 'SMOKE':
            report({'ERROR'}, 'Could not find the Smoke modifier (1)')
            return 0
        else :            
            report({'INFO'}, 'OBJ = %s ' %str(obj))
            smoke_DS = obj.modifiers['Smoke'].domain_settings
    except:
        report({'ERROR'}, 'Could not find the Smoke modifier (2)')
        return 0
        
    #mfile = open('voxelBIT.vol','wb')    
    try :
        mfile = open(filename,'wb')
    except:
        report({'ERROR'}, 'Cannot open file : %s' %filename)
        return 0
        
    int32format = "i"
    float32format = 'f' 
    
    #try:        
    mfile.write(bytes('VOL\x03', 'ASCII'))    
    data = struct.pack(int32format , 1)
    mfile.write(data)

    xx,yy,zz = smoke_DS.domain_resolution    
    data = struct.pack(int32format , xx)
    mfile.write(data)
    data = struct.pack(int32format , yy)
    mfile.write(data)
    data = struct.pack(int32format , zz)
    mfile.write(data)        
    
    data = struct.pack(int32format , 1)
    mfile.write(data)
    
    xmin=xmax=obj.data.vertices[0].co.x
    ymin=ymax=obj.data.vertices[0].co.y
    zmin=zmax=obj.data.vertices[0].co.z
    #TODO: a function for this
    for i in obj.data.vertices :                        
        if i.co.x > xmax :
            xmax = i.co.x
        elif i.co.x < xmin :
            xmin = i.co.x
        
        if i.co.y > ymax :
            ymax = i.co.y
        elif i.co.y < ymin :
            ymin = i.co.y
            
        if i.co.z > zmax :
            zmax = i.co.z
        elif i.co.z < zmin :
            zmin = i.co.z    

    data = struct.pack(float32format, xmin)
    mfile.write(data)
    data = struct.pack(float32format, ymin)
    mfile.write(data)
    data = struct.pack(float32format, zmin)
    mfile.write(data)        
    data = struct.pack(float32format, xmax)
    mfile.write(data)
    data = struct.pack(float32format, ymax)
    mfile.write(data)
    data = struct.pack(float32format, zmax)
    mfile.write(data)
    #except:
    #    report({'ERROR'}, "Cannot write header of the file %s" %filename)
    #    return 0
    
    try :   
        #leng = len(smoke_DS.density) 
        for i in smoke_DS.density :
            data = struct.pack(float32format , i)            
            mfile.write(data)
    except :
        report({'ERROR'}, "Cannot write header of the file %s" %filename)
        return 0
    try :        
        mfile.close()
    except :
        report({'ERROR'}, "Cannot close the file %s" %filename)
        return 0
    return 1