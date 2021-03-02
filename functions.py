import os, glob, sys

# try:
#     from WBT.whitebox_tools import WhiteboxTools
# except ImportError:
#     print ("WBT python package is required!")
#     sys.exit ( -1 )

try:
    import numpy as np
except ImportError:
    print ("Numpy python package is required!")
    sys.exit ( -1 )

try:
  import gdal
except ImportError:
    print ("GDAL python package is required!")
    sys.exit ( -1 )


GDAL_OPTS = [
    "COMPRESS=LZW",
    "INTERLEAVE=PIXEL",
    "TILED=YES",
    "SPARSE_OK=TRUE",
    "BIGTIFF=YES" ]


def read_image_header(fpath):
    print('\n\n\n')
    print (gdal.Info(fpath))


def check_file_exists(directory):
    return os.path.isfile(directory)


def fetch_files(directory, extension):
    targetPattern0 = r"C:\Test\*.txt"
    targetPattern = directory + '*.' + extension
    res = glob.glob(targetPattern)
    return res


def process_metadata ( fname ):
    """A function to extract the relelvant metadata from the
    USGS control file. Returns dicionaries with LMAX, LMIN,
    QCAL_LMIN and QCAL_LMAX for each of the bands of interest."""

    fp = open( fname, 'r')
    lmax = {}
    lmin = {}
    qc_lmax = {}
    qc_lmin = {}
    gain = {}
    bias = {}

    for line in fp: # 
      # Check for LMAX and LMIN strings
      # Note that parse logic is identical to the first case
      # This version of the code works, but is rather inelegant!
      if ( line.find ("RADIANCE_MULT_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              gain[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("RADIANCE_ADD_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              bias[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("QUANTIZE_CAL_MAX_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[4]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              qc_lmax[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("QUANTIZE_CAL_MIN_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[4]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              qc_lmin[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("RADIANCE_MAXIMUM_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              lmax[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("RADIANCE_MINIMUM_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [1,2,3,4,5,7]: # Is this one of the bands we want?
              lmin[the_band] = float ( s[-1] ) # Get constant as float

    return ( bias, gain, lmax, lmin, qc_lmax, qc_lmin )

def apply_reflectance(band, gain, bias):
    for i in range(0, 5):
        # The bands are indexed 1, 2, 3... but the mult_term list is indexed 0, 1, 2...
        band_num = i + 1
        print("Transforming band {}...".format(band_num))
        inFile = "band{}.tif".format(
            band_num)
        # This is where the DN-to-reflectance transform equation happens.
        # It creates two temporary rasters that are continually over-written.
        wbt.multiply(inFile, mult_term[i], "tmp1.tif")
        wbt.add("tmp1.tif", add_term[i], "tmp2.tif")
        # The final transformed raster is called bandX_reflect.tif
        wbt.divide("tmp2.tif", sin(sun_elevation),
                   "band{}_reflect.tif".format(band_num))












