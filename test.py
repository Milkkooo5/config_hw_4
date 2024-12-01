import unittest
import json
import os
from assembler import assemble, pack_instruction
from interpreter import interpret


class TestAssemblerAndInterpreter(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для тестов
        self.input_file = "test_input.asm"
        self.output_file = "test_output.bin"
        self.log_file = "test_log.json"
        self.result_file = "test_result.json"

    def tearDown(self):
        # Удаляем временные файлы после тестов
        for file in [self.input_file, self.output_file, self.log_file, self.result_file]:
            if os.path.exists(file):
                os.remove(file)

    def write_input_file(self, lines):
        """Утилита для записи тестового входного файла."""
        with open(self.input_file, "w") as f:
            f.write("\n".join(lines))

    def test_assemble_and_interpret_load_const(self):
        # Входные данные для ассемблера
        input_lines = [
            "LOAD_CONST 5 12345",
            "LOAD_CONST 6 1234"  # Исправлено значение
        ]
        self.write_input_file(input_lines)

        # Выполняем сборку
        assemble(self.input_file, self.output_file, self.log_file)

        # Проверяем, что бинарный файл создан
        self.assertTrue(os.path.exists(self.output_file))

        # Выполняем интерпретацию
        interpret(self.output_file, self.result_file, (0, 10))

        # Проверяем результат выполнения
        with open(self.result_file, "r") as f:
            result = json.load(f)

        # Проверяем память
        expected_memory = [0] * 50
        expected_memory[5] = 12345
        expected_memory[6] = 1234  # Обновленное значение
        self.assertEqual(result["memory"], expected_memory[:10])

    def test_assemble_and_interpret_mod(self):
        # Входные данные для ассемблера
        input_lines = [
            "LOAD_CONST 5 10",
            "LOAD_CONST 6 3",
            "MOD 5 6"
        ]
        self.write_input_file(input_lines)

        # Выполняем сборку
        assemble(self.input_file, self.output_file, self.log_file)

        # Проверяем, что бинарный файл создан
        self.assertTrue(os.path.exists(self.output_file))

        # Выполняем интерпретацию
        interpret(self.output_file, self.result_file, (0, 10))

        # Проверяем результат выполнения
        with open(self.result_file, "r") as f:
            result = json.load(f)

        # Проверяем память
        expected_memory = [0] * 50
        expected_memory[5] = 1  # 10 % 3 = 1
        expected_memory[6] = 3
        self.assertEqual(result["memory"], expected_memory[:10])

    def test_invalid_command(self):
        # Входные данные с ошибочной командой
        input_lines = ["INVALID_CMD 5 10"]
        self.write_input_file(input_lines)

        with self.assertRaises(ValueError) as context:
            assemble(self.input_file, self.output_file, self.log_file)

        self.assertIn("Неизвестная команда", str(context.exception))

    def test_log_format(self):
        # Входные данные для проверки логов
        input_lines = [
            "LOAD_CONST 2 255",
            "READ_MEM 3 2"
        ]
        self.write_input_file(input_lines)

        # Выполняем сборку
        assemble(self.input_file, self.output_file, self.log_file)

        # Проверяем содержимое логов
        with open(self.log_file, "r") as f:
            logs = json.load(f)

        self.assertEqual(logs[0]["command"], "LOAD_CONST")
        self.assertEqual(logs[0]["A"], 121)  # LOAD_CONST
        self.assertEqual(logs[0]["B"], 2)
        self.assertEqual(logs[0]["C"], 255)

        self.assertEqual(logs[1]["command"], "READ_MEM")
        self.assertEqual(logs[1]["A"], 18)  # READ_MEM
        self.assertEqual(logs[1]["B"], 3)
        self.assertEqual(logs[1]["C"], 2)

    def test_divide_by_zero(self):
        # Входные данные для команды MOD с делением на ноль
        input_lines = [
            "LOAD_CONST 5 10",
            "LOAD_CONST 6 0",
            "MOD 5 6"
        ]
        self.write_input_file(input_lines)

        # Выполняем сборку
        assemble(self.input_file, self.output_file, self.log_file)

        # Выполняем интерпретацию
        interpret(self.output_file, self.result_file, (0, 10))

        # Проверяем результат выполнения
        with open(self.result_file, "r") as f:
            result = json.load(f)

        # Проверяем, что деление на ноль обработано
        self.assertIn("ERROR (div by 0)", result["execution_steps"][-1][0])


if __name__ == "__main__":
    unittest.main()
