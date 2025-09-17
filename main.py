import argparse
import json
from pathlib import Path
import sys
import logging
from typing import Any, List

from game import Game, NoMoreSkipsError
from ui import UI
from player import Player

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def parse_arguments(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A Trivia Game!"
    )
    parser.add_argument(
        "--json_file",
        help="Path to the questions json",
        action="store",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--question_count",
        help="How many questions should be in the game",
        action="store",
        default=10,
        type=int
    )
    parser.add_argument(
        "--players_count",
        action="store",
        type=int,
        default=2,
        help="Number of players (default 2)",
    )
    return parser.parse_args(argv)


def load_json_file(file_path: str) -> Any:
    path = Path(file_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Not a file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

 

def main(argv: List[str] | None = None) -> int:
    args = parse_arguments(argv)
    if args.json_file:
        try:
            data = load_json_file(args.json_file)
        except FileNotFoundError as exc:
            logger.error(str(exc))
            return 2
        except IsADirectoryError as exc:
            logger.error(str(exc))
            return 2
        except json.JSONDecodeError as exc:
            location = f"line {exc.lineno}, column {exc.colno}"
            logger.error(f"Invalid JSON in {args.json_file}: {exc.msg} ({location})")
            return 3
        except Exception as exc:
            logger.error(f"Unexpected error reading {args.json_file}: {exc}")
            return 1
        questions = Game.load_questions_from_json(data)
    else:
        questions = Game.load_questions_from_api(args.question_count)
    players = []
    for i in range(args.players_count):
        input_name = input(f"Enter name for player {i+1}: ")
        players.append(Player(input_name))

    game = Game(players, questions)
    ui = UI(game)
    while not game.is_game_over:
        category = ui.prompt_category()
        game.start_round(category)
        while not game.round_over:
            choice_index = ui.prompt_player_for_answer(game.current_player, game.current_question)
            try:
                result = game.submit_answer(game.current_player, choice_index)
            except NoMoreSkipsError as e:
                logging.warning(e)
                continue
            ui.show_submission_result(result)
    ui.show_final_scores()
    return 0


if __name__ == "__main__":
    sys.exit(main())