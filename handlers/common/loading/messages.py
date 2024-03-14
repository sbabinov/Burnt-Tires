from typing import List


def clock_animation(message: str) -> List[str]:
    clock_emoji = '🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚'
    frames = []
    dot = 1
    for clock in clock_emoji:
        frame = message.replace('CLOCK', clock)
        frame += '.' * dot
        frames.append(frame)
        dot += 1
        if dot > 3:
            dot = 1
    return frames


loading_messages = {
    'default': ['Загрузка.', 'Загрузка..', 'Загрузка...'],
    'preparing_for_race': ['🏁 Подготавливаем трассу.', '🏁 Подготавливаем трассу..', '🏁 Подготавливаем трассу...'],
    'waiting_for_choice': ['⌛️ Ждём выбора игрока.', '⏳ Ждём выбора игрока..', '⌛️ Ждём выбора игрока...'],
    'finishing_race': ['🏁 Завершаем гонку.', '🏁 Завершаем гонку..', '🏁 Завершаем гонку...'],
    'waiting_for_move': ['🎲 Ждём следующего хода.', '🎲 Ждём следующего хода..', '🎲 Ждём следующего хода...'],
    'clock': clock_animation('CLOCK Ждём остальных игроков'),
    'game_results': ['🏆 Игра окончена! Подсчитываем результаты.', '🏆 Игра окончена! Подсчитываем результаты..',
                     '🏆 Игра окончена! Подсчитываем результаты...']
}
