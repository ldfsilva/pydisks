import sys
import argparse
import json


def clean_line(line):
    """Clean up and split file line"""

    line = line.strip()
    line = line.replace(' ', '')
    line = line.split(',')

    return line


def build_dict(f_content):
    """It loads a dictionary with servers' volume group detail.

    File content is expected to be in the following format[1].

    [1] file format:
    lpar_name,disk_name,pvid,serial_number,disk_size,vg_name

    file sample:
    lpar1,hdisk0,00f713f8ee8cb0a5,200C,70031,rootvg
    lpar1,hdisk3,00f713f3399dfd5d,2806,61440,pagingvg
    lpar1,hdisk4,00f713f306ce1167,2DFF,102401,datavg
    lpar1,hdisk5,00f713f802eacdae,0761,116738,datavg
    """
    lpar_dict = {}

    for line in f_content.splitlines():
        lpar, hdisk, pvid, serial, size, vg = clean_line(line)

        # update existent lpar detail in dict
        if lpar in lpar_dict:
            # add initial vg detail to the dict
            if not vg in lpar_dict[lpar]:
                lpar_dict[lpar].update({vg: {hdisk: int(size) }})
            # update existent vg detail in dict
            lpar_dict[lpar][vg].update({hdisk: int(size)})
        # add initial lpar detail to the dict
        else:
            lpar_dict.update({lpar: {vg: {hdisk: int(size)}}})

    return lpar_dict


def sum_up_dict(lpar_dict):
    """Walk through an initial dictionary build by build_dict and add
    information pertaining to each lpar at different levels.

    From bottom to the top it will be added:

    #1 high level detail at VG level
        n_disks == total number of disks
        t_size  == total capacity

    #2 high level detail at lpar level
        n_vgs   == total number of VGs
        n_disks == total number of disks
        t_size  == total capacity

    #3 high level detail for all lpars
        n_lpars == total number of lpars
        n_vgs   == total number of VGs
        n_disks == total number of disks
        t_size  == total capacity
    """

    # initiatlize variables for later use
    t_vgs = 0
    t_disks = 0
    t_capacity = 0
    # count number of lpars
    n_lpar = len(lpar_dict.keys())

    # iterate through each lpar and vg calculating totals
    for lpar, vgs in lpar_dict.items():
        lpar_size = 0
        lpar_disks = 0
        for vg, disks in vgs.items():
            t_size = 0
            for size in disks.values():
                t_size += size
            n_disks = len(disks)

            # #1 update at vg level
            # add VG total size and number of disks
            lpar_dict[lpar][vg].update({'t_size': t_size, 'n_disks': n_disks})
            lpar_size += t_size
            lpar_disks += n_disks
            n_vgs = len(vgs)

        # #2 update at lpar level
        # add lpar total size, number of disks and number of VGs
        lpar_dict[lpar].update(
            {'n_vgs': n_vgs, 't_size': lpar_size, 'n_disks': lpar_disks}
        )
        t_capacity += lpar_size
        t_disks += lpar_disks
        t_vgs += n_vgs

    # #3 update for all lpars
    # add total number of lpars, number of VGs, total size, and number of disks
    lpar_dict.update({
            'n_lpars': n_lpar, 'n_vgs': t_vgs,
            't_size': t_capacity, 'n_disks': t_disks
    })

    return lpar_dict


def summary(lpar_dict):
    """Print a summary for all lpars"""

    # get high level information for all lpars
    n_lpars = lpar_dict.get('n_lpars')
    total_vgs = lpar_dict.get('n_vgs')
    total_disks = lpar_dict.get('n_disks')
    total_size = lpar_dict.get('t_size')
    message = ''

    # build the print message
    message += (
        '{0}{5}{0}'
        'Number of LPARS: {1}{0}'
        'Total number of VGs: {2}{0}'
        'Total number of disks: {3}{0}'
        'Total capacity: {4} MB{0}'
    ).format('\n', n_lpars, total_vgs, total_disks, total_size, '-'*20)

    print(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", 
        help="input file containing LPAR VGs and disks information in csv format"
    )

    args = parser.parse_args()
    if args.filename:
        filename = args.filename

        with open(filename) as fd:
            f_content = fd.read()

        
        lpar_dict = build_dict(f_content)
        lpar_dict = sum_up_dict(lpar_dict)
        summary(lpar_dict)

