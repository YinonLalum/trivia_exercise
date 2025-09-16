from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Iterable
import random

from questions import TriviaQuestion
from player import Player


@dataclass(frozen=True)
class SubmissionResult:
    correct: bool
    question_completed: bool
    scoring_player: Optional["Player"]
    next_player: Optional["Player"]


@dataclass
class Round:
    question: TriviaQuestion
    players: List[Player]
    current_player_index: int = 0
    _players_asked: int = 0  # Track how many players have been asked in this round

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def advance_player(self) -> None:
        if self.round_over:
            raise RuntimeError("Round is over")
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self._players_asked += 1

    @property
    def round_over(self) -> bool:
        return self._players_asked >= len(self.players) - 1



class Game:
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
        self._scores = {p: 0 for p in self.players}
        self._current_question_index: int = 0
        self._round = None
        self._next_start_index: int = 0

    def start_round(self):
        if self.is_game_over:
            raise RuntimeError("Game is over; no more rounds can be started")
        self._round = Round(
            question=self.current_question,
            players=self.players,
            current_player_index=self._next_start_index,
        )

    def submit_answer(self, player: Player, choice_index: int) -> SubmissionResult:
        if self.is_game_over:
            raise RuntimeError("Game is over; cannot submit answers")
            
        if not self._round:
            self.start_round()

        if player is not self._round.current_player:
            raise RuntimeError(f"It's {self._round.current_player.name}'s turn")

        if self._round.question.is_correct(choice_index):
            self._scores[player] += 1
            self._end_round()
            return SubmissionResult(
                correct=True,
                question_completed=True,
                scoring_player=player,
                next_player=None,
            )
        if self._round.round_over:
            self._end_round()
            return SubmissionResult(
                correct=False,
                question_completed=True,
                scoring_player=None,
                next_player=None,
            )
        self._round.advance_player()
        return SubmissionResult(
            correct=False,
            question_completed=False,
            scoring_player=None,
            next_player=self._round.current_player,
        )


    @property
    def is_game_over(self) -> bool:
        return self._current_question_index >= len(self.questions)

    @property
    def current_question(self) -> TriviaQuestion:
        if self.is_game_over:
            raise RuntimeError("No current question; game is over")
        return self.questions[self._current_question_index]

    @property
    def current_player(self) -> Player:
        if self._round:
            return self._round.current_player

    def _end_round(self):
        self._next_start_index = (self._next_start_index + 1) % len(self.players)
        self._current_question_index += 1
        self._round = None

    @staticmethod
    def load_questions_from_json(objects: Iterable[dict]) -> List[TriviaQuestion]:
        return [TriviaQuestion.from_dict(obj) for obj in objects]
    
    def get_player_score(self,player : Player):
        return self._scores[player]
