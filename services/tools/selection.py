from dataclasses import dataclass 

@dataclass
class ToolSelectionPolicy:
    max_tools: int = 3 
    min_score: float | None = None 

    def select(self, results):
        selected = []

        for result in results:

            if self.min_score is not None:

                if result.score is None:
                    continue

                if result.score < self.min_score:
                    continue

            selected.append(result)

            if len(selected) >= self.max_tools:
                break

        return selected