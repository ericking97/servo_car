from machine import Pin, UART


class UARTController:
    """
    Reads single byte commands from a UART connection.

    Attributes:
        _uart (UART): Micropython UART instance

    Example:
        >>> ctrl = UARTController(Pin(0), Pin(1))
        >>> command = ctrl.read_command()
    """
    _uart: UART

    def __init__(self, tx: Pin, rx: Pin):
        """
        """
        self._uart = UART(0, 9_600, tx=tx, rx=rx)

    def read_command(self) -> str | None:
        """
        Read and return the next single-byte command from the UART buffer.

        :returns: Single lowercase character string if a byte is available,
            or ``None`` if the buffer was empty or decoding produced an 
            empty string.
        """
        if not self._uart.any():
            return None

        data = self._uart.read()
        if not data:
            return None
        return data.decode("utf-8").strip().lower() or None
