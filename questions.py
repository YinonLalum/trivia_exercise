from typing import List, Dict, Any

# Define the constant set of allowed categories
ALLOWED_CATEGORIES: List[str] = [
    "Geography",
    "Science",
    "Literature",
    "General",
]

class TriviaQuestion:
    def __init__(self, question: str, options: List[str], answer: int, category: str) -> None:
        import random
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")
        if not isinstance(options, list) or len(options) < 2:
            raise ValueError("Options must be a list with at least two choices.")
        if not all(isinstance(opt, str) and opt.strip() for opt in options):
            raise ValueError("All options must be non-empty strings.")
        if not isinstance(answer, int) or not (0 <= answer < len(options)):
            raise ValueError("Answer must be an integer index within the range of options.")
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category must be a non-empty string.")
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category '{category}' is not allowed. Allowed: {ALLOWED_CATEGORIES}")

        self.question = question
        self.category = category

        # Randomize options and keep track of the correct answer index
        option_tuples = list(enumerate(options))
        random.shuffle(option_tuples)
        self.options = [opt for idx, opt in option_tuples]
        for new_idx, (orig_idx, _) in enumerate(option_tuples):
            if orig_idx == answer:
                self.answer = new_idx
                break

    def is_correct(self, choice_index: int) -> bool:
        return choice_index == self.answer

    def __str__(self) -> str:
        options_str = "\n".join(f"{idx + 1}. {opt}" for idx, opt in enumerate(self.options))
        return f"[{self.category}] {self.question}\n{options_str}"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TriviaQuestion":
        if not isinstance(data, dict):
            raise ValueError("Each question must be a dictionary.")
        required_keys = {"question", "options", "answer", "category"}
        if not required_keys.issubset(data):
            missing = required_keys - set(data)
            raise ValueError(f"Missing keys in question: {missing}")
        return TriviaQuestion(
            question=data["question"],
            options=data["options"],
            answer=data["answer"],
            category=data["category"],
        )
