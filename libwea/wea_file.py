#
# wea_file
#

import sys
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
            self.fd = open(filename, 'rb')
            self.read_data()

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

    def read_data(self):
        """
        Read the entire wea file and store in a numpy.array
        """
        if self.data is None:
            h = self.read_header()
            ne, pr, oi = h['ne'], h['pr'], h['oi']
            self.data = array(
                    self._do_unpack("%df" % ne * (pr / oi),
                    4 * ne * (pr / oi))
                ).reshape((pr / oi), ne)
        # Now self.data is an array like the output of readwea2.e
        # self.data[:, 2].min(): the min value of column 2 (same as pcodes[2])
        return self.data


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
