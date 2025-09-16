from __future__ import annotations
import logging
from typing import TextIO, TYPE_CHECKING
from game import Game, SubmissionResult
import sys

from player import Player
if TYPE_CHECKING:
    from questions import TriviaQuestion


class UI:
    def __init__(self, game: Game, output_stream: TextIO = sys.stdout):
        self.game = game
        self._out = output_stream
        self._logger = logging.getLogger(__name__)

    def prompt_category(self) -> str:
        categories = self.game.available_categories()
        if not categories:
            raise RuntimeError("No categories available")
        if len(categories) == 1:
            return categories[0]
        self._writeln("Choose a category:")
        for idx, cat in enumerate(categories):
            self._writeln(f"{idx + 1}. {cat}")
        while True:
            try:
                choice = input("Enter the number of your category: ").strip()
                if not choice.isdigit():
                    self._logger.warning("Please enter a valid number.")
                    continue
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(categories):
                    return categories[choice_index]
                else:
                    self._logger.warning(f"Please enter a number between 1 and {len(categories)}.")
            except Exception as exc:
                self._logger.error(f"Error: {exc}")

    def prompt_player_for_answer(self, player: Player, question: TriviaQuestion) -> int:
        self._writeln(f"{player.name}, it's your turn!")
        self._writeln(str(question))
        while True:
            try:
                choice = input("Enter the number of your answer(0 to skip): ").strip()
                if not choice.isdigit():
                    self._logger.warning("Please enter a valid number.")
                    continue
                choice_index = int(choice) - 1
                if -1 <= choice_index < len(question.options):
                    return choice_index
                else:
                    self._logger.warning(f"Please enter a number between 1 and {len(question.options)}.")
            except Exception as exc:
                self._logger.error(f"Error: {exc}")

    def show_submission_result(self, result: SubmissionResult) -> None:
        if result.skipped:
            self._writeln(f"{self.game.current_player.name} has {self.game.remaining_skips[self.game.current_player]} skips left!")
        else:
            if result.correct:
                self._writeln("Correct!")
            else:
                self._writeln("Incorrect.")
        if result.question_completed:
            self._writeln("Moving to next question...\n")

    def show_final_scores(self) -> None:
        self._writeln("\nGame Over! Final Scores:")
        for player in self.game.players:
            self._writeln(f"{player.name}: {self.game.get_player_score(player)}")

    def _writeln(self, text: str) -> None:
        self._out.write(f"{text}\n")
        try:
            self._out.flush()
        except Exception:
            pass


