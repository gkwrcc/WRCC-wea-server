#
# meta
# Metadata functions
#

import os
import datetime
from utils import yearmonth_from_filename, is_valid_filename, days_in_month
from ..settings import DATAPATH

class WeaMeta(object):
    def __init__(self, stn_id):
        self.stn_id = str(stn_id).lower()
        self.data_dir = os.path.join(DATAPATH, self.stn_id)

    def get_date_list(self):
        """
        Return a list of dates (year/month) that this stn has data files.
        """
        filenames = os.listdir(self.data_dir)
        dates = [yearmonth_from_filename(f)
                for f in filenames if is_valid_filename(f, self.stn_id)]
        dates.sort()
        return dates

    def get_latest_month(self):
        dates = self.get_date_list()
        if dates:
            y = dates[-1][0]
            m = dates[-1][1]
            return datetime.datetime(y, m, days_in_month(m, y))
