#==========================================================================
# PD Analyzers Library
#--------------------------------------------------------------------------
# Copyright (c) 2004-2017 Total Phase, Inc.
# All rights reserved.
# www.totalphase.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# - Neither the name of Total Phase, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
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
#--------------------------------------------------------------------------
# To access Total Phase PD analyzers through the API:
#
# 1) Use one of the following shared objects:
#      pd.so        --  Linux shared object
#          or
#      pd.dll       --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      pd.c/h       --  C/C++ API header file and interface module
#      pd_py.py     --  Python API
#      pd.bas       --  Visual Basic 6 API
#      pd.cs        --  C# .NET source
#      pd_net.dll   --  Compiled .NET binding
#==========================================================================


#==========================================================================
# VERSION
#==========================================================================
PD_API_VERSION    = 0x0114   # v1.20
PD_REQ_SW_VERSION = 0x0114   # v1.20

import os
import sys
try:
    import pd as api
except ImportError, ex1:
    import imp, platform
    ext = platform.system() in ('Windows', 'Microsoft') and '.dll' or '.so'
    try:
        api = imp.load_dynamic('pd', 'pd' + ext)
    except ImportError, ex2:
        import_err_msg  = 'Error importing pd%s\n' % ext
        import_err_msg += '  Architecture of pd%s may be wrong\n' % ext
        import_err_msg += '%s\n%s' % (ex1, ex2)
        raise ImportError(import_err_msg)

PD_SW_VERSION      = api.py_version() & 0xffff
PD_REQ_API_VERSION = (api.py_version() >> 16) & 0xffff
PD_LIBRARY_LOADED  = \
    ((PD_SW_VERSION >= PD_REQ_SW_VERSION) and \
     (PD_API_VERSION >= PD_REQ_API_VERSION))

from array import array, ArrayType
import struct


#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def array_u08 (n):  return array('B', '\0'*n)
def array_u16 (n):  return array('H', '\0\0'*n)
def array_u32 (n):  return array('I', '\0\0\0\0'*n)
def array_u64 (n):  return array('K', '\0\0\0\0\0\0\0\0'*n)
def array_s08 (n):  return array('b', '\0'*n)
def array_s16 (n):  return array('h', '\0\0'*n)
def array_s32 (n):  return array('i', '\0\0\0\0'*n)
def array_s64 (n):  return array('L', '\0\0\0\0\0\0\0\0'*n)
def array_f32 (n):  return array('f', '\0\0\0\0'*n)
def array_f64 (n):  return array('d', '\0\0\0\0\0\0\0\0'*n)


#==========================================================================
# STATUS CODES
#==========================================================================
# All API functions return an integer which is the result of the
# transaction, or a status code if negative.  The status codes are
# defined as follows:
# enum PdStatus
# General codes (0 to -99)
PD_OK                      =    0
PD_UNABLE_TO_LOAD_LIBRARY  =   -1
PD_UNABLE_TO_LOAD_DRIVER   =   -2
PD_UNABLE_TO_LOAD_FUNCTION =   -3
PD_INCOMPATIBLE_LIBRARY    =   -4
PD_INCOMPATIBLE_DEVICE     =   -5
PD_INCOMPATIBLE_DRIVER     =   -6
PD_COMMUNICATION_ERROR     =   -7
PD_UNABLE_TO_OPEN          =   -8
PD_UNABLE_TO_CLOSE         =   -9
PD_INVALID_HANDLE          =  -10
PD_CONFIG_ERROR            =  -11
PD_STILL_ACTIVE            =  -12
PD_FUNCTION_NOT_AVAILABLE  =  -13

PD_READ_EMPTY              = -100


#==========================================================================
# GENERAL TYPE DEFINITIONS
#==========================================================================
# Pd handle type definition
# typedef Pd => integer

# Pd version matrix.
#
# This matrix describes the various version dependencies
# of Pd components.  It can be used to determine
# which component caused an incompatibility error.
#
# All version numbers are of the format:
#   (major << 8) | minor
#
# ex. v1.20 would be encoded as:  0x0114
class PdVersion:
    def __init__ (self):
        # Software, firmware, and hardware versions.
        self.software      = 0
        self.firmware      = 0
        self.hardware      = 0

        # Firmware requires that software must be >= this version.
        self.sw_req_by_fw  = 0

        # Software requires that firmware must be >= this version.
        self.fw_req_by_sw  = 0

        # Software requires that the API interface must be >= this version.
        self.api_req_by_sw = 0


#==========================================================================
# GENERAL API
#==========================================================================
# Get a list of ports to which Pd devices are attached.
#
# num_devices = maximum number of elements to return
# devices     = array into which the port numbers are returned
#
# Each element of the array is written with the port number.
# Devices that are in-use are ORed with PD_PORT_NOT_FREE
# (0x8000).
#
# ex.  devices are attached to ports 0, 1, 2
#      ports 0 and 2 are available, and port 1 is in-use.
#      array => 0x0000, 0x8001, 0x0002
#
# If the array is NULL, it is not filled with any values.
# If there are more devices than the array size, only the
# first nmemb port numbers will be written into the array.
#
# Returns the number of devices found, regardless of the
# array size.
PD_PORT_NOT_FREE = 0x8000
def pd_find_devices (devices):
    """usage: (int return, u16[] devices) = pd_find_devices(u16[] devices)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u16(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'H':
            raise TypeError("type for 'devices' must be array('H')")
    # Call API function
    (_ret_) = api.py_pd_find_devices(num_devices, devices)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    return (_ret_, devices)


# Get a list of ports to which Pd devices are attached
#
# This function is the same as pd_find_devices() except that
# it returns the unique IDs of each Pd device.  The IDs
# are guaranteed to be non-zero if valid.
#
# The IDs are the unsigned integer representation of the 10-digit
# serial numbers.
def pd_find_devices_ext (devices, unique_ids):
    """usage: (int return, u16[] devices, u32[] unique_ids) = pd_find_devices_ext(u16[] devices, u32[] unique_ids)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u16(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'H':
            raise TypeError("type for 'devices' must be array('H')")
    # unique_ids pre-processing
    __unique_ids = isinstance(unique_ids, int)
    if __unique_ids:
        (unique_ids, num_ids) = (array_u32(unique_ids), unique_ids)
    else:
        (unique_ids, num_ids) = isinstance(unique_ids, ArrayType) and (unique_ids, len(unique_ids)) or (unique_ids[0], min(len(unique_ids[0]), int(unique_ids[1])))
        if unique_ids.typecode != 'I':
            raise TypeError("type for 'unique_ids' must be array('I')")
    # Call API function
    (_ret_) = api.py_pd_find_devices_ext(num_devices, num_ids, devices, unique_ids)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    # unique_ids post-processing
    if __unique_ids: del unique_ids[max(0, min(_ret_, len(unique_ids))):]
    return (_ret_, devices, unique_ids)


# Open the Pd port.
#
# The port number is a zero-indexed integer.
#
# The port number is the same as that obtained from the
# pd_find_devices() function above.
#
# Returns an Pd handle, which is guaranteed to be
# greater than zero if it is valid.
#
# This function is recommended for use in simple applications
# where extended information is not required.  For more complex
# applications, the use of pd_open_ext() is recommended.
def pd_open (port_number):
    """usage: Pd return = pd_open(int port_number)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_open(port_number)


# Open the Pd port, returning extended information
# in the supplied structure.  Behavior is otherwise identical
# to pd_open() above.  If 0 is passed as the pointer to the
# structure, this function is exactly equivalent to pd_open().
#
# The structure is zeroed before the open is attempted.
# It is filled with whatever information is available.
#
# For example, if the hardware version is not filled, then
# the device could not be queried for its version number.
#
# This function is recommended for use in complex applications
# where extended information is required.  For more simple
# applications, the use of pd_open() is recommended.
class PdExt:
    def __init__ (self):
        # Version matrix
        self.version  = PdVersion()

        # Features of this device.
        self.features = 0

PD_FEATURE_NONE = 0x00000000
PD_FEATURE_USBPD = 0x00000001
PD_FEATURE_USBPD_IV = 0x00000002
def pd_open_ext (port_number):
    """usage: (Pd return, PdExt pd_ext) = pd_open_ext(int port_number)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_pd_ext) = api.py_pd_open_ext(port_number)
    # pd_ext post-processing
    pd_ext = PdExt()
    (pd_ext.version.software, pd_ext.version.firmware, pd_ext.version.hardware, pd_ext.version.sw_req_by_fw, pd_ext.version.fw_req_by_sw, pd_ext.version.api_req_by_sw, pd_ext.features) = c_pd_ext
    return (_ret_, pd_ext)


# Close the Pd port.
def pd_close (pd):
    """usage: int return = pd_close(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_close(pd)


# Return the port for this Pd handle.
#
# The port number is a zero-indexed integer.
def pd_port (pd):
    """usage: int return = pd_port(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_port(pd)


# Return the unique ID for this Pd adapter.
# IDs are guaranteed to be non-zero if valid.
# The ID is the unsigned integer representation of the
# 10-digit serial number.
def pd_unique_id (pd):
    """usage: u32 return = pd_unique_id(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_unique_id(pd)


# Return the status string for the given status code.
# If the code is not valid or the library function cannot
# be loaded, return a NULL string.
def pd_status_string (status):
    """usage: str return = pd_status_string(int status)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_status_string(status)


# Return the version matrix for the device attached to the
# given handle.  If the handle is 0 or invalid, only the
# software and required api versions are set.
def pd_version (pd):
    """usage: (int return, PdVersion version) = pd_version(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_version) = api.py_pd_version(pd)
    # version post-processing
    version = PdVersion()
    (version.software, version.firmware, version.hardware, version.sw_req_by_fw, version.fw_req_by_sw, version.api_req_by_sw) = c_version
    return (_ret_, version)


# Sleep for the specified number of milliseconds
# Accuracy depends on the operating system scheduler
# Returns the number of milliseconds slept
def pd_sleep_ms (milliseconds):
    """usage: u32 return = pd_sleep_ms(u32 milliseconds)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_sleep_ms(milliseconds)



#==========================================================================
# CAPTURE API
#==========================================================================
# Start capturing
def pd_capture_start (pd):
    """usage: int return = pd_capture_start(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_capture_start(pd)


# Stop capturing data
def pd_capture_stop (pd):
    """usage: int return = pd_capture_stop(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pd_capture_stop(pd)



#==========================================================================
# PD CC API
#==========================================================================
# Valid with pd_usbpd_read_bits and pd_usbpd_read_data
PD_STATUS_USBPD_ERR_MASK = 0x0000000f
PD_STATUS_USBPD_ERR_PREAMBLE = 0x00000001
PD_STATUS_USBPD_ERR_SOP = 0x00000002
PD_STATUS_USBPD_ERR_HEADER = 0x00000003
PD_STATUS_USBPD_ERR_DATA = 0x00000004
PD_STATUS_USBPD_ERR_CRC = 0x00000005
PD_STATUS_USBPD_ERR_EOP = 0x00000006
PD_STATUS_USBPD_ERR_BAD_CRC = 0x01000000
PD_STATUS_USBPD_ERR_UNKNOWN_TYPE = 0x02000000
# Valid with pd_usbpd_read_bits and pd_usbpd_read_data
PD_EVENT_USBPD_CC_MASK = 0xf0000000
PD_EVENT_USBPD_CC_SHIFT = 28
PD_EVENT_USBPD_CC1 = 0x00000000
PD_EVENT_USBPD_CC2 = 0x10000000
PD_EVENT_USBPD_POL_CHANGE = 0x00000008
PD_EVENT_USBPD_SOP_MASK = 0x00000007
PD_EVENT_USBPD_SOP = 0x00000000
PD_EVENT_USBPD_SOP_PRIME = 0x00000001
PD_EVENT_USBPD_SOP_DPRIME = 0x00000002
PD_EVENT_USBPD_SOP_PRIME_DEBUG = 0x00000003
PD_EVENT_USBPD_SOP_DPRIME_DEBUG = 0x00000004
PD_EVENT_USBPD_HARD_RESET = 0x00000006
PD_EVENT_USBPD_CABLE_RESET = 0x00000007
PD_EVENT_USBPD_EXTENDED_HEADER = 0x00000010
# Valid only with pd_usbpd_read_iv
PD_EVENT_USBPD_IV_SOURCE_MASK = 0x0f000000
PD_EVENT_USBPD_IV_SHIFT = 24
PD_EVENT_USBPD_IV_VBUS_VOLTAGE = 0x00000000
PD_EVENT_USBPD_IV_VBUS_CURRENT = 0x01000000
PD_EVENT_USBPD_IV_VCONN_VOLTAGE = 0x02000000
PD_EVENT_USBPD_IV_VCONN_CURRENT = 0x03000000
PD_EVENT_USBPD_IV_CC1_VOLTAGE = 0x04000000
PD_EVENT_USBPD_IV_CC2_VOLTAGE = 0x06000000
class PdReadInfo:
    def __init__ (self):
        self.timestamp = 0
        self.duration  = 0
        self.status    = 0
        self.events    = 0

# Read PD bits
def pd_usbpd_read_bits (pd, bits):
    """usage: (int return, PdReadInfo read_info, u32 bits_length, u32 preamble_length, u08[] bits) = pd_usbpd_read_bits(Pd pd, u08[] bits)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # bits pre-processing
    __bits = isinstance(bits, int)
    if __bits:
        (bits, max_bytes) = (array_u08(bits), bits)
    else:
        (bits, max_bytes) = isinstance(bits, ArrayType) and (bits, len(bits)) or (bits[0], min(len(bits[0]), int(bits[1])))
        if bits.typecode != 'B':
            raise TypeError("type for 'bits' must be array('B')")
    # Call API function
    (_ret_, c_read_info, bits_length, preamble_length) = api.py_pd_usbpd_read_bits(pd, max_bytes, bits)
    # read_info post-processing
    read_info = PdReadInfo()
    (read_info.timestamp, read_info.duration, read_info.status, read_info.events) = c_read_info
    # bits post-processing
    if __bits: del bits[max(0, min(_ret_, len(bits))):]
    return (_ret_, read_info, bits_length, preamble_length, bits)


# Decode PD bits
PD_HEADER_USBPD_STANDARD_MASK = 0x0000ffff
PD_HEADER_USBPD_EXTENDED_MASK = 0xffff0000
def pd_usbpd_decode_bits (pd, bits, data):
    """usage: (int return, u32 header, u32 crc, u08[] data) = pd_usbpd_decode_bits(Pd pd, u08[] bits, u08[] data)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # bits pre-processing
    (bits, bytes_length) = isinstance(bits, ArrayType) and (bits, len(bits)) or (bits[0], min(len(bits[0]), int(bits[1])))
    if bits.typecode != 'B':
        raise TypeError("type for 'bits' must be array('B')")
    # data pre-processing
    __data = isinstance(data, int)
    if __data:
        (data, max_bytes) = (array_u08(data), data)
    else:
        (data, max_bytes) = isinstance(data, ArrayType) and (data, len(data)) or (data[0], min(len(data[0]), int(data[1])))
        if data.typecode != 'B':
            raise TypeError("type for 'data' must be array('B')")
    # Call API function
    (_ret_, header, crc) = api.py_pd_usbpd_decode_bits(pd, bytes_length, bits, max_bytes, data)
    # data post-processing
    if __data: del data[max(0, min(_ret_, len(data))):]
    return (_ret_, header, crc, data)


# Read PD data return u08
def pd_usbpd_read_data (pd, data):
    """usage: (int return, PdReadInfo read_info, u32 preamble_length, u32 header, u32 crc, u08[] data) = pd_usbpd_read_data(Pd pd, u08[] data)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # data pre-processing
    __data = isinstance(data, int)
    if __data:
        (data, max_bytes) = (array_u08(data), data)
    else:
        (data, max_bytes) = isinstance(data, ArrayType) and (data, len(data)) or (data[0], min(len(data[0]), int(data[1])))
        if data.typecode != 'B':
            raise TypeError("type for 'data' must be array('B')")
    # Call API function
    (_ret_, c_read_info, preamble_length, header, crc) = api.py_pd_usbpd_read_data(pd, max_bytes, data)
    # read_info post-processing
    read_info = PdReadInfo()
    (read_info.timestamp, read_info.duration, read_info.status, read_info.events) = c_read_info
    # data post-processing
    if __data: del data[max(0, min(_ret_, len(data))):]
    return (_ret_, read_info, preamble_length, header, crc, data)


# Read IV data
def pd_usbpd_read_iv (pd):
    """usage: (int return, PdReadInfo read_info, int val) = pd_usbpd_read_iv(Pd pd)"""

    if not PD_LIBRARY_LOADED: return PD_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_read_info, val) = api.py_pd_usbpd_read_iv(pd)
    # read_info post-processing
    read_info = PdReadInfo()
    (read_info.timestamp, read_info.duration, read_info.status, read_info.events) = c_read_info
    return (_ret_, read_info, val)


