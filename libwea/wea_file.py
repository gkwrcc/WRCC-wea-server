#
# wea_file
#

import sys
import numpy as np
from numpy import array, zeros
from utils import days_in_month, yearmonth_from_filename


class WeaFile(object):
    """
    This class reads a single .wea file and returns as a numpy.array.
    """

    def __init__(self, filename, readdata=True):
        self.filename = filename
        self.header = {}
        self.data = None
        if readdata:
            self.read_data()

    def _open(self):
        self.fd = open(self.filename, 'rb')

    def __repr__(self):
        return "<WeaFile %s>" % self.filename

    def yearmonth(self):
        return yearmonth_from_filename(self.filename)

    def _do_unpack(self, fmt, nbytes):
        """
        This is a wrapper function that calls struct.unpack.
        Unpack from file 'fd', using format string 'fmt',
        size 'nbytes'. The first character of 'fmt' can be '<' for
        little-endian or '>' for big-endian.
        See http://docs.python.org/lib/module-struct.html
        """
        import struct
        return struct.unpack(fmt, self.fd.read(nbytes))

    def _get_short(self):
        # unpack returns a tuple, so take first value
        return self._do_unpack('<h', 2)[0]

    def read_header(self):
        """
        Read the header of a .wea file and save in self.header.
        """
        if self.header:
            return self.header

        if not hasattr(self, 'fd'):
            self._open()
        tr = self._get_short()  # Always 1 ?
        # pr = float Total minutes in this file
        # oi = short Observation Interval (in minutes)
        # ne = short Number of Elements
        # rgt = short Rain Gauge Type
        # wsh = short Wind Speed Height
        pr, oi, ne, rgt, wsh = self._do_unpack("f4h", 4 + 2 * 4)

        # BUG FIX. Recalculate pr manually
        year, month = self.yearmonth()
        pr = days_in_month(month, year) * 24 * 60

        # Read 8 shorts (unused placeholders)
        self._do_unpack("8h", 2 * 8)

        # Read pc based on ne
        # Read 3 1-byte chars per element
        pc = ''.join(self._do_unpack("%dc" % ne * 3, ne * 3))
        # Put pcodes in a tuple
        pcodes = []
        for i in range(0, len(pc), 3):
            pcodes.append(pc[i:i + 3])
        pcodes = tuple(pcodes)

        # Set observation factors
        if oi == 1440: fac1 = 1;  fac2 = 24
        if oi == 360:  fac1 = 1;  fac2 = 6
        if oi == 240:  fac1 = 1;  fac2 = 4
        if oi == 60:   fac1 = 1;  fac2 = 1
        if oi == 30:   fac1 = 2;  fac2 = 1
        if oi == 20:   fac1 = 3;  fac2 = 1
        if oi == 15:   fac1 = 4;  fac2 = 1
        if oi == 10:   fac1 = 6;  fac2 = 1
        if oi == 5:    fac1 = 12; fac2 = 1
        if oi == 2:    fac1 = 30; fac2 = 1
        if oi == 1:    fac1 = 60; fac2 = 1

        self.header = {
            'tr': tr,
            'pr': pr,
            'oi': oi,
            'ne': ne,
            'rgt': rgt,
            'wsh': wsh,
            'ne': ne,
            'pcodes': pcodes,
            'fac1': fac1,
            'fac2': fac2,
        }

        return self.header

    def header_size(self):
        """
        After reading header, return where self.fd.tell() should be. In other words,
        how many bytes does the header consume?
        """
        if not self.header:
            self.read_header()

        size = 0
        size += 2  # tr
        size += 4  # pr
        size += 2  # oi
        size += 2  # ne
        size += 2  # rgt
        size += 2  # wsh
        size += 2 * 8  # unused
        size += self.header['ne'] * 3  # pcode string

        return size

    def read_data(self):
        """
        Read the entire wea file and store in a numpy.array
        """
        if self.data is None:
            h = self.read_header()
            ne, pr, oi = h['ne'], h['pr'], h['oi']
            self.fd.seek(0)  # reset fd because memmap will do its own offset
            # Create a memmap array-like object.
            # TODO: possibly call ndarray.__new__ with this as buffer.
            self.data = np.memmap(
                self.fd,
                dtype=np.dtype('<f4'),  # 32-bit float, little-endian
                mode='r',  # read-only mode
                offset=self.header_size(),  # skip these bytes of the header
                shape=((pr / oi), ne))  # reshape to (num records, num elements)

        # Now self.data is an array like the output of readwea2.e
        # self.data[:, 2].min(): the min value of column 2 (same as pcodes[2])
        return self.data

    def latest_data(self):
        """
        Return a slice of self.data with the most recent, non-missing data.
        """
        MISSING = 10000000.0  # TODO: Get this from settings?
        a = self.data  # use a short reference to data array

        # We want to find the last row of data where
        # there is a non-missing value, excluding the first two columns,
        # which are DAY and TIM.
        ind = np.where(a[:,2:] < MISSING)  # the index where non-missing are
        last_row = ind[0][-1]
        # TODO: Convert to requested units_system
        # Convert data to floats to allow json serialize
        data = dict(zip(self.header['pcodes'], [float(i) for i in a[last_row]]))
        return data


if __name__ == '__main__':
    # This is just an example of how to use WeaFile.
    filename = sys.argv[1]

    wea = WeaFile(filename)
    h = wea.header

    # similar to readwea2.e output
    print h['tr']
    print h['pr']
    print h['oi']
    print h['ne']
    print h['rgt']
    print h['wsh']
    print ''.join(h['pcodes'])

    for row in wea.data:
        print "  ".join(["%.6f" % d for d in row])
