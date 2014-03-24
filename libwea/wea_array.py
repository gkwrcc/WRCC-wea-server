import os
import sys
import datetime
import logging

from numpy import array, nan, zeros
from wea_file import WeaFile
from elements import WeaElements
from utils import minutes_diff, round_date, get_next_month, \
    get_var_units, wea_convert

from ..settings import DATAPATH, MISSINGS

log = logging.getLogger('WeaArray')


class WeaArray(object):
    """
    Class that arranges multiple WeaFile objects into a single array.
    """
    def __init__(self, stn_id, sD, eD, units_system='N'):
        self.data = None
        self.stn_id = str(stn_id).lower()
        self.sD = sD
        self.eD = eD
        self.units_system = units_system
        self._make_filenames()
        self._load_full_months()

    def set_units_system(self, new_units_system):
        self.units_system = new_units_system

    def _make_filenames(self):
        "Generate the needed data file names based on months requested."
        base = DATAPATH
        filenames = []
        t = self.sD
        while t.timetuple()[:2] <= self.eD.timetuple()[:2]:
            filenames.append(os.path.join(
                base,
                self.stn_id,
                "%s%s.wea" % (self.stn_id, t.strftime("%m%y"))
            ))
            t = get_next_month(t)
        self.filenames = filenames

    def _load_full_months(self):
        "Create WeaFile objects, which load the entire data file."
        weafiles = []
        for f in self.filenames:
            weafiles.append(WeaFile(f))
        self.weafiles = weafiles
        log.debug("weafiles: %s" % " ".join(map(str, weafiles)))

    def _last_header(self):
        return self.weafiles[-1].header

    def get_ne(self):
        return self._last_header()['ne']
        """
        s = set()
        for f in self.weafiles:
            s.add(f.header['ne'])
        return max(list(s))
        """

    def get_var(self, pcode, round_start_up=False, round_end_up=False):
        pcode = str(pcode).upper()
        h = self.weafiles[0].header
        for f in self.weafiles:
            assert f.header['oi'] == h['oi']

        rsD = round_date(self.sD, h['oi'], up=round_start_up)
        reD = round_date(self.eD, h['oi'], up=round_end_up)
        md = minutes_diff(rsD, reD)
        num_vals = (md / h['oi']) + 1

        # calculate starting index
        s_indx = minutes_diff(
            self.sD.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            rsD) / h['oi']
        # calculate ending index
        e_indx = minutes_diff(
            self.eD.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            reD) / h['oi']

        log.debug(h)
        log.debug("Start (round): %s   %s" % (self.sD, rsD))
        log.debug("End   (round): %s   %s" % (self.eD, reD))
        log.debug("minute diff: %s" % md)
        log.debug("num vals: %s" % num_vals)

        # TODO: Use faster array operations instead of
        # extending a list
        ret = []
        for f in self.weafiles:
            pcodes = list(f.header['pcodes'])
            if pcode in pcodes:
                indx = pcodes.index(pcode)
                # if only one data file
                if len(self.weafiles) == 1:
                    ret.extend(list(f.data[:, indx][s_indx:e_indx + 1]))
                # if first file
                elif f == self.weafiles[0]:
                    ret.extend(list(f.data[:, indx][s_indx:]))
                # if last file
                elif f == self.weafiles[-1]:
                    ret.extend(list(f.data[:, indx][:e_indx + 1]))
                else:  # use full month
                    # grab the column from the data array
                    ret.extend(list(f.data[:, indx]))
            else:
                # WHAT TO DO IF pcode DOESN'T EXIST??
                raise

        # Convert units, unless N (native)
        if self.units_system != 'N':
            # Get this element's properties
            try:
                elem = WeaElements[pcode]
            except KeyError:
                elem = {}

            # Try to get a conversion function to change units
            if 'units' in elem and elem['units']:
                conv_f, new_units = wea_convert(elem['units'], self.units_system)
                if not conv_f is None:
                    for i in range(len(ret)):
                        if not ret[i] in MISSINGS:
                            ret[i] = conv_f(ret[i])

        # Return a numpy array
        return array(ret)


if __name__ == '__main__':
    log = logging.getLogger('WeaArray')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())  # log output to console
    w = WeaArray('slid',
                 datetime.datetime(2007, 2, 28, 23, 40),
                 datetime.datetime(2008, 3, 1, 0, 20))
    w.set_units_system("M")
    print w.get_var('AVA')
