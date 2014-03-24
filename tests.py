import datetime
import unittest
import requests
import json
from numpy import array
from unittest import TestCase
from libwea.utils import round_date, minutes_diff, days_in_month, is_leap, \
                    is_valid_filename, filename_from_yearmonth, \
                    datetime_from_DAYTIM, wea_convert, get_var_units
from libwea.wea_file import WeaFile
from libwea.wea_array import WeaArray
from libwea.meta import WeaMeta
from libwea.elements import WeaElements
from service import utils
from settings import TEST_SERVICE

class DatetimeTest(TestCase):
    def setUp(self):
        pass

    def testFive(self):
        d1 = datetime.datetime(2009, 1, 1, 8, 16)
        d2 = datetime.datetime(2009, 1, 1, 8, 15)
        d3 = datetime.datetime(2009, 1, 1, 8, 20)
        self.assertEquals(d2, round_date(d2, 5))
        self.assertEquals(d2, round_date(d1, 5))
        self.assertEquals(d3, round_date(d1, 5, up=True))
        self.assertEquals(d3 + datetime.timedelta(seconds=60 * 5),
                          round_date(d3, 5, up=True))

    def testTen(self):
        d1 = datetime.datetime(2009, 1, 1, 8, 15)
        d2 = datetime.datetime(2009, 1, 1, 8, 10)
        d3 = datetime.datetime(2009, 1, 1, 8, 20)
        self.assertEquals(d2, round_date(d2, 10))
        self.assertEquals(d2, round_date(d1, 10))
        self.assertEquals(d3, round_date(d1, 10, up=True))
        self.assertEquals(d3 + datetime.timedelta(seconds=60 * 10),
                          round_date(d3, 10, up=True))

    def testFifteen(self):
        d1 = datetime.datetime(2009, 1, 1, 8, 20)
        d2 = datetime.datetime(2009, 1, 1, 8, 15)
        d3 = datetime.datetime(2009, 1, 1, 8, 30)
        self.assertEquals(d2, round_date(d2, 15))
        self.assertEquals(d2, round_date(d1, 15))
        self.assertEquals(d3, round_date(d1, 30, up=True))
        self.assertEquals(d3 + datetime.timedelta(seconds=60 * 30),
                          round_date(d3, 30, up=True))

    def testSixty(self):
        d1 = datetime.datetime(2009, 1, 1, 8, 25)
        d2 = datetime.datetime(2009, 1, 1, 8, 0)
        d3 = datetime.datetime(2009, 1, 1, 9, 0)
        self.assertEquals(d2, round_date(d2, 60))
        self.assertEquals(d2, round_date(d1, 60))
        self.assertEquals(d3, round_date(d1, 60, up=True))
        self.assertEquals(d3 + datetime.timedelta(seconds=60 * 60),
                          round_date(d3, 60, up=True))

    """
    def testDontRound(self):
        d1 = datetime.datetime(2009, 1, 1, 8, 25)
        self.assertEquals(d1, round_date(d1,5, up=True))
    """

    def testTotalMins(self):
        d1 = datetime.datetime(2008, 1, 1, 10, 0)
        d2 = datetime.datetime(2008, 1, 1, 10, 30)
        self.assertEquals(0, minutes_diff(d1, d1))
        self.assertEquals(30, minutes_diff(d1, d2))
        d1 = datetime.datetime(2009, 1, 1, 0, 0)
        d2 = datetime.datetime(2009, 12, 31, 23, 59)
        self.assertEquals(525599, minutes_diff(d1, d2))

    def testYearMonthFromFile(self):
        for y in range(1940, 2008):
            for m in range(1, 13):
                filename = "/tmp/weabase/data/nnsc/nnsc%02d%s.wea" % (m, str(y)[-2:])
                wea = WeaFile(filename, readdata=False)
                self.assertEquals((y, m), wea.yearmonth())

    def testYearsArray(self):
        filename = "/tmp/weabase/data/nnsc/nnsc0112.wea"
        wea = WeaFile(filename)
        # Check that all elements are the same.
        self.assertEquals(wea.years.all(), array([2012,] * 4464).all())

    def testNumberElements(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 1, 1, 0, 0),
                     datetime.datetime(2011, 1, 1, 23, 50))
        h = w._last_header()
        self.assertEquals(22, w.get_ne())
        self.assertEquals(len(h['pcodes']), w.get_ne())

    def testYearsWeaArray(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 12, 31),
                     datetime.datetime(2012, 1, 31, 23, 50))
        years = w.get_var('years')
        self.assertEquals(len(years), 4608)

    def testFullMonth(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 1, 1, 0, 0),
                     datetime.datetime(2011, 3, 31, 23, 50))
        rec_length = 0  # Expected number of records
        for wf in w.weafiles:
            h = wf.header
            rec_length += h['pr'] / h['oi']
        self.assertEquals(len(w.get_var('TIM')), rec_length)

    def testObInterval(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2012, 1, 1, 0, 0),
                     datetime.datetime(2012, 1, 1, 23, 50))
        ans = [
            "%02d%02d" % (i, j)
            for i in range(0, 24)
                for j in range(0, 60, 10)]
        result = ["%04d" % i for i in w.get_var('TIM')]
        self.assertEquals(ans, result)
        w = WeaArray('nnsc',
                     datetime.datetime(2012, 2, 29, 23, 50),
                     datetime.datetime(2012, 3, 1, 0, 10))
        result = ["%04d" % i for i in w.get_var('TIM')]
        self.assertEquals(['2350', '0000', '0010'], result)
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 12, 31, 23, 40),
                     datetime.datetime(2012, 1, 1, 0, 10))
        result = ["%04d" % i for i in w.get_var('TIM')]
        self.assertEquals(['2340', '2350', '0000', '0010'], result)

        w = WeaArray('nnsc',
                     datetime.datetime(2011, 12, 31, 23, 40),
                     datetime.datetime(2012, 1, 1, 0, 10))
        result = ["%04d" % i for i in w.get_var('TIM')]
        self.assertEquals(['2340', '2350', '0000', '0010'], result)


class OpenFileTest(TestCase):
    def setUp(self):
        pass

    def testOneMonth(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 1, 1, 0, 0),
                     datetime.datetime(2011, 1, 31, 0, 0))
        self.assertEquals(1, len(w.filenames))
        self.assertEquals(1, len(w.weafiles))

    def testTwoMonths(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 6, 30, 0, 0),
                     datetime.datetime(2011, 7, 31, 0, 0))
        self.assertEquals(2, len(w.filenames))
        self.assertEquals(2, len(w.weafiles))

    def testOneYear(self):
        w = WeaArray('nnsc',
                     datetime.datetime(2011, 1, 15, 0, 0),
                     datetime.datetime(2011, 12, 31, 0, 0))
        self.assertEquals(12, len(w.filenames))
        self.assertEquals(12, len(w.weafiles))


class LeapYearTest(TestCase):
    def setUp(self):
        pass

    def testBadDaysInMonth(self):
        self.assertRaises(ValueError, days_in_month, 2000, -19)

    def testDaysInMonth(self):
        numdays = {1: (31, 31), 2: (28, 29), 3: (31, 31), 4: (30, 30),
                   5: (31, 31), 6: (30, 30), 7: (31, 31), 8: (31, 31),
                   9: (30, 30), 10: (31, 31), 11: (30, 30), 12: (31, 31)}
        for k, v in numdays.items():
            self.assertEquals(days_in_month(k, 1999), v[0])
            self.assertEquals(days_in_month(k, 2000), v[1])
        for y in range(1900, 2101):
            n = is_leap(y) and 29 or 28
            self.assertEquals(days_in_month(2, y), n)


class UtilsTest(TestCase):
    def setUp(self):
        pass

    def testBadParseDate(self):
        self.assertEquals(None, utils.parse_date(None))
        self.assertEquals(None, utils.parse_date('9999-9999-9999-9999'))
        self.assertEquals(None, utils.parse_date('abcdefgh'))

    def testParseDate(self):
        date_strings = [
            "1999-1-1",
            "2011-1-1-13",
            "2011-12-31-23-59",
        ]
        date_objs = [
            datetime.datetime(1999,1,1),
            datetime.datetime(2011,1,1,13),
            datetime.datetime(2011,12,31,23,59),
        ]
        for s, d in zip(date_strings, date_objs):
            self.assertEquals(utils.parse_date(s), d)

    def testValidFilename(self):
        self.assertTrue(
            is_valid_filename('nnsc1012.wea', 'nnsc')
            )
        self.assertFalse(  # incorrect stn_id
            is_valid_filename('aaaa1012.wea', 'nnsc')
            )
        self.assertFalse(  # incorrect month
            is_valid_filename('nnsc1300.wea', 'nnsc')
            )
        self.assertFalse(  # incorrect month
            is_valid_filename('nnsc0000.wea', 'nnsc')
            )
        self.assertFalse(  # incorrect format
            is_valid_filename('1300nnsc.wea', 'nnsc')
            )
        self.assertFalse(  # incorrect format
            is_valid_filename('nnsc0101', 'nnsc')
            )

    def testMakeFilename(self):
        for y in (1999,2000,2011):
            for m in (1,2,3,4,5,6,7,8,9,10,11,12):
                fn = filename_from_yearmonth((y,m), 'NNSC')
                self.assertEquals(
                    "nnsc%s%s.wea" % ("%02d" % m, str(y)[2:]),
                    fn)
    def test_datetime_from_DAYTIM(self):
        answers = {
            (1, "0000"): datetime.datetime(2012,1,1,0,0,0),
            (2, "0200"): datetime.datetime(2012,1,2,2,0,0),
            (60, "1001"): datetime.datetime(2012,2,29,10,1,0),
            (366, "2350"): datetime.datetime(2012,12,31,23,50,0),
        }
        for daytim in answers:
            self.assertEquals(answers[daytim], datetime_from_DAYTIM(daytim[0], daytim[1], year=2012))

        answers = {
            (1, "0000"): datetime.datetime(2011,1,1,0,0,0),
            (2, "0200"): datetime.datetime(2011,1,2,2,0,0),
            (60, "1001"): datetime.datetime(2011,3,1,10,1,0),
            (365, "2350"): datetime.datetime(2011,12,31,23,50,0),
        }
        for daytim in answers:
            self.assertEquals(answers[daytim], datetime_from_DAYTIM(daytim[0], daytim[1], year=2011))

    def test_error_response(self):
        r = utils.ErrorResponse("This is an error.")
        d = json.loads(r.data)
        self.assertTrue("error" in d)


class MetaTest(TestCase):
    def setUp(self):
        self.stn_meta = WeaMeta('NNSC')

    def testWeaMetaInit(self):
        self.assertEquals('nnsc', self.stn_meta.stn_id)

    def testDateList(self):
        dates = self.stn_meta.get_date_list()
        self.assertTrue(len(dates)>0)
        # make datetime objects for each (year, month) tuple
        for ym in dates:
            d = datetime.datetime(ym[0], ym[1], 1)

    def testLastestMonth(self):
        today = datetime.date.today()
        last_date = self.stn_meta.get_latest_month()
        self.assertEquals(today.year, last_date.year)
        self.assertEquals(today.month, last_date.month)


class ServiceTest(TestCase):
    def setUp(self):
        self.test_url = TEST_SERVICE

    def make_request(self, url, params={}):
        return json.loads(requests.get(self.test_url+url, params=params).content)

    def testRootHasRoutes(self):
        r = self.make_request("/")
        self.assertTrue("routes" in r)

    def testAllNative(self):
        params = {
            "stn": 'nnsc',
            "sD": '2011-12-7-15',
            "eD": '2011-12-7-16',
        }
        r = self.make_request("/getData", params)
        self.assertEquals(r["stn"], params["stn"])
        self.assertEquals(r["oi"], 10)
        self.assertEquals(r["data"]["TIM"],
            ['1500', '1510', '1520', '1530', '1540', '1550', '1600'])
        self.assertTrue("sD" in r)
        self.assertTrue("eD" in r)

    def testAllNativeArgs(self):
        r = self.make_request("/getData")
        self.assertTrue("error" in r)
        params = {
            "stn": 'nnsc',
        }
        r = self.make_request("/getData", params)
        self.assertTrue("error" in r)
        params = {
            "stn": 'nnsc',
            "sD": '2011-12-1',
        }
        r = self.make_request("/getData", params)
        self.assertTrue("error" in r)

    def testSingleDay(self):
        params = {
            "stn": 'nnsc',
        }
        r = self.make_request("/getDataSingleDay", params)
        self.assertTrue("error" in r)
        params['sD'] = "2012-12-1"
        r = self.make_request("/getDataSingleDay", params)
        self.assertTrue("units" in r)
        self.assertTrue(r["units"].keys() == r["data"].keys())
        self.assertEquals(len(r["data"]["TIM"]), 6*24)
        days = set(r["data"]["DAY"])
        self.assertEquals(len(days), 1)

    def testRecentData(self):
        params = {}
        r = self.make_request("/getMostRecentData", params)
        self.assertTrue("error" in r)
        params = {
            "stn": 'nnsc',
        }
        r = self.make_request("/getMostRecentData", params)
        self.assertTrue("units" in r)
        self.assertTrue("DAY" in r["data"])
        self.assertTrue("TIM" in r["data"])

        # Test that the data pcodes and the units pcodes are the same.
        units_pcodes = r["units"].keys()
        units_pcodes.sort()
        data_pcodes = r["data"].keys()
        data_pcodes.sort()
        self.assertTrue(units_pcodes == data_pcodes)

    def testDateList(self):
        params = {}
        r = self.make_request("/getStnDates", params)
        self.assertTrue("error" in r)
        params = {
            "stn": 'nnsc',
        }
        r = self.make_request("/getStnDates", params)
        self.assertTrue("dates" in r)
        dates = r['dates']
        self.assertTrue(len(dates)>0)
        self.assertEquals(dates[0], [2011, 1])  # the first data month.

    def testConvertData(self):
        params = {
            "stn": 'nnsc',
            "sD": '2012-2-1',
            "eD": '2012-2-2',
            "units": 'M',
        }
        r = self.make_request("/getData", params)
        self.assertEquals(r["units"]["AVA"], "Deg C")
        degC = r["data"]["AVA"]
        params.update({"units": 'E'})
        r = self.make_request("/getData", params)
        self.assertEquals(r["units"]["AVA"], "Deg F")
        degF = r["data"]["AVA"]


class ConversionsTest(TestCase):
    def setUp(self):
        pass

    def testNoConversion(self):
        self.assertEquals((None, None), wea_convert("FooBar", "N"))

    def assertStringEquals(self, a, b, fmt):
        "Helper function to compare formatted strings."
        self.assertEquals(fmt % a, fmt % b)

    def testConvertAVA(self):
        elem = WeaElements['AVA']
        self.assertEquals(elem['units'], "Deg C")
        fmt = elem['format']
        self.assertEquals(fmt, '%.1f')
        ans = (  # various C to F
            (0.0, 32.0),
            (100.0, 212.0),
            (-10.0, 14.0),
            (-17.5, 0.5),
        )
        conv_f, units = wea_convert(elem["units"], "E")
        self.assertEquals(units, "Deg F")
        for a in ans:
            self.assertStringEquals(conv_f(a[0]), a[1], fmt)

    def testVarUnits(self):
        degC = get_var_units('AVA')
        self.assertEquals('Deg C', degC)
        degC = get_var_units('AVA', units_system="M")
        self.assertEquals('Deg C', degC)
        degF = get_var_units('AVA', units_system="E")
        self.assertEquals('Deg F', degF)
        self.assertEquals(None, get_var_units("FOOBAR"))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
