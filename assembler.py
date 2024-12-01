import argparse
import json

COMMANDS = {
    "LOAD_CONST": 121,  # A = 121
    "READ_MEM": 18,    # A = 18
    "WRITE_MEM": 44,   # A = 44
    "MOD": 4           # A = 4
}


def pack_instruction(fields):
    """
    Упаковывает инструкцию, формируя ее справа налево, дополняя до 5 байт нулями в начале,
    и переворачивает порядок байтов.
    :param fields: Список кортежей (значение, размер_в_битах), где:
        - значение: значение поля
        - размер_в_битах: количество бит, занимаемое этим полем
    :return: Упакованная инструкция в виде ровно 5 байт с перевёрнутым порядком байтов
    """
    instruction = 0
    total_bits = 0

    # Формирование инструкции справа налево
    for value, size in reversed(fields):
        if value >= (1 << size):
            raise ValueError(f"Значение {value} превышает допустимое для {size} бит.")
        instruction = (instruction << size) | value
        total_bits += size

    # Преобразование инструкции в байты
    num_bytes = (total_bits + 7) // 8
    byte_array = instruction.to_bytes(num_bytes, byteorder='big')

    # Дополнение до 5 байт нулями в начале
    padded_array = byte_array.rjust(5, b'\x00')

    # Переворот порядка байтов
    reversed_array = padded_array[::-1]

    return reversed_array

