from services.observability.langsmith import configure_langsmith
from services.observability.evaluation import run_v1_evaluation
from v1_support import build_demo_brain


def main():
    configuration = configure_langsmith()
    print("LangSmith enabled:", configuration.enabled)
    print("LangSmith project:", configuration.project)

    brain = build_demo_brain()
    result = run_v1_evaluation(brain)

    print("Evaluation submitted:")
    print(result)


if __name__ == "__main__":
    main()
