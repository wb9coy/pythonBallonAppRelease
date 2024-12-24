import ctypes

c_uint32 = ctypes.c_uint32
c_uint16 = ctypes.c_uint16
c_uint8  = ctypes.c_uint8
c_float  = ctypes.c_float
c_int32  = ctypes.c_int32

# protocol constants
PREAMBLE1 = 0xb5
PREAMBLE2 = 0x62

# message classes
CLASS_NAV = 0x01
CLASS_RXM = 0x02
CLASS_INF = 0x04
CLASS_ACK = 0x05
CLASS_CFG = 0x06
CLASS_MON = 0x0A
CLASS_AID = 0x0B
CLASS_TIM = 0x0D
CLASS_ESF = 0x10

# ACK messages
MSG_ACK_NACK = 0x00
MSG_ACK_ACK = 0x01

# NAV messages
MSG_NAV_POSECEF   = 0x1
MSG_NAV_POSLLH    = 0x2
MSG_NAV_STATUS    = 0x3
MSG_NAV_DOP       = 0x4
MSG_NAV_SOL       = 0x6
MSG_NAV_POSUTM    = 0x8
MSG_NAV_VELNED    = 0x12
MSG_NAV_VELECEF   = 0x11
MSG_NAV_TIMEGPS   = 0x20
MSG_NAV_TIMEUTC   = 0x21
MSG_NAV_CLOCK     = 0x22
MSG_NAV_SVINFO    = 0x30
MSG_NAV_AOPSTATUS = 0x60
MSG_NAV_DGPS      = 0x31
MSG_NAV_DOP       = 0x04
MSG_NAV_EKFSTATUS = 0x40
MSG_NAV_SBAS      = 0x32
MSG_NAV_SOL       = 0x06

# RXM messages
MSG_RXM_RAW    = 0x10
MSG_RXM_SFRB   = 0x11
MSG_RXM_SVSI   = 0x20
MSG_RXM_EPH    = 0x31
MSG_RXM_ALM    = 0x30
MSG_RXM_PMREQ  = 0x41

# AID messages
MSG_AID_ALM    = 0x30
MSG_AID_EPH    = 0x31
MSG_AID_ALPSRV = 0x32
MSG_AID_AOP    = 0x33
MSG_AID_DATA   = 0x10
MSG_AID_ALP    = 0x50
MSG_AID_DATA   = 0x10
MSG_AID_HUI    = 0x02
MSG_AID_INI    = 0x01
MSG_AID_REQ    = 0x00

# CFG messages
MSG_CFG_PRT = 0x00
MSG_CFG_ANT = 0x13
MSG_CFG_DAT = 0x06
MSG_CFG_EKF = 0x12
MSG_CFG_ESFGWT = 0x29
MSG_CFG_CFG = 0x09
MSG_CFG_USB = 0x1b
MSG_CFG_RATE = 0x08
MSG_CFG_SET_RATE = 0x01
MSG_CFG_NAV5 = 0x24
MSG_CFG_FXN = 0x0E
MSG_CFG_INF = 0x02
MSG_CFG_ITFM = 0x39
MSG_CFG_MSG = 0x01
MSG_CFG_NAVX5 = 0x23
MSG_CFG_NMEA = 0x17
MSG_CFG_NVS = 0x22
MSG_CFG_PM2 = 0x3B
MSG_CFG_PM = 0x32
MSG_CFG_RINV = 0x34
MSG_CFG_RST = 0x04
MSG_CFG_RXM = 0x11
MSG_CFG_SBAS = 0x16
MSG_CFG_TMODE2 = 0x3D
MSG_CFG_TMODE = 0x1D
MSG_CFG_TPS = 0x31
MSG_CFG_TP = 0x07
MSG_CFG_GNSS = 0x3E

# ESF messages
MSG_ESF_MEAS   = 0x02
MSG_ESF_STATUS = 0x10

# INF messages
MSG_INF_DEBUG  = 0x04
MSG_INF_ERROR  = 0x00
MSG_INF_NOTICE = 0x02
MSG_INF_TEST   = 0x03
MSG_INF_WARNING= 0x01

# MON messages
MSG_MON_SCHD  = 0x01
MSG_MON_HW    = 0x09
MSG_MON_HW2   = 0x0B
MSG_MON_IO    = 0x02
MSG_MON_MSGPP = 0x06
MSG_MON_RXBUF = 0x07
MSG_MON_RXR   = 0x21
MSG_MON_TXBUF = 0x08
MSG_MON_VER   = 0x04

# TIM messages
MSG_TIM_TP   = 0x01
MSG_TIM_TM2  = 0x03
MSG_TIM_SVIN = 0x04
MSG_TIM_VRFY = 0x06

RESET_CMD    = 0xFF
NUM_CONFIG_BLOCKS = 5
GPS_ID     = 0x00
SBAS_ID    = 0x01
BeiDou_ID  = 0x03
QZSS_ID    = 0x05
GLONASS_ID = 0x06

class ubloxPacketSyncType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("sync1",         c_uint8),
        ("sync2",         c_uint8)
        ]

class ubloxPacketHeaderType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("Class",   c_uint8),
        ("id",      c_uint8),
        ("length",  c_uint16)
        ]

class ubloxPacketCkType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("cka",         c_uint8),
        ("ckb",         c_uint8)
        ]
    
class gnssConfigBlock(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("gnssId",      c_uint8),
        ("resTrkCh",    c_uint8),
        ("maxTrkCh",    c_uint8),
        ("reserved1",   c_uint8),
        ("flags",       c_uint8*4)
        ]    

class UBXCFGNAV5Type(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("mask",              c_uint16),
        ("dynModel",          c_uint8),
        ("fixMode",           c_uint8),
        ("fixedAlt",          c_int32),
        ("fixedAltVar",       c_uint32),
        ("minElev",           c_uint8),
        ("drLimit",           c_uint8),
        ("pDop",              c_uint16),
        ("tDop",              c_uint16),
        ("pAcc",              c_uint16),
        ("tAcc",              c_uint16),
        ("staticHoldThresh",  c_uint8),
        ("dgnssTimeout",      c_uint8),
        ("cnoThreshNumSVs",   c_uint8),
        ("cnoThresh",         c_uint8),
        ("reserved1",         c_uint8*2),
        ("staticHoldMaxDist", c_uint16),
        ("utcStandard",       c_uint8),
        ("reserved2",         c_uint8*5)
        ]
    
class UBXCFGGNSSType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("msgVer",            c_uint8),
        ("numTrkChHw",        c_uint8),
        ("numTrkChUse",       c_uint8),
        ("numConfigBlocks",    c_uint8),
        ("gnssConfigBlock",   gnssConfigBlock*NUM_CONFIG_BLOCKS)
        ]
        
class UBXCFGRXMType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("reserved1",   c_uint8),
        ("lpMode",      c_uint8)
        ]    
