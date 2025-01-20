import time
from langchain_community.callbacks import get_openai_callback


def timer(verbose=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if verbose:
                start_time = time.time()
            result = func(*args, **kwargs)
            if verbose:
                end_time = time.time()
                print("======== Timer =========")
                print(f"Complete {func.__name__}, {end_time - start_time:.2f} sec")
                print("========================")
            return result

        return wrapper

    return decorator


def count_tokens(verbose=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with get_openai_callback() as cb:
                res = func(*args, **kwargs)
                if verbose:
                    print("=== OpenAI API Usage ===")
                    print(f"Tokens used: {cb.total_tokens}")
                    print(f"Total cost: ${cb.total_cost:.2f}")
                    print("========================")
                return res

        return wrapper

    return decorator
