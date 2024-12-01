import json


def interpret(binary_file, result_file, memory_range):
    with open(binary_file, "rb") as f:
        data = f.read()

    memory = [0] * 50  # Простая модель памяти
    program_counter = 0
    log_data = []  # Лог выполнения инструкций
    execution_steps = []  # Пошаговый результат выполнения

    while program_counter < len(data):
        # Читаем 5 байт команды
        instruction_bytes = data[program_counter:program_counter + 5]
        program_counter += 5

        if len(instruction_bytes) < 5:
            break  # Конец файла, если данных меньше 5 байт

        # Распаковка команды
        instruction = int.from_bytes(instruction_bytes, "little")
        A = instruction & 0x7F  # Первые 7 бит
        B = (instruction >> 7) & 0x7F  # Вторые 7 бит
        C = (instruction >> 14) & 0x3FFF  # Следующие 8 бит

        # Выполнение команды
        if A == 121:  # LOAD_CONST
            memory[B] = C
            execution_steps.append([f"LOAD_CONST: R{B} <- {C}"])
        elif A == 18:  # READ_MEM
            value = memory[memory[C]]
            memory[B] = value
            execution_steps.append([f"READ_MEM: R{B} <- M{memory[C]} "])
        elif A == 44:  # WRITE_MEM
            memory[B] = memory[C]
            execution_steps.append([f"WRITE_MEM: M{C} <- R{B} "])
        elif A == 4:  # MOD
            if memory[C] != 0:  # Проверка делителя на 0
                result = memory[B] % memory[C]
                memory[B] = result
                execution_steps.append(
                    [f"MOD: R{B} <- {memory[B]} % {memory[C]} = {result}"]
                )
            else:
                execution_steps.append([f"MOD: R{B} <- {memory[B]} % {memory[C]} = ERROR (div by 0)"])

        # Логируем инструкцию
        log_data.append({
            "bytes": [f"0x{b:02X}" for b in instruction_bytes],
            "A": A,
            "B": B,
            "C": C,
        })

    # Формируем итоговый результат
    result = {
        "memory": memory[memory_range[0]:memory_range[1]],
        "log": log_data,
        "execution_steps": execution_steps
    }

    # Записываем результат в JSON файл
    with open(result_file, "w") as f:
        json.dump(result, f, indent=4)

