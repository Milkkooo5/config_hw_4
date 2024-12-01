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

def assemble(input_file, output_file, log_file):
    binary_output = bytearray()
    log_output = []

    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            cmd = parts[0]
            args = list(map(int, parts[1:]))

            if cmd == "LOAD_CONST":
                opcode = COMMANDS[cmd]  # Опкод (A)
                b = args[0]  # Поле B (Адрес)
                c = args[1]  # Поле C (Константа)

                # Упаковываем инструкцию, начиная с младших бит
                fields = [
                    (opcode, 7),  # A: 7 бит
                    (b, 7),       # B: 7 бит
                    (c, 14)       # C: 14 бит
                ]
                instruction = pack_instruction(fields)

            elif cmd == "READ_MEM":
                opcode = COMMANDS[cmd]  # Опкод (A)
                b = args[0]  # Поле B
                c = args[1]  # Поле C

                fields = [
                    (opcode, 7),  # A: 7 бит
                    (b, 7),       # B: 7 бит
                    (c, 7)        # C: 7 бит
                ]
                instruction = pack_instruction(fields)

            elif cmd == "WRITE_MEM":
                opcode = COMMANDS[cmd]  # Опкод (A)
                b = args[0]  # Поле B
                c = args[1]  # Поле C

                fields = [
                    (opcode, 7),  # A: 7 бит
                    (b, 7),       # B: 7 бит
                    (c, 9)        # C: 9 бит
                ]
                instruction = pack_instruction(fields)

            elif cmd == "MOD":
                opcode = COMMANDS[cmd]  # Опкод (A)
                b = args[0]  # Поле B
                c = args[1]  # Поле C

                fields = [
                    (opcode, 7),  # A: 7 бит
                    (b, 7),       # B: 7 бит
                    (c, 7)        # C: 7 бит
                ]
                instruction = pack_instruction(fields)

            else:
                raise ValueError(f"Неизвестная команда: {cmd}")

            # Добавляем инструкцию в бинарный файл
            binary_output.extend(instruction)

            # Логируем инструкцию (переместили поле A перед командой)
            log_output.append({
                "A": opcode,  # Сначала сохраняем значение A (опкод)
                "command": cmd,  # Команда
                "B": args[0],
                "C": args[1],
                "bytes": [f'0x{byte:02X}' for byte in instruction]
            })

    # Сохраняем бинарный файл
    with open(output_file, 'wb') as f:
        f.write(binary_output)

    # Сохраняем лог файл в JSON
    with open(log_file, 'w') as f:
        json.dump(log_output, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for UVM")
    parser.add_argument("input", help="Input file with assembly code")
    parser.add_argument("output", help="Output binary file")
    parser.add_argument("log", help="Log file in JSON format")
    args = parser.parse_args()
