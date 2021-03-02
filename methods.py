import os
import time
import glob
import re
import tarfile
import utm
import numpy
import rasterio
import multiprocessing
import matplotlib.pyplot as plt

# print ('\n++++ Requirement: ++++')
# print ('GDAL version', gdal.VersionInfo())
# print ('Rasterio version', rasterio.__version__)

from configparser import ConfigParser
from math import radians, sin

from functions import *

setting = ConfigParser() 
setting.read('config.ini')

def get_time():
    return time.time()

def read_image_header(fpath):
    print (gdal.Info(fpath))

def check_file_exists(directory):
    return os.path.exists(directory)

def list_image_files(target, directory):
    if check_file_exists(directory):
        if target == '-sat':
            directory += '//*.tar.gz'
            satellite_images = glob.glob(directory)
            if len(satellite_images):
                return satellite_images
            else:
                raise Exception(
                    "Directory doesn't contain any satellite image!")

        elif target == '-dem':
            print('1')
    else:
        raise Exception("Directory doesn't exist!")

def list_files(directory, expression_str):
    content = tarfile.open(directory)
    file_names = content.getnames()
    if len(file_names):
        temp = ''
        files = []
        for name in file_names:
            expression = re.compile(expression_str)
            if expression.search(name):
                content.extract(name, path=os.path.dirname(directory))
                files.append(name)
        content.close()
        return files
    else:
        content.close()
        raise Exception("Folder %s is empty" % directory.split('//')[-1])

def fetch_bands(directory, bands:list):
    content = tarfile.open(directory)
    file_names = content.getnames()
    if len(file_names):
        expression = re.compile(".*_(B1|B2|B3|B4|B5|B6|B7|B8)\.TIF")
        files = []
        for name in file_names:
            if expression.search(name) and name.split('.')[0][-2:] in bands:
                content.extract(name, path=os.path.dirname(directory))
                files.append(name)
        content.close()
        return files
    else:
        content.close()
        raise Exception("Folder %s is empty" % directory.split('//')[-1])

def read_band(path:str):
    """
    This function read band and return a numpy ndarray data
    \nInputs=> A string path to .tif file of band.
    \nOutputs=> A Numpy ndarray data + metadata of band
    """
    if type(path) != str:
        raise Exception("Error in input data. Argument <path> must be a string.")
    else:
        if check_file_exists(path):
            with rasterio.open(path) as src:
                return (src.read(1), src.meta)
        else:
            raise Exception("Image not found!")
            

def calculate_ndwi2(image:str, options={'status': False, 'modified': False, 'BBX': False}):
    """
    This function calculates NDWI (Normalized Difference Water Index).
    There are three options: (1) Calculating modified version of NDWI by
    setting "options:modified" to "True" (2) Calculating some additional
    information by setting "options:status" to "True" (3) Fast calculation
    by reducing area to the BBX by setting "options:BBx" to "True".
    \nInputs=> A sting path to the tar.gz. file of bands
    \nOutputs=> Calculated (M)NDWI + metadata + some additional information
    """
    file_name = os.path.split(image)[1].replace('.tar.gz', '')
    print('Calculating (M)NDWI for %s ...' % file_name)
    if type(image) != str:
        raise Exception("Error in input data. Argument <image> must be a string.")
    else:
        if check_file_exists(image):
            if options['modified']:
                bands = fetch_bands(image, ['B2', 'B5'])
            else:
                bands = fetch_bands(image, ['B2', 'B4'])
            band0_dir = os.path.dirname(image) + '\\' + bands[0]
            band1_dir = os.path.dirname(image) + '\\' + bands[1]

            band0, metadata0 = read_band(band0_dir)
            band1, metadata1 = read_band(band1_dir)
            
            if options['BBX']:
                bound0 = get_pixel_bound(band0_dir)
                bound1 = get_pixel_bound(band0_dir)
                band0 = band0 [bound0[2]:bound0[3], bound0[0]:bound0[1]]
                band1 = band1 [bound1[2]:bound1[3], bound1[0]:bound1[1]]

                fig, ax = plt.subplots(figsize=(4,4))
                fig.subplots_adjust(0,0,1,1)
                ax.axis("off")
                ax.imshow(band0)
                plt.savefig(
                    'b2-bbx.png',
                    format='png',
                    dpi=250,
                    transparent=True)
                plt.close()

                fig, ax = plt.subplots(figsize=(4,4))
                fig.subplots_adjust(0,0,1,1)
                ax.axis("off")
                ax.imshow(band1)
                plt.savefig(
                    'b5-bbx.png',
                    format='png',
                    dpi=250,
                    transparent=True)
                plt.close()

                # metadata0 = ?
                # metadata1 = ?

            os.remove(band0_dir)
            os.remove(band1_dir)            

            band0_size = band0.size
            band1_size = band1.size
            if not band0_size or not band1_size:
                raise Exception("Band is in zero size!!")
            elif band0_size != band1_size:
                raise Exception("Bands should be in same size!")
            else:
                try:
                    results = {}

                    numpy.seterr(divide='ignore', invalid='ignore')
                    a1 = band0.astype(float) - band1.astype(float)
                    a2 = band0.astype(float) + band1.astype(float)
                    ndwi = a1 / a2

                    
                    if options['modified'] == True:
                        export_name = 'Modified_NDWI__' + file_name
                    else:
                        export_name = 'NDWI__' + file_name
                        
                    results['metadata'] = metadata0
                    results['name'] = export_name
                    results['matrix'] = ndwi

                    if options['status']:
                        results['status'] = {}
                        results['status']['min'] = numpy.nanmin(ndwi)
                        results['status']['max'] = numpy.nanmax(ndwi)
                        results['status']['mean'] = numpy.nanmean(ndwi)
                        results['status']['median'] = numpy.nanmedian(ndwi)
                    
                    print("Done successfully -> %s\n" % file_name)

                    return results
                except:
                    raise Exception("Unknown error in calculating NDWI!")
        else:
            raise Exception("Image not found!")

def get_pixel_bound(image:str):
    # https://gis.stackexchange.com/questions/299787/finding-pixel-location-in-raster-using-coordinates
    # https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel
    # https://gis.stackexchange.com/questions/129847/obtain-coordinates-and-corresponding-pixel-values-from-geotiff-using-python-gdal
    # https://stackoverflow.com/questions/60127026/python-how-do-i-get-the-pixel-values-from-an-geotiff-map-by-coordinate
    # https://github.com/Turbo87/utm
    """
    This function returns pixels of interested area which has been
    defined by an array of tuples.
    \nInputs=> A sting path to the .tif file
    \nOutputs=> An array of pixel coordinate of BBX
    """
    if type(image) != str:
        raise Exception("Error in input data. Argument <image> must be a string.")
    else:
        if check_file_exists(image):
            bbx = setting.get('constants', 'BBX').split(',')
            if len(bbx) == 4:
                try: 
                    dataset = rasterio.open(image)
                    
                    SW = utm.from_latlon(float(bbx[1]), float(bbx[0]))
                    NE = utm.from_latlon(float(bbx[3]), float(bbx[2]))

                    py0, px0 = dataset.index(SW[0], SW[1])
                    py1, px1 = dataset.index(NE[0], NE[1])
                    
                    return [px0, px1, py1, py0]

                except Exception as e:
                    print('Error calculating pixel coordinate\n' + str(e))

            else:
                raise Exception("Check BBX parameter in config.ini. It should have 4 parts")    
        else:
            raise Exception("Image not found!")

def export_to_tiff(directory, matrix, metadata):
    """
    This function get Numpy ndarray and related metadata to create
    a .tif file as the results of process.
    \nInputs=> A directory for exported .tif file, Numpy and meta
    \nOutputs=> A path to result .tif file
    """
    file_name = os.path.split(directory)[1]
    kwargs = metadata
    kwargs.update(dtype=rasterio.float32, count = 1)
    try:
        with rasterio.open(directory, 'w', **kwargs) as dst:
            dst.write_band(1, matrix.astype(rasterio.float32))
            print('\n File was created successfully.\n%s' % file_name)
    except:
        raise Exception("Error in exporting dataset to .tif!")

def load_meta(fname):
    """A function to extract the relelvant metadata from the
    USGS control file. Returns dicionaries with LMAX, LMIN,
    QCAL_LMIN and QCAL_LMAX for each of the bands of interest."""

    fp = open(fname, 'r')
    lmax = {}
    lmin = {}
    qc_lmax = {}
    qc_lmin = {}
    gain = {}
    bias = {}

    for line in fp:
        # Check for LMAX and LMIN strings
        # Note that parse logic is identical to the first case
        # This version of the code works, but is rather inelegant!
        if (line.find("RADIANCE_MULT_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[3])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                gain[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("RADIANCE_ADD_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[3])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                bias[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("QUANTIZE_CAL_MAX_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[4])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                qc_lmax[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("QUANTIZE_CAL_MIN_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[4])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                qc_lmin[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("RADIANCE_MAXIMUM_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[3])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                lmax[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("RADIANCE_MINIMUM_BAND") >= 0):
            s = line.split("=")  # Split by equal sign
            the_band = int(s[0].split("_")[3])  # Band number as integer
            if the_band in [1, 2, 3, 4, 5, 7]:  # Is this one of the bands we want?
                lmin[the_band] = float(s[-1])  # Get constant as float
        elif (line.find("SUN_ELEVATION") >= 0):
            s = line.split("=")
            sun_elevation = radians(float(s[1].strip()))

    return (bias, gain, lmax, lmin, qc_lmax, qc_lmin)
    # return (bias, gain, sun_elevation)

