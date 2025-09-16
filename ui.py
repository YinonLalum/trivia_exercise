import logging
from game import Game
import sys


class UI:
    def __init__(self, game: Game, output_stream=sys.stdout):
        self.game = game
        self._out = output_stream
        self._logger = logging.getLogger(__name__)

    def prompt_player_for_answer(self, player, question):
        self._writeln(f"{player.name}, it's your turn!")
        self._writeln(str(question))
        while True:
            try:
                choice = input("Enter the number of your answer: ").strip()
                if not choice.isdigit():
                    self._logger.warning("Please enter a valid number.")
                    continue
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(question.options):
                    return choice_index
                else:
                    self._logger.warning(f"Please enter a number between 1 and {len(question.options)}.")
            except Exception as exc:
                self._logger.error(f"Error: {exc}")

    def show_submission_result(self, result):
        if result.correct:
            self._writeln("Correct!")
            if result.scoring_player:
                self._writeln(f"{result.scoring_player.name} scores a point!")
        else:
            self._writeln("Incorrect.")
        if result.question_completed:
            self._writeln("Moving to next question...\n")
        elif result.next_player:
            self._writeln(f"Next up: {result.next_player.name}")

    def show_final_scores(self):
        self._writeln("\nGame Over! Final Scores:")
        for player in self.game.players:
            self._writeln(f"{player.name}: {self.game.get_player_score(player)}")

    def _writeln(self, text: str):
        self._out.write(f"{text}\n")
        try:
            self._out.flush()
        except Exception:
            pass


