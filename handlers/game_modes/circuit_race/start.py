from ..modes import CircuitRace
from .preparation import show_players, select_circuit, show_race_info, select_tires, generate_cards
from .race import start, hold_race, summarize_results, clear_race_data


async def start_circuit_race(race: CircuitRace):
    # await show_players(race)
    await select_circuit(race)
    await show_race_info(race)
    await select_tires(race)
    await generate_cards(race)
    await start(race)
    await hold_race(race)
    await summarize_results(race)
    clear_race_data(race)
