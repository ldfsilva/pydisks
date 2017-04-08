import unittest
from unittest.mock import patch, mock_open
from collections import namedtuple
from pydisks import clean_line, build_dict, sum_up_dict


class TestSplitLine(unittest.TestCase):
    def setUp(self):
        self.data = "lpar01,hdisk0,00c7dbbe6670ae67  ,0004AB8A, 70006,rootvg\n"

    def test_clean_line_returns_a_list(self):
        """clean_line has to return a list"""

        res = clean_line(self.data)

        self.assertTrue(type([]), type(res))

    def test_clean_line_lenght_equals_6(self):
        """clean_line list lenght equals to 6"""

        res = clean_line(self.data)

        self.assertTrue(6, len(res))

    def test_clean_line_content(self):
        """clean_line check its content"""

        expected = ['lpar01', 'hdisk0', '00c7dbbe6670ae67',
                   '0004AB8A', '70006', 'rootvg']
        res = clean_line(self.data)

        self.assertListEqual(expected, res)

    def test_clean_line_has_no_line_return(self):
        """spline_line has no \n"""

        res = clean_line(self.data)

        for val in res:
            with self.subTest():
                self.assertNotIn('\n', val)

    def test_clean_line_has_no_line_spaces(self):
        """spline_line has no spaces"""

        res = clean_line(self.data)

        for val in res:
            with self.subTest():
                self.assertNotIn(' ', val)


class TestBuildDict(unittest.TestCase):
    def setUp(self):
        self.data = (
            "lpar01,hdisk0,00c7dbbe6670ae67,0004AB8A,70006,rootvg\n"
            "lpar01,hdisk1,00c7dbbe6670ae68,0004AB8B,70006,datavg\n"
            "lpar01,hdisk2,00c7dbbe6670ae69,0004AB8C,70006,datavg\n"
        )

    def test_build_dict_return_dict(self):
        "build_dict has to return a dictionary"""

        res = build_dict(self.data)

        self.assertTrue(type({}), type(res))
        
    def test_build_dict_content(self):
        expected = {
            'lpar01': {
                'rootvg': { 
                    'hdisk0': 70006,
                },
                'datavg': {
                    'hdisk1': 70006,
                    'hdisk2': 70006,
                },
            },
        }
        res = build_dict(self.data)

        self.assertDictEqual(expected, res)

    def test_sum_up_dict_content(self):
        # data returned by build_dict
        lpar_dict = {
            'lpar01': {
                'rootvg': {'hdisk0': 70006},
                'datavg': {'hdisk1': 70006, 'hdisk2': 70006}
            },
            'lpar02': {'rootvg': { 'hdisk0': 70006}}
        }
        expected = {
            'lpar01': {
                'rootvg': { 
                    'hdisk0': 70006, 'n_disks': 1, 't_size': 70006,
                },
                'datavg': {
                    'hdisk1': 70006, 'hdisk2': 70006,
                    'n_disks': 2, 't_size': 140012,
                },
                'n_vgs': 2, 'n_disks': 3, 't_size': 210018,
            },
            'lpar02': {
                'rootvg': { 
                    # high level detail at VG level 
                    # n_disks == total number of disks
                    # t_size == total capacity
                    'hdisk0': 70006, 'n_disks': 1, 't_size': 70006,
                },
                # high level detail at lpar level
                # n_vgs == total number of VGs
                # n_disks == total number of disks
                # t_size == total capacity
                'n_vgs': 1, 'n_disks': 1, 't_size': 70006,
            },
            # high level detail for all lpars
            # n_lpars == total number of lpars
            # n_vgs   == total number of VGs
            # n_disks == total number of disks
            # t_size  == total capacity
            'n_lpars': 2, 'n_vgs': 3, 'n_disks': 4, 't_size': 280024,
        }
        res = sum_up_dict(lpar_dict)

        self.assertDictEqual(expected, res)

