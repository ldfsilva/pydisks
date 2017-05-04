#!/usr/bin/env ksh
#
# It collects aix fc information and output its results in a
# csv file on the following format:
#
# File name: <server_name>_<date>.csv
#
# Sample csv output file
#
# vios01,fcs0,10000000C94B3117,DPM078F-P1-C1-T1,80P4543,1B5310346A
# vios01,fcs1,10000000C946DDC1,DPM078F-P1-C2-T1,80P4543,1B52603F5C
#

# server name
SERVER=$(uname -n)

# <year><month><day>_<hour><minute><second>
DATE="$(date +%Y%m%d_%H%M%S)"

LOGFILE="fc_info_${SERVER}_${DATE}.csv"

echo "server,fc,wwpn,hardware_location,part_number,serial_number" | tee -a $LOGFILE
lsdev -Cc adapter -F name -l fcs* | while read fc; do
    fc_info=$(lscfg -vl $fc)
    fc_pn=$(echo "$fc_info" | sed '/Part Number/!d;s/.*[\.\., ]//')
    fc_serial=$(echo "$fc_info" | sed '/Serial Number/!d;s/.*[\.\., ]//')
    fc_hlc=$(echo "$fc_info" | sed '/Hardware Location Code/!d;s/.*[\.\., ]//')
    fc_wwpn=$(echo "$fc_info" | sed '/Network Address/!d;s/.*[\.\., ]//')

    # output to file
    echo "$SERVER,$fc,$fc_wwpn,$fc_hlc,$fc_pn,$fc_serial" | tee -a $LOGFILE
done

