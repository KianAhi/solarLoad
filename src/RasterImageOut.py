from osgeo import gdal, osr
import matplotlib.pyplot as plt

class RasterImage:
    def __init__(self, geoTiff_path):
        """initializes an object from a geoTiff (.tif) file
        
        Args:
            geoTiff_path (Path): path to an existing geoTiff file
        """
        
        self.dataset = gdal.Open(geoTiff_path, gdal.GA_ReadOnly)
        self.spatial_ref = self.dataset.GetSpatialRef()
        self.raster_x_size = self.dataset.RasterXSize
        self.raster_y_size = self.dataset.RasterYSize
        
    def getImageAsArray(self, band=1, pyplot_out=False):
        """return an image array for further use e.g. plotting via plt.imshow(imgArray) [!don't forget plt.show() after that!]
        
        Args:
            band (int, optional): which band to take the data from (only useful in multiband data). Defaults to 1.
            pyplot_out (bool, optional): if you want to spawn a pyplot plot set to True. WILL NOT RETURN AN IMAGE ARRAY!
        
        Returns:
            imgArray: array of pixels
        """
        band = self.dataset.GetRasterBand(band)
        imgArray = band.ReadAsArray()
        
        if pyplot_out:
            import matplotlib.pyplot as plt
            
            plt.imshow(imgArray)
            plt.show()
        
        else:
            return imgArray
    
    def getCoordinateSystem(self):
        spatial_reference = osr.SpatialReference(wkt=self.dataset.GetProjection())
        
        return spatial_reference.GetAttrValue('geogcs')

if __name__ == '__main__':
    geoTiff = RasterImage('../data/raster/PVOUT.tif')
    geoTiff_image = geoTiff.getImageAsArray(pyplot_out=True)
    geoTiff_coordinate_system = geoTiff.getCoordinateSystem()
    print("coordinate system: %s" % geoTiff_coordinate_system)