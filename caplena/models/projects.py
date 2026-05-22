from datetime import datetime
from enum import Enum
from typing import Any, Callable, ClassVar, Dict, List, Optional, Sequence, Union, cast

import pydantic

from caplena.validations.projects import validate_no_duplicated_topics


class NonTTAColumnType(Enum):
    numerical = "numerical"
    date = "date"
    boolean = "boolean"
    text = "text"


class TTAColumnType(Enum):
    text_to_analyze = "text_to_analyze"


class NonTTAColumnDefinition(pydantic.BaseModel):
    """Column definition for NonTextToAnalyze column."""

    ref: str
    type: NonTTAColumnType
    name: str
    convertor: ClassVar[Dict[str, Callable[[str], Union[int, datetime, bool, str]]]] = {
        NonTTAColumnType.numerical.value: int,
        NonTTAColumnType.date.value: datetime.fromisoformat,
        NonTTAColumnType.boolean.value: bool,
        NonTTAColumnType.text.value: str,
    }

    # we want the enum value when serialising to .dict()
    model_config = pydantic.ConfigDict(use_enum_values=True)

    def convert_to_type(self, val: str) -> Union[int, datetime, bool, str]:
        # we use the enum's values here since the class is configured to always use enum's values
        type_val = cast(str, self.type)  # Config.use_enum_values converts type to .value (str)
        return self.convertor[type_val](val)

    def build_cell(self, ref: str, value: str) -> "NonTTACell":
        return NonTTACell(ref=ref, value=self.convert_to_type(value))


class Sentiment(pydantic.BaseModel):
    code: Optional[int] = None
    label: Optional[str] = None


class TopicSentiment(Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ANY = "any"


class TopicDefinition(pydantic.BaseModel):
    label: str
    sentiment_enabled: bool
    category: str
    color: Optional[str] = None
    description: Optional[str] = None
    sentiment_neutral: Optional[Sentiment] = None
    sentiment_negative: Optional[Sentiment] = None
    sentiment_positive: Optional[Sentiment] = None

    def build_topic(self, id: str, sentiment: TopicSentiment = TopicSentiment.ANY) -> "Topic":
        _sentiment = sentiment if self.sentiment_enabled else TopicSentiment.ANY
        return Topic(id=id, sentiment=_sentiment)


class TTAColumnDefinition(pydantic.BaseModel):
    """Column definition for TextToAnalyze column."""

    ref: str
    name: str
    topics: List[TopicDefinition]
    type: TTAColumnType = TTAColumnType.text_to_analyze
    description: Optional[str] = None
    model_config = pydantic.ConfigDict(use_enum_values=True)

    def convert_to_type(self, val: Any) -> str:
        return str(val)

    def build_cell(
        self, ref: str, topics: List["Topic"], value: str, was_reviewed: bool
    ) -> "TTACell":
        return TTACell(
            ref=ref, topics=topics, value=self.convert_to_type(value), was_reviewed=was_reviewed
        )


ColumnDefinition = Union[TTAColumnDefinition, NonTTAColumnDefinition]


class Topic(pydantic.BaseModel):
    id: str
    sentiment: TopicSentiment
    model_config = pydantic.ConfigDict(use_enum_values=True)


class TTACell(pydantic.BaseModel):
    """Cell definition for TextToAnalyze cell."""

    ref: str
    topics: List[Topic]
    value: str
    was_reviewed: bool = False

    @pydantic.validator("topics")
    def topics_shouldnt_have_duplicates(cls, topics: List[Topic]) -> List[Topic]:
        validate_no_duplicated_topics(topics)
        return topics


class NonTTACell(pydantic.BaseModel):
    """Cell definition for NonTextToAnalyze cell."""

    ref: str
    value: Optional[Union[int, str, bool, datetime]] = None


Cell = Union[TTACell, NonTTACell]


class MultipleCellPayload(pydantic.BaseModel):
    cells: List[Cell]


class RowPayload(pydantic.BaseModel):
    columns: List[Cell]


class MultipleRowPayload(pydantic.BaseModel):
    rows: List[RowPayload]


class ProjectLanguage(Enum):
    AF = "af"
    SQ = "sq"
    EU = "eu"
    CA = "ca"
    CS = "cs"
    DA = "da"
    NL = "nl"
    EN = "en"
    ET = "et"
    FI = "fi"
    FR = "fr"
    GL = "gl"
    DE = "de"
    EL = "el"
    HU = "hu"
    IS = "is"
    IT = "it"
    LB = "lb"
    LT = "lt"
    LV = "lv"
    MK = "mk"
    NO = "no"
    PL = "pl"
    PT = "pt"
    RO = "ro"
    SR = "sr"
    SK = "sk"
    SL = "sl"
    ES = "es"
    SV = "sv"
    TR = "tr"


class ProjectSettings(pydantic.BaseModel):
    """Projects settings for project creation."""

    name: str
    language: ProjectLanguage
    columns: Sequence[ColumnDefinition]
    tags: List[str] = pydantic.Field(default_factory=list)
    translation_engine: Optional[str] = None
    anonymize_pii: Optional[Any] = pydantic.Field(default=None)
    model_config = pydantic.ConfigDict(use_enum_values=True)
