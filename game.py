from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Iterable
import random

from .questions import TriviaQuestion


@dataclass(frozen=True)
class RoundResult:
    correct: bool
    round_ended: bool
    question_advanced: bool
    scoring_player: Optional["Player"]
    next_player: Optional["Player"]


@dataclass(frozen=True)
class Attempt:
    choice_index: int


@dataclass
class Player:
    name: str
    score: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Player name must be a non-empty string")

    def submit_answer(self, choice_index: int) -> Attempt:
        return Attempt(choice_index=choice_index)


class Game:
    """Trivia game engine with rounds, scoring, and turn rotation.

    Rules implemented:
    - Questions are randomized once at the beginning of the game.
    - A round is tied to a single question.
    - The first player answers first; if wrong, the next player gets a chance, etc.
    - If all players answer incorrectly once, the round ends with no points and the game moves on.
    - Any number of players is supported (>= 1).
    """

    def __init__(
        self,
        players: Iterable[Player],
        questions: List[TriviaQuestion]
    ) -> None:
        player_list = [p for p in players if isinstance(p, Player)]
        if not player_list:
            raise ValueError("At least one valid player name is required")
        if not questions:
            raise ValueError("At least one question is required")

        self.players = player_list

        self.questions = list(questions)
        random.shuffle(self.questions)

        self._current_question_index: int = 0
        self._current_player_index: int = 0
        self._attempts_this_round: int = 0
        self._in_round: bool = False

    def start_round(self) -> TriviaQuestion:
        if self.is_game_over():
            raise RuntimeError("Game is over; no more rounds can be started")
        self._in_round = True
        self._attempts_this_round = 0
        self._current_player_index = 0
        return self.current_question

    def resolve_attempt(self, player: Player, attempt: Attempt) -> RoundResult:
        """Apply a player's attempt to the current round.

        Enforces turn order and advances state accordingly.
        """
        if self.is_game_over():
            raise RuntimeError("Game is over; cannot submit answers")
        if not self._in_round:
            self.start_round()

        if player is not self.current_player:
            raise RuntimeError(f"It's {self.current_player.name}'s turn")

        if self.current_question.is_correct(attempt.choice_index):
            player.score += 1
            self._end_round(advance_question=True)
            return RoundResult(
                correct=True,
                round_ended=True,
                question_advanced=True,
                scoring_player=player,
                next_player=self.current_player if not self.is_game_over() else None,
            )

        # Incorrect answer; move to next player or end the round if all tried once
        self._attempts_this_round += 1
        if self._attempts_this_round >= len(self.players):
            self._end_round(advance_question=True)
            return RoundResult(
                correct=False,
                round_ended=True,
                question_advanced=True,
                scoring_player=None,
                next_player=self.current_player if not self.is_game_over() else None,
            )

        # Pass turn to next player
        self._current_player_index = (self._current_player_index + 1) % len(self.players)
        return RoundResult(
            correct=False,
            round_ended=False,
            question_advanced=False,
            scoring_player=None,
            next_player=self.current_player,
        )

    def is_game_over(self) -> bool:
        return self._current_question_index >= len(self.questions)

    def get_scores(self) -> Dict[str, int]:
        return {p.name: p.score for p in self.players}

    @property
    def current_question(self) -> TriviaQuestion:
        if self.is_game_over():
            raise RuntimeError("No current question; game is over")
        return self.questions[self._current_question_index]

    @property
    def current_player(self) -> Player:
        return self.players[self._current_player_index]

    def _end_round(self, advance_question: bool) -> None:
        self._in_round = False
        self._attempts_this_round = 0
        self._current_player_index = 0
        if advance_question:
            self._current_question_index += 1


def load_questions_from_json(objects: Iterable[dict]) -> List[TriviaQuestion]:
    """Utility to convert iterable of dicts to `TriviaQuestion` instances.

    Expected dict schema matches `TriviaQuestion.from_dict`.
    """
    return [TriviaQuestion.from_dict(obj) for obj in objects]

