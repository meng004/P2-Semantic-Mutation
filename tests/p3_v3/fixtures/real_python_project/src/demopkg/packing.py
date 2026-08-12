"""Binary packing helpers for the demo fixture."""

import struct


def pack(payload: bytes) -> bytes:
    return struct.pack("<I", len(payload)) + payload
