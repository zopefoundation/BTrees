# Copied from ZODB/utils.py

from binascii import hexlify
from struct import calcsize

_ADDRESS_MASK = 256 ** calcsize('P')

def positive_id(obj):
    """Return id(obj) as a non-negative integer."""

    result = id(obj)
    if result < 0:
        result += _ADDRESS_MASK
        assert result > 0
    return result

def oid_repr(oid):
    if isinstance(oid, str) and len(oid) == 8:
        # Convert to hex and strip leading zeroes.
        as_hex = hexlify(oid).lstrip('0')
        # Ensure two characters per input byte.
        if len(as_hex) & 1:
            as_hex = '0' + as_hex
        elif as_hex == '':
            as_hex = '00'
        return '0x' + as_hex
    else:
        return repr(oid)
