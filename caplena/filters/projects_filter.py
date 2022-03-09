from datetime import datetime

from typing_extensions import Literal

from caplena.api import ApiFilter, ZeroOrMany

DateRange = Literal[
    "all_time", "this_month", "last_month", "this_quarter", "last_quarter", "this_year", "last_year"
]


class ProjectsFilter(ApiFilter):
    """The filter that can be used to filter projects.

    :param constraints: The internal filter constraints. Should never be manually given.
    :param has_conjunction: The internal conjunction boolean. Should never be manually given.
    """

    @classmethod
    def name(
        cls,
        *,
        exact__i: ZeroOrMany[str] = None,
        contains__i: ZeroOrMany[str] = None,
    ) -> "ProjectsFilter":
        """Allows filtering results based on text fields. For example, filtering with
        :code:`ProjectsFilter.name(contains__i='reviews')` only returns results containing the
        text reviews for the specified field.

        :param exact__i: Allows filtering on exact, case-insensitive text.
        :param contains__i: Allows filtering on partial, case-insensitive text.
        """
        return cls.construct(
            name="name",
            filters={
                "exact.i": exact__i,
                "contains.i": contains__i,
            },
        )

    @classmethod
    def owner(
        cls,
        *,
        id: ZeroOrMany[str],
        email__exact__i: ZeroOrMany[str],
        email__contains__i: ZeroOrMany[str],
    ) -> "ProjectsFilter":
        """Allows filtering projects based on their owner. For example, filtering with
        :code:`ProjectsFilter.owner(email__exact__i='katy@acme.com')` only returns
        projects that belong to :code:`katy@acme.com`.

        :param id: Allows filtering on project owner identifiers.
        :param email__exact__i: Allows filtering on exact, case-insensitive email addresses of project owners.
        :param email__contains__i: Allows filtering on partial, case-insensitive email addresses of project owners.
        """
        return cls.construct(
            name="owner",
            filters={
                "id": id,
                "email.exact.i": email__exact__i,
                "email.contains.i": email__contains__i,
            },
        )

    @classmethod
    def tags(cls, tag: ZeroOrMany[str]) -> "ProjectsFilter":
        """Allows filtering projects based on the tags they contain. For example, filtering with
        :code:`ProjectsFilter.tags('tag1') & ProjectsFilter.tags('tag2')` returns all projects
        that are tagged with both :code:`tag1` and :code:`tag2`.

        :param tag: Allows filtering on project tags.
        """
        return cls.construct(
            name="tags",
            filters={
                cls.DEFAULT: tag,
            },
        )

    @classmethod
    def upload_status(cls, upload_status: ZeroOrMany[str]) -> "ProjectsFilter":
        """Allows filtering projects based on their upload status. For example, filtering
        with :code:`ProjectsFilter.upload_status(['pending', 'failed'])` returns all
        projects that are pending or have failed.

        :param upload_status: Allows filtering on upload status.
        """
        return cls.construct(
            name="upload_status",
            filters={
                cls.DEFAULT: upload_status,
            },
        )

    @classmethod
    def language(cls, language: ZeroOrMany[str]) -> "ProjectsFilter":
        """Allows filtering projects based on their language. For example, filtering with
        :code:`ProjectsFilter.language(['en', 'es'])` returns all English and Spanish projects.

        :param language: Allows filtering on project language.
        """
        return cls.construct(
            name="language",
            filters={
                cls.DEFAULT: language,
            },
        )

    @classmethod
    def translation_status(cls, translation_status: ZeroOrMany[str]) -> "ProjectsFilter":
        """Allows filtering projects based on their translation status. For example, filtering
        with :code:`ProjectsFilter.translation_status(['disabled', 'pending'])` returns all
        projects that have translation disabled or translation is still pending.

        :param translation_status: Allows filtering on translation status.
        """
        return cls.construct(
            name="translation_status",
            filters={
                cls.DEFAULT: translation_status,
            },
        )

    @classmethod
    def translation_engine(cls, translation_engine: ZeroOrMany[str]) -> "ProjectsFilter":
        """Allows filtering projects based on their translation engine. For example, filtering
        with :code:`ProjectsFilter.translation_engine('google_translate')` returns all projects
        that have Google Translate enabled.

        :param translation_engine: Allows filtering on translation engine.
        """
        return cls.construct(
            name="translation_engine",
            filters={
                cls.DEFAULT: translation_engine,
            },
        )

    @classmethod
    def created(
        cls,
        *,
        gte: ZeroOrMany[datetime] = None,
        gt: ZeroOrMany[datetime] = None,
        lte: ZeroOrMany[datetime] = None,
        lt: ZeroOrMany[datetime] = None,
        range: ZeroOrMany[DateRange] = None,
        year: ZeroOrMany[int] = None,
        year__gte: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lte: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        month__gte: ZeroOrMany[int] = None,
        month__gt: ZeroOrMany[int] = None,
        month__lte: ZeroOrMany[int] = None,
        month__lt: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
        day__gte: ZeroOrMany[int] = None,
        day__gt: ZeroOrMany[int] = None,
        day__lte: ZeroOrMany[int] = None,
        day__lt: ZeroOrMany[int] = None,
    ) -> "ProjectsFilter":
        """Allows filtering results based on date fields. For example, filtering with
        :code:`ProjectsFilter.created(year=2022, month=1)` returns all results for
        January 2022 for the specified field.

        :param gte: Greater than or equal to filter for date times.
        :param gt: Greater than filter for date times.
        :param lte: Less than or equal to filter for date times.
        :param lt: Less than filter for date times.
        :param range: Range filter for date times.
        :param year: Allows filtering on the year.
        :param year__gte: Greater than or equal to filter on the year.
        :param year__gt: Greater than filter on the year.
        :param year__lte: Less than or equal to filter on the year.
        :param year__lt: Less than filter on the year.
        :param month: Allows filtering on the month of the year.
        :param month__gte: Greater than or equal to filter on the month of the year.
        :param month__gt: Greater than filter on the month of the year.
        :param month__lte: Less than or equal to filter on the month of the year.
        :param month__lt: Greater than filter on the month of the year.
        :param day: Allows filtering on the day of the month.
        :param day__gte: Greater than or equal to filter on the day of the month.
        :param day__gt: Greater than filter on the day of the month.
        :param day__lte: Less than or equal to filter on the day of the month.
        :param day__lt: Greater than filter on the day of the month.
        """
        return cls.construct(
            name="created",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
                "range": range,
                "year": year,
                "year.gte": year__gte,
                "year.gt": year__gt,
                "year.lte": year__lte,
                "year.lt": year__lt,
                "month": month,
                "month.gte": month__gte,
                "month.gt": month__gt,
                "month.lte": month__lte,
                "month.lt": month__lt,
                "day": day,
                "day.gte": day__gte,
                "day.gt": day__gt,
                "day.lte": day__lte,
                "day.lt": day__lt,
            },
        )

    @classmethod
    def last_modified(
        cls,
        *,
        gte: ZeroOrMany[datetime] = None,
        gt: ZeroOrMany[datetime] = None,
        lte: ZeroOrMany[datetime] = None,
        lt: ZeroOrMany[datetime] = None,
        range: ZeroOrMany[DateRange] = None,
        year: ZeroOrMany[int] = None,
        year__gte: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lte: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        month__gte: ZeroOrMany[int] = None,
        month__gt: ZeroOrMany[int] = None,
        month__lte: ZeroOrMany[int] = None,
        month__lt: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
        day__gte: ZeroOrMany[int] = None,
        day__gt: ZeroOrMany[int] = None,
        day__lte: ZeroOrMany[int] = None,
        day__lt: ZeroOrMany[int] = None,
    ) -> "ProjectsFilter":
        """Allows filtering results based on date fields. For example, filtering with
        :code:`ProjectsFilter.last_modified(year=2022, month=1)` returns all results for
        January 2022 for the specified field.

        :param gte: Greater than or equal to filter for date times.
        :param gt: Greater than filter for date times.
        :param lte: Less than or equal to filter for date times.
        :param lt: Less than filter for date times.
        :param range: Range filter for date times.
        :param year: Allows filtering on the year.
        :param year__gte: Greater than or equal to filter on the year.
        :param year__gt: Greater than filter on the year.
        :param year__lte: Less than or equal to filter on the year.
        :param year__lt: Less than filter on the year.
        :param month: Allows filtering on the month of the year.
        :param month__gte: Greater than or equal to filter on the month of the year.
        :param month__gt: Greater than filter on the month of the year.
        :param month__lte: Less than or equal to filter on the month of the year.
        :param month__lt: Greater than filter on the month of the year.
        :param day: Allows filtering on the day of the month.
        :param day__gte: Greater than or equal to filter on the day of the month.
        :param day__gt: Greater than filter on the day of the month.
        :param day__lte: Less than or equal to filter on the day of the month.
        :param day__lt: Greater than filter on the day of the month.
        """
        return cls.construct(
            name="last_modified",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
                "range": range,
                "year": year,
                "year.gte": year__gte,
                "year.gt": year__gt,
                "year.lte": year__lte,
                "year.lt": year__lt,
                "month": month,
                "month.gte": month__gte,
                "month.gt": month__gt,
                "month.lte": month__lte,
                "month.lt": month__lt,
                "day": day,
                "day.gte": day__gte,
                "day.gt": day__gt,
                "day.lte": day__lte,
                "day.lt": day__lt,
            },
        )


class RowsFilter(ApiFilter):
    """The filter that can be used to filter rows.

    :param constraints: The internal filter constraints. Should never be manually given.
    :param has_conjunction: The internal conjunction boolean. Should never be manually given.
    """

    class Columns:
        """Allows filtering rows based on the values of its columns."""

        @staticmethod
        def numerical(
            *,
            ref: str,
            exact: ZeroOrMany[float] = None,
            gte: ZeroOrMany[float] = None,
            gt: ZeroOrMany[float] = None,
            lte: ZeroOrMany[float] = None,
            lt: ZeroOrMany[float] = None,
        ) -> "RowsFilter":
            """Allows filtering on numerical columns.

            :param ref: The numerical column reference.
            :param exact: Exact filter for numerical values.
            :param gte: Greater than or equal to filter for numerical values.
            :param gt: Greater than filter for numerical values.
            :param lte: Less than or equal to filter for numerical values.
            :param lt: Less than filter for numerical values.
            """
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[numerical]": exact,
                    f"{ref}[numerical].gte": gte,
                    f"{ref}[numerical].gt": gt,
                    f"{ref}[numerical].lte": lte,
                    f"{ref}[numerical].lt": lt,
                },
            )

        @classmethod
        def boolean(
            cls,
            *,
            ref: str,
            exact: ZeroOrMany[bool] = None,
        ) -> "RowsFilter":
            """Allows filtering on boolean columns.

            :param ref: The boolean column reference.
            :param exact: Exact filter for boolean values.
            """
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[boolean]": exact,
                },
            )

        @classmethod
        def text(
            cls,
            *,
            ref: str,
            exact__i: ZeroOrMany[str] = None,
            contains__i: ZeroOrMany[str] = None,
        ) -> "RowsFilter":
            """Allows filtering on text columns.

            :param ref: The text column reference.
            :param exact__i: Allows filtering on exact, case-insensitive text values.
            :param contains__i: Allows filtering on partial, case-insensitive text values.
            """
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[text].exact.i": exact__i,
                    f"{ref}[text].contains.i": contains__i,
                },
            )

        @classmethod
        def date(
            cls,
            *,
            ref: str,
            gte: ZeroOrMany[datetime] = None,
            gt: ZeroOrMany[datetime] = None,
            lte: ZeroOrMany[datetime] = None,
            lt: ZeroOrMany[datetime] = None,
            range: ZeroOrMany[DateRange] = None,
        ) -> "RowsFilter":
            """Allows filtering on date columns.

            :param gte: Greater than or equal to filter for date times.
            :param gt: Greater than filter for date times.
            :param lte: Less than or equal to filter for date times.
            :param lt: Less than filter for date times.
            :param range: Range filter for date times.
            """
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[date].gte": gte,
                    f"{ref}[date].gt": gt,
                    f"{ref}[date].lte": lte,
                    f"{ref}[date].lt": lt,
                    f"{ref}[date].range": range,
                },
            )

        @classmethod
        def text_to_analyze(
            cls,
            *,
            ref: str,
            exact__i: ZeroOrMany[str] = None,
            contains__i: ZeroOrMany[str] = None,
            was_reviewed: ZeroOrMany[bool] = None,
            source_language: ZeroOrMany[str] = None,
            translated_value__exact__i: ZeroOrMany[str] = None,
            translated_value__contains__i: ZeroOrMany[str] = None,
        ) -> "RowsFilter":
            """Allows filtering on verbatim columns.

            :param ref: The verbatim column reference.
            :param exact__i: Allows filtering on exact, case-insensitive verbatims.
            :param contains__i: Allows filtering on partial, case-insensitive verbatims.
            :param was_reviewed: Allows filtering on reviewed columns.
            :param source_language: Allows filtering on the source language of this column.
            :param translated_value__exact__i: Allows filtering on exact, case-insensitive translated text verbatims.
            :param translated_value__contains__i: Allows filtering on partial, case-insensitive translated text verbatims.
            """
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[text_to_analyze].exact.i": exact__i,
                    f"{ref}[text_to_analyze].contains.i": contains__i,
                    f"{ref}[text_to_analyze].was_reviewed": was_reviewed,
                    f"{ref}[text_to_analyze].source_language": source_language,
                    f"{ref}[text_to_analyze].translated_value.exact.i": translated_value__exact__i,
                    f"{ref}[text_to_analyze].translated_value.contains.i": translated_value__contains__i,
                },
            )

    @classmethod
    def created(
        cls,
        *,
        gte: ZeroOrMany[datetime] = None,
        gt: ZeroOrMany[datetime] = None,
        lte: ZeroOrMany[datetime] = None,
        lt: ZeroOrMany[datetime] = None,
        range: ZeroOrMany[DateRange] = None,
        year: ZeroOrMany[int] = None,
        year__gte: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lte: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        month__gte: ZeroOrMany[int] = None,
        month__gt: ZeroOrMany[int] = None,
        month__lte: ZeroOrMany[int] = None,
        month__lt: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
        day__gte: ZeroOrMany[int] = None,
        day__gt: ZeroOrMany[int] = None,
        day__lte: ZeroOrMany[int] = None,
        day__lt: ZeroOrMany[int] = None,
    ) -> "RowsFilter":
        """Allows filtering results based on date fields. For example, filtering with
        :code:`RowsFilter.created(year=2022, month=1)` returns all results for
        January 2022 for the specified field.

        :param gte: Greater than or equal to filter for date times.
        :param gt: Greater than filter for date times.
        :param lte: Less than or equal to filter for date times.
        :param lt: Less than filter for date times.
        :param range: Range filter for date times.
        :param year: Allows filtering on the year.
        :param year__gte: Greater than or equal to filter on the year.
        :param year__gt: Greater than filter on the year.
        :param year__lte: Less than or equal to filter on the year.
        :param year__lt: Less than filter on the year.
        :param month: Allows filtering on the month of the year.
        :param month__gte: Greater than or equal to filter on the month of the year.
        :param month__gt: Greater than filter on the month of the year.
        :param month__lte: Less than or equal to filter on the month of the year.
        :param month__lt: Greater than filter on the month of the year.
        :param day: Allows filtering on the day of the month.
        :param day__gte: Greater than or equal to filter on the day of the month.
        :param day__gt: Greater than filter on the day of the month.
        :param day__lte: Less than or equal to filter on the day of the month.
        :param day__lt: Greater than filter on the day of the month.
        """
        return cls.construct(
            name="created",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
                "range": range,
                "year": year,
                "year.gte": year__gte,
                "year.gt": year__gt,
                "year.lte": year__lte,
                "year.lt": year__lt,
                "month": month,
                "month.gte": month__gte,
                "month.gt": month__gt,
                "month.lte": month__lte,
                "month.lt": month__lt,
                "day": day,
                "day.gte": day__gte,
                "day.gt": day__gt,
                "day.lte": day__lte,
                "day.lt": day__lt,
            },
        )

    @classmethod
    def last_modified(
        cls,
        *,
        gte: ZeroOrMany[datetime] = None,
        gt: ZeroOrMany[datetime] = None,
        lte: ZeroOrMany[datetime] = None,
        lt: ZeroOrMany[datetime] = None,
        range: ZeroOrMany[DateRange] = None,
        year: ZeroOrMany[int] = None,
        year__gte: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lte: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        month__gte: ZeroOrMany[int] = None,
        month__gt: ZeroOrMany[int] = None,
        month__lte: ZeroOrMany[int] = None,
        month__lt: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
        day__gte: ZeroOrMany[int] = None,
        day__gt: ZeroOrMany[int] = None,
        day__lte: ZeroOrMany[int] = None,
        day__lt: ZeroOrMany[int] = None,
    ) -> "RowsFilter":
        """Allows filtering results based on date fields. For example, filtering with
        :code:`RowsFilter.last_modified(year=2022, month=1)` returns all results for
        January 2022 for the specified field.

        :param gte: Greater than or equal to filter for date times.
        :param gt: Greater than filter for date times.
        :param lte: Less than or equal to filter for date times.
        :param lt: Less than filter for date times.
        :param range: Range filter for date times.
        :param year: Allows filtering on the year.
        :param year__gte: Greater than or equal to filter on the year.
        :param year__gt: Greater than filter on the year.
        :param year__lte: Less than or equal to filter on the year.
        :param year__lt: Less than filter on the year.
        :param month: Allows filtering on the month of the year.
        :param month__gte: Greater than or equal to filter on the month of the year.
        :param month__gt: Greater than filter on the month of the year.
        :param month__lte: Less than or equal to filter on the month of the year.
        :param month__lt: Greater than filter on the month of the year.
        :param day: Allows filtering on the day of the month.
        :param day__gte: Greater than or equal to filter on the day of the month.
        :param day__gt: Greater than filter on the day of the month.
        :param day__lte: Less than or equal to filter on the day of the month.
        :param day__lt: Greater than filter on the day of the month.
        """
        return cls.construct(
            name="last_modified",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
                "range": range,
                "year": year,
                "year.gte": year__gte,
                "year.gt": year__gt,
                "year.lte": year__lte,
                "year.lt": year__lt,
                "month": month,
                "month.gte": month__gte,
                "month.gt": month__gt,
                "month.lte": month__lte,
                "month.lt": month__lt,
                "day": day,
                "day.gte": day__gte,
                "day.gt": day__gt,
                "day.lte": day__lte,
                "day.lt": day__lt,
            },
        )
