from typing import List

import pytest

from caplena.errors import DuplicatedTopicsError
from caplena.models.projects import Topic, TopicSentiment
from caplena.validations.projects import validate_no_duplicated_topics


@pytest.fixture
def topics(topic_ids: List[str]) -> List[Topic]:
    return [Topic(id=tid, sentiment=TopicSentiment.ANY) for tid in topic_ids]


@pytest.mark.parametrize(
    "topic_ids",
    [
        ["one", "two", "one"],
        ["one", "one"],
    ],
)
def test_validate_no_duplicated_topics_raises(topics: List[Topic]) -> None:
    with pytest.raises(DuplicatedTopicsError):
        validate_no_duplicated_topics(topics)


@pytest.mark.parametrize(
    "topic_ids",
    [
        [],
        ["one"],
        ["one", "two", "three"],
    ],
)
def test_validate_no_duplicated_topics_succeeds(topics: List[Topic]) -> None:
    validate_no_duplicated_topics(topics)
    assert True
