import copy
from typing import Callable, Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class Iterator(Generic[T]):
    @property
    def count(self) -> int:
        if self._total_count is not None:
            return self._total_count
        else:
            self._retrieve_next_page()
            return self._total_count  # type: ignore

    def __init__(
        self,
        *,
        results_fetcher: Callable[[int], Tuple[List[T], bool, int]],
        limit: int,
        current_page: int = 0,
        total_results_fetched: int = 0,
        results: Optional[List[T]] = None,
        total_count: Optional[int] = None,
        has_next: bool = True
    ):
        self._results_fetcher = results_fetcher
        self._limit = limit

        self._total_results_iterated = 0
        self._current_results_index = 0

        self._current_page = current_page
        self._total_results_fetched = total_results_fetched
        self._results: List[T] = [] if results is None else results
        self._total_count: Optional[int] = total_count
        self._has_next: bool = has_next

    def _retrieve_next_page(self):
        self._current_page += 1
        results, has_next, count = self._results_fetcher(self._current_page)

        self._total_results_fetched += len(results)
        self._current_results_index = 0
        self._results = results
        self._total_count = count
        self._has_next = has_next

    def __len__(self):
        return self.count if self.count < self._limit else self._limit

    def __iter__(self):
        return type(self)(
            results_fetcher=self._results_fetcher,
            limit=self._limit,
            current_page=self._current_page,
            total_results_fetched=self._total_results_fetched,
            results=copy.deepcopy(self._results),
            total_count=self._total_count,
            has_next=self._has_next,
        )

    def __next__(self):
        if self._total_results_iterated >= self._limit:
            raise StopIteration()

        self._total_results_iterated += 1
        if self._total_results_iterated > self._total_results_fetched and self._has_next:
            self._retrieve_next_page()
        elif self._total_results_iterated > self._total_results_fetched:
            raise StopIteration()

        self._current_results_index += 1
        return self._results[self._current_results_index - 1]