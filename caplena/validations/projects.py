from typing import TYPE_CHECKING, Dict, List

from caplena.errors import DuplicatedTopicsError

# avoid circular dependency when not type-checking
if TYPE_CHECKING:
    from caplena.models.projects import Topic


def validate_no_duplicated_topics(topics: List["Topic"]) -> None:
    """Validates whether there are duplicate topics in a list provided.

    :param topics: A list of topics to check for duplicates.
    :raises caplena.errors.DuplicatedTopicsError: An exception raised if there are duplicate topics.
    """
    id_to_occurences: Dict[str, List[Topic]] = {}
    for topic in topics:
        id_to_occurences.setdefault(topic.id, []).append(topic)
    duplicates = {id: len(topics) for id, topics in id_to_occurences.items() if len(topics) > 1}
    if duplicates:
        raise DuplicatedTopicsError(
            "A cell cannot contain duplicated topics. The topics with following ids have been"
            "provided multiple times. `.duplicates` attribute of this exception contains: "
            f"{duplicates}",
            duplicates,
        )
