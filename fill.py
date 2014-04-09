import os
import random

FILE = 'text.txt'
file_size = os.stat(FILE).st_size

# Создать тему
def make_topic(file_str, file_size):
    '''
    Функция открывает файл со случайным смещением и
    и возвращает от 1 до 3 слов, идущих подряд
    '''
    
    random.seed()
    offset = random.randrange(0, file_size-1)
    file = open(file_str)
    file.seek(offset)

    topic = ''
    started = False
    end = [' ', '.', '!', '?', '\n']
    number = random.randrange(1, 4)
    for line in file:
        for char in line:
            # Если слово ещё не началось
            if not started:
                if char not in end:
                    continue
                else:
                    started = True
            # Если предложение уже в записи
            else:
                # Ждать один из символов окончания предложения
                if char in end:
                    topic += char
                    number -= 1
                    break
                # Если не конец, то продолжать записывать предложение
                else:
                    topic += char            
        if not number and started and topic[-1] in end:
            topic = topic.replace('\n', ' ')[:-1]
            return(topic)
    
    
# Создать сообщение
def make_message(file_str, file_size):
    '''
    Функция открывает файл со случайным смещением и
    и возвращает от 1 до 7 предложений, идущих подряд
    '''
    
    random.seed()
    offset = random.randrange(0, file_size-1)
    file = open(file_str)
    file.seek(offset)
    
    message = ''
    started = False
    end = ['.', '!', '?']
    number = random.randrange(1, 8)
    for line in file:
        for char in line:
            # Если предложение ещё не началось
            if not started:
                if char not in end:
                    continue
                else:
                    started = True
            # Если предложение уже в записи
            else:
                # Ждать один из символов окончания предложения
                if char in end:
                    message += char
                    number -= 1
                    break
                # Если не конец, то продолжать записывать предложение
                else:
                    message += char            
        if not number and started and message[-1] in end:
            message = message.replace('\n', ' ')
            return(message)

print(make_topic(FILE, file_size))