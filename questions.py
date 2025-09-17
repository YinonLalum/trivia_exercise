import html
from pickle import DICT
from typing import List, Dict, Any
import random

DIFFICULTY_SCORES = {"easy": 1, "medium": 2, "hard": 3}


class TriviaQuestion:
    def __init__(self, question: str, options: List[str], answer: str, category: str, difficulty: str) -> None:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")
        if not isinstance(options, list) or len(options) < 1:
            raise ValueError(
                "Options must be a list with at least one choice.")
        if not all(isinstance(opt, str) and opt.strip() for opt in options):
            raise ValueError("All options must be non-empty strings.")
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category must be a non-empty string.")
        if not isinstance(difficulty, str) or difficulty not in DIFFICULTY_SCORES.keys():
            raise ValueError("Difficulty must be one of known levels!")

        self.question = question
        self.category = category
        self.score = DIFFICULTY_SCORES[difficulty]
        options = list(options)
        options.append(answer)
        answer_idx = len(options) - 1
        # Randomize options and keep track of the correct answer index
        option_tuples = list(enumerate(options))
        random.shuffle(option_tuples)
        self.options = [opt for _, opt in option_tuples]
        for new_idx, (orig_idx, _) in enumerate(option_tuples):
            if orig_idx == answer_idx:
                self.answer = new_idx
                break

    def is_correct(self, choice_index: int) -> bool:
        return choice_index == self.answer

    def __str__(self) -> str:
        options_str = "\n".join(
            f"{idx + 1}. {opt}" for idx, opt in enumerate(self.options))
        return f"[{self.category}][{self.score} Points] {self.question}\n{options_str}"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TriviaQuestion":
        if not isinstance(data, dict):
            raise ValueError("Each question must be a dictionary.")
        required_keys = {"question", "incorrect_answers",
                         "correct_answer", "category", "difficulty"}
        if not required_keys.issubset(data):
            missing = required_keys - set(data)
            raise ValueError(f"Missing keys in question: {missing}")
        return TriviaQuestion(
            question=html.unescape(data["question"]),
            options=[html.unescape(o) for o in data["incorrect_answers"]],
            answer=html.unescape(data["correct_answer"]),
            category=html.unescape(data["category"]),
            difficulty=html.unescape(data["difficulty"])
        )
