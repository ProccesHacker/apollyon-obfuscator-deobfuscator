# Apollyon Deobfuscator

Деобфускатор для файлов, обфусцированных Apollyon.

## Возможности

- достаёт payload из marshal.loads;
- поддерживает .py, .pyc, .zip и папки с src/_run.py;
- восстанавливает Kyrie-шифрование, сдвиг алфавита и ζ-переносы строк;
- ищет ключи автоматически;
- не запускает обфусцированный файл и не требует apollyon.pyd.

## Использование

Запуск:

```bash
python deapollyon.py obfuscated.zip
```

С сохранением результата в файл:

```bash
python deapollyon.py
```

Также можно указать .py, .pyc или папку:

```bash
python deapollyon.py src/_run.py -o clean.py
```

```bash
python deapollyon.py obfuscated.pyc -o clean.py
```

Также можно использовать из Python:

```python
from deapollyon import proc

proc("obfuscated.zip")
```

По умолчанию результат сохраняется рядом с исходным файлом с суффиксом `_deobf.py`.

## Обфускатор

https://github.com/billythegoat356/Apollyon — это исходный обфускатор.

## Требования

- Python 3.8+

## Примечание

Инструмент предназначен для деобфускации файлов что были обфусцированы Apollyon.
