#!/usr/bin/env ksh
#
# It collects aix disk information and output its results in a 
# csv file on the following format:
#
# File name: <server_name>_<date>.csv
#
# Sample csv output file
#
# vios01,hdisk0,00c7dbbe6670ae67,0004AC9A,70006,rootvg
# vios01,hdisk1,00c7dbbeb43e6001,0004AC84,70006,None
#

# server name
SERVER=$(uname -n) 

# <year><month><day>_<hour><minute><second>
DATE="$(date +%Y%m%d_%H%M%S)"

LOGFILE="${SERVER}_${DATE}.csv"

lspv | while read disk pvid vg active; do
    # verify if the disk is a hdiskpower device
    echo $disk | grep -q power && is_hdisk_power=1 || is_hdisk_power=0
    if [ $is_hdisk_power -eq 1 ]; then
        serial=$(powermt display dev=$disk | grep -i logical | cut -d'=' -f2)
    else
        serial=$(lscfg -vpl $disk | grep 'Serial Number'|sed 's/.*\.//')
    fi
    size=$(bootinfo -s $disk)

    # output to file
    echo "$SERVER,$disk,$pvid,$serial,$size,$vg" | tee -a $LOGFILE
done