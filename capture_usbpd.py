#!/bin/env python
#==========================================================================
# (c) 2017  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : PD Analyzer Sample Code
# File    : capture_usbpd.py
#--------------------------------------------------------------------------
# Simple Capture Example
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
#from pd_py import *
import pd_py
import sys

#==========================================================================
# PRINT FUNCTIONS
#==========================================================================
def print_pd_info (idx, info, info_type):
    print '%d, %d, %s,' % (idx, info.timestamp, info_type),

    if info_type != 'PD':
        return True

    cc = (info.events & pd_py.PD_EVENT_USBPD_CC_MASK) >> pd_py.PD_EVENT_USBPD_CC_SHIFT
    print '%d,' % (cc + 1),

    if info.events & pd_py.PD_EVENT_USBPD_POL_CHANGE:
        print 'POL_CHANGE,'
        return False
    elif (info.events & pd_py.PD_EVENT_USBPD_SOP_MASK) == pd_py.PD_EVENT_USBPD_HARD_RESET:
        print 'HARD_RESET,'
        return False
    elif (info.events & pd_py.PD_EVENT_USBPD_SOP_MASK) == pd_py.PD_EVENT_USBPD_CABLE_RESET:
        print 'CABLE_RESET,'
        return False

    pos_err = info.status & pd_py.PD_STATUS_USBPD_ERR_MASK
    if pos_err == pd_py.PD_STATUS_USBPD_ERR_PREAMBLE:
        print 'ERR_PREAMBLE,',
    elif pos_err == pd_py.PD_STATUS_USBPD_ERR_SOP:
        print 'ERR_SOP,',
    elif pos_err == pd_py.PD_STATUS_USBPD_ERR_HEADER:
        print 'ERR_HEADER,',
    elif pos_err == pd_py.PD_STATUS_USBPD_ERR_DATA:
        print 'ERR_DATA,',
    elif pos_err == pd_py.PD_STATUS_USBPD_ERR_CRC:
        print 'ERR_CRC,',
    elif pos_err == pd_py.PD_STATUS_USBPD_ERR_EOP:
        print 'ERR_EOP,',

    if info.status & pd_py.PD_STATUS_USBPD_ERR_BAD_CRC:
        print 'BAD_CRC,',
    elif pos_err == 0:
        print 'OK,',

    return True

def print_bits (idx, info, bits, pl, bl):
    kcode_str = [
        'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'SYNC3', 'RST1',
        'Error', '1', '4', '5', 'Error', 'EOP', '6', '7',
        'Error', 'SYNC2', '8', '9', '2', '3', 'A', 'B',
        'SYNC1', 'RST2', 'C', 'D', 'E', 'F', '0', 'Error'
    ]

    if not print_pd_info(idx, info, 'PD'):
        return

    print '%d,' % pl,

    for ii in range(pl, bl, 5):
        if ii + 5 > bl:
            break

        kcode = 0
        for jj in range(5):
            off = ii + jj
            bit = (bits[off / 8] >> (7 - (off % 8))) & 0x1

            kcode |= (bit << jj)

        print '%s' % kcode_str[kcode],

    print ''

def print_pd_packets (idx, info, preamble, header, crc, data):
    if not print_pd_info(idx, info, 'PD'):
        return

    pos_err = info.status & pd_py.PD_STATUS_USBPD_ERR_MASK

    if (pos_err == pd_py.PD_STATUS_USBPD_ERR_PREAMBLE or
        pos_err == pd_py.PD_STATUS_USBPD_ERR_SOP):
        print ''
        return

    sop_str = [ 'SOP', 'SOP\'', 'SOP"', 'SOP\'D', 'SOP"D', '', '', '' ]
    sop = info.events & pd_py.PD_EVENT_USBPD_SOP_MASK

    print '%s,' % sop_str[sop],

    if pos_err == pd_py.PD_STATUS_USBPD_ERR_HEADER:
        print ''
        return

    if info.events & pd_py.PD_EVENT_USBPD_EXTENDED_HEADER:
        print '%04x;%04x,' \
            % (header & pd_py.PD_HEADER_USBPD_STANDARD_MASK,
               (header & pd_py.PD_HEADER_USBPD_EXTENDED_MASK) >> 16),
    else:
        print '%04x,' % (header & pd_py.PD_HEADER_USBPD_STANDARD_MASK),

    if len(data) > 0:
        for offset in range(len(data)):
            print "%02x" % data[offset],

    print ",",

    if (pos_err == pd_py.PD_STATUS_USBPD_ERR_DATA or
        pos_err == pd_py.PD_STATUS_USBPD_ERR_CRC):
        print ''
        return

    if info.status & pd_py.PD_STATUS_USBPD_ERR_BAD_CRC:
        print '%08x(NOT OK)' % crc
    else:
        print '%08x(OK)' % crc

def print_pd_iv (idx, info, val, debug):

    #if not print_pd_info(idx, info, 'PD_IV'):
    #   return

    iv_type = ((info.events & pd_py.PD_EVENT_USBPD_IV_SOURCE_MASK)
               >> pd_py.PD_EVENT_USBPD_IV_SHIFT)
    iv_type_str = [
        'Vbus Voltage', 'Vbus Current', 'Vconn Voltage', 'Vconn Current',
        'CC1 Voltage', 'CC1 Current', 'CC2 Voltage', 'CC2 Current',
    ]

    # Create data list, convert mV/mA to V/A
    data = [info.timestamp / 1e6, iv_type_str[iv_type], val * 1e-3]
    if debug == 1:
        print('%s, %d%s' % (iv_type_str[iv_type], val, 'mA' if (iv_type & 1) else 'mV'))
    return data

#==========================================================================
# DUMP FUNCTIONS
#==========================================================================
def dump_pd_raw (pd, num_packets):
    packetnum = 0

    print "index,time(us),PD,status,cc,preamble,bits"

    while (num_packets <= 0 or packetnum < num_packets):
        # maximum bit length of USB PD v3.0 is 2769 bits = 347 bytes
        ret, info, bl, pl, bits = pd_py.pd_usbpd_read_bits(pd, 512)
        if ret == pd_py.PD_READ_EMPTY:
            continue

        if ret < 0:
            print ('Failed to capture PD on port: %d(%s)' %
                   (ret, pd_py.pd_status_string(ret)))
            break

        print_bits(packetnum, info, bits, pl, bl)

        packetnum += 1

def dump_pd_data (pd, num_packets):
    packetnum = 0

    print "index,time(us),PD,cc,status,sop,header,data0 ... dataN,crc"

    while (num_packets <= 0 or packetnum < num_packets):
        # maximum bit length of USB PD v3.0 is 2769 bits = 347 bytes
        ret, info, pl, header, crc, data = pd_py.pd_usbpd_read_data(pd, 512)
        if ret == pd_py.PD_READ_EMPTY:
            continue

        if ret < 0:
            print ('Failed to capture PD on port: %d(%s)' %
                   (ret, pd_py.pd_status_string(ret)))
            break

        print_pd_packets(packetnum, info, pl, header, crc, data)

        packetnum += 1

def dump_pd_iv (pd, num_packets, debug):
    packetnum = 0
    data = []

    print "index,time(us),PD_IV,type,value"

    while (num_packets <= 0 or packetnum < num_packets):
        ret, info, val = pd_py.pd_usbpd_read_iv(pd)
        if ret == pd_py.PD_READ_EMPTY:
            continue

        if ret < 0:
            print ('Failed to capture PD on port: %d(%s)' %
                   (ret, pd_py.pd_status_string(ret)))
            break

        # Create a list of lists with single data points
        data.append(print_pd_iv(packetnum, info, val, debug))

        packetnum += 1
    return data

def dump_pd_all (pd, num_packets):
    packetnum = 0

    print "index,time(us),PD,cc,status,sop,header,data0 ... dataN,crc"
    print " or"
    print "index,time(us),PD_IV,type,value"

    while (num_packets <= 0 or packetnum < num_packets):
        ret, info, pl, header, crc, data = pd_py.pd_usbpd_read_data(pd, 512)
        if ret != pd_py.PD_READ_EMPTY:
            if ret < 0:
                print ('Failed to capture PD on port: %d(%s)' %
                       (ret, pd_py.pd_status_string(ret)))
                break

            print_pd_packets(packetnum, info, pl, header, crc, data)

            packetnum += 1

        ret, info, val = pd_py.pd_usbpd_read_iv(pd)
        if ret != pd_py.PD_READ_EMPTY:
            if ret < 0:
                print ('Failed to capture PD on port: %d(%s)' %
                       (ret, pd_py.pd_status_string(ret)))
                break

            print_pd_iv(packetnum, info, val)

            packetnum += 1


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: capture_usbpd port mode num_events
Example utility for capturing USB PD data from Power Delivery analyzers.

  The parameter mode can be one of 'raw', 'data', 'iv', and 'all'.
    'raw' mode shows raw data after bmc decoding, 'data' mode shows pd packets,
    'iv' mode shows voltage and current, and 'all' is combined of 'data' and 'iv'

  The parameter num_events is set to the number of events to process
    before exiting.  If num_events is set to zero, the capture will continue
    indefinitely.

For product documentation and specifications, see www.totalphase.com."""
    sys.stdout.flush()


#==========================================================================
# MAIN PROGRAM
#==========================================================================
def capture_usbpd(port=0, mode='iv', num=10, debug=0):

    '''
    if (len(sys.argv) < 3):
        print_usage()
        sys.exit()

    port = int(sys.argv[1])
    mode = sys.argv[2]
    num  = int(sys.argv[3]) if len(sys.argv) == 4 else 0
    '''

    data = []

    # Open the device
    pd = pd_py.pd_open(port)
    if (pd <= 0):
        print ('Unable to open PD Analyzer on port %d: %d(%s)' %
               (port, pd, pd_py.pd_status_string(pd)))
        sys.exit(1)
    print 'Opened PD Analyzer on port %d' % port;

    # Start capture
    pd_py.pd_capture_start(pd)

    print 'Start capturing'
    if mode == 'raw':
        dump_pd_raw(num)
    if mode == 'data':
        dump_pd_data(num)
    if mode == 'iv':
        data = dump_pd_iv(pd, num, debug)
    if mode == 'all':
        dump_pd_all(num)

    # Stop capture
    pd_py.pd_capture_stop(pd)

    # Close the device
    pd_py.pd_close(pd)

    return data

#capture_usbpd(0, 'iv', 10)
