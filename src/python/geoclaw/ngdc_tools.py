
"""

Tools to download data from NGDC.

"""


def etopo1_download(xlimits, ylimits, dx=0.0166666666667, dy=None, \
        output_dir='.', file_name='etopo1.tt3', force=False, verbose=True):

    """
    Create a url to download etopo1 topography from NGDC and
    save as a topo_type 3 file.  Uses the database described at
        http://www.ngdc.noaa.gov/mgg/global/global.html

    :Inputs:

    - *xlimits*: tuple (x1, x2) limits in longitude
      Must either have -180 <= x1 < x2 <= 180
           or 180 <= x1 < x2 <= 360
      To download topo for a region spanning longitude 180, you must
      download two separate files, one on each side.

    - *ylimits*: tuple (y1, y2) limits in latitude
      Must have -90 <= y1 < y2 <= 90.

    - *dx*: resolution in x, default is 1./60. degree = 1 arcminute.
    - *dy*: resolution in y, default is dy = dx.
    - *output_dir*: directory to store file, default is '.'
    - *file_name*: name of file, default is 'etopo1.tt3'.
    - *force*: if True, download even if the file already exists.
    - *verbose*: if True, print info from clawpack.geoclaw.util.get_remote_file

    Note: New NGDC format gives cell-registered values, so shift the 
    values `xllcorner` and `yllcorner` to the specified corner.

    **To do:** Check whether it is possible to specify grid-registered
    values as implied at http://www.ngdc.noaa.gov/mgg/global/global.html

    The `nodata_value` line expected by GeoClaw is now missing,
    so add this in too.
    """

    from clawpack.geoclaw import util
    import os

    format = '&format=aaigrid'   # topo_type 3

    if dy is None:
        dy = dx

    x1,x2 = xlimits
    y1,y2 = ylimits

    if (x1>=180) and (x1<x2) and (x2<=360):
        shift_by_360 = True
        x1 = x1 - 360.
        x2 = x2 - 360.
    else:
        shift_by_360 = False

    if (x1<-180) or (x1>=x2) or (x2>180):
        raise ValueError("Require -180 <= x1 < x2 <= 180 or 180 <= x1 < x2 <=360")
    if (y1<-90) or (y1>=y2) or (y2>90):
        raise ValueError("Require -90 <= y1 < y2 <= 90")

    bbox = '&bbox=%1.4f,%1.4f,%1.4f,%1.4f' % (x1,y1,x2,y2)
    res = '&resx=%1.12f&resy=%1.12f' % (dx,dy)
    url = 'http://maps.ngdc.noaa.gov/mapviewer-support/wcs-proxy/wcs.groovy' \
            + '?request=getcoverage&version=1.0.0&service=wcs' \
            + '&coverage=etopo1&CRS=EPSG:4326' \
            + format + bbox + res

    util.get_remote_file(url, output_dir=output_dir, file_name=file_name, \
                    verbose=verbose,force=force)

    if shift_by_360:
        x1 = x1 + 360.

    path = os.path.join(output_dir,file_name)
    lines = open(path).readlines()
    if lines[2].split()[0] != 'xllcorner':
        print "*** Error downloading, check the file!"
    else:
        lines[2] = 'xllcorner    %1.12f\n' % x1
        lines[3] = 'yllcorner    %1.12f\n' % y1
        lines = lines[:5] + ['nodata_value    -99999\n'] + lines[5:]
        f = open(path,'w')
        f.writelines(lines)
        f.close()
        print "Shifted xllcorner and yllcorner to cell centers"
        print "   and added nodata_value line"
    print "File: ",path

