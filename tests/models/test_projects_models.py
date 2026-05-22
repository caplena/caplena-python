from datetime import datetime
from typing import List, Optional, Union

import pytest

from caplena.errors import DuplicatedTopicsError
from caplena.models.projects import (
    NonTTACell,
    NonTTAColumnDefinition,
    NonTTAColumnType,
    Topic,
    TopicDefinition,
    TopicSentiment,
    TTACell,
)


class TestTTACell:
    @pytest.mark.parametrize(
        "topics",
        [
            [
                Topic(id="one", sentiment=TopicSentiment.ANY),
                Topic(id="two", sentiment=TopicSentiment.ANY),
            ]
        ],
    )
    def test_cell_without_duplicated_topics_succeeds(self, topics: List[Topic]) -> None:
        actual = TTACell(ref="_", value="_", topics=topics)
        assert actual

    @pytest.mark.parametrize(
        "topics",
        [
            [
                Topic(id="one", sentiment=TopicSentiment.ANY),
                Topic(id="one", sentiment=TopicSentiment.ANY),
                Topic(id="two", sentiment=TopicSentiment.ANY),
            ]
        ],
    )
    def test_cell_with_duplicated_topics_raises(self, topics: List[Topic]) -> None:
        with pytest.raises(DuplicatedTopicsError):
            TTACell(ref="_", value="_", topics=topics)


class TestNonTTACell:
    NOW_DT = datetime.now()

    @pytest.fixture
    def cell(self, cell_value: Optional[Union[int, str, bool, datetime]]) -> NonTTACell:
        return NonTTACell(ref="_", value=cell_value)

    @pytest.mark.parametrize(
        "cell_value, expected",
        [
            (1, 1),
            ("1", "1"),
            ("True", "True"),
            (True, True),
            ("2023-06-29 11:11:43.377780", "2023-06-29 11:11:43.377780"),
            (NOW_DT, NOW_DT),
        ],
    )
    def test_values_preserve_their_types(
        self, cell: NonTTACell, expected: Union[int, str, bool, datetime]
    ) -> None:
        actual = cell
        assert actual.value == expected


NOT_PROVIDED = object()


class TestTopicDefinition:
    @pytest.fixture
    def topic_definition(self, sentiment_enabled: bool) -> TopicDefinition:
        return TopicDefinition(label="_", sentiment_enabled=sentiment_enabled, category="_")

    @pytest.mark.parametrize(
        "sentiment, sentiment_enabled, expected",
        [
            (NOT_PROVIDED, False, TopicSentiment.ANY),
            (TopicSentiment.NEUTRAL, False, TopicSentiment.ANY),
            (TopicSentiment.POSITIVE, False, TopicSentiment.ANY),
            (TopicSentiment.NEGATIVE, False, TopicSentiment.ANY),
            (NOT_PROVIDED, True, TopicSentiment.ANY),
            (TopicSentiment.NEUTRAL, True, TopicSentiment.NEUTRAL),
            (TopicSentiment.POSITIVE, True, TopicSentiment.POSITIVE),
            (TopicSentiment.NEGATIVE, True, TopicSentiment.NEGATIVE),
        ],
    )
    def test_build_topic_respects_sentiment_enabled(
        self, topic_definition: TopicDefinition, sentiment: TopicSentiment, expected: TopicSentiment
    ) -> None:
        if sentiment == NOT_PROVIDED:
            actual = topic_definition.build_topic(id="_")
        else:
            actual = topic_definition.build_topic(id="_", sentiment=sentiment)

        assert actual.sentiment == expected.value  # type: ignore[comparison-overlap]


class TestNonTTAColumnDefinition:
    @pytest.mark.parametrize(
        "type, value, expected",
        [
            (NonTTAColumnType.numerical, 1, 1),
            (NonTTAColumnType.numerical, "1", 1),
            (
                NonTTAColumnType.date,
                str(datetime(2023, 6, 29, 11, 11, 11)),
                datetime(2023, 6, 29, 11, 11, 11),
            ),
            (NonTTAColumnType.boolean, True, True),
            (NonTTAColumnType.boolean, "True", True),
            (NonTTAColumnType.text, True, "True"),
            (NonTTAColumnType.text, 1, "1"),
            (NonTTAColumnType.text, "1", "1"),
            (
                NonTTAColumnType.text,
                str(datetime(2023, 6, 29, 11, 11, 11)),
                str(datetime(2023, 6, 29, 11, 11, 11)),
            ),
        ],
    )
    def test_build_cell(
        self, type: NonTTAColumnType, value: str, expected: Union[int, datetime, bool, str]
    ) -> None:
        non_tta_col_def = NonTTAColumnDefinition(ref="_", type=type, name="_")
        actual = non_tta_col_def.build_cell(ref="_", value=value)
        assert actual.value == expected
