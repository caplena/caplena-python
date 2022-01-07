from datetime import datetime

from caplena.api import ApiFilter, ZeroOrMany


class ProjectsFilter(ApiFilter):
    @classmethod
    def name(
        cls,
        *,
        exact__i: ZeroOrMany[str] = None,
        contains__i: ZeroOrMany[str] = None,
    ) -> "ProjectsFilter":
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
        return cls.construct(
            name="tags",
            filters={
                cls.DEFAULT: tag,
            },
        )

    @classmethod
    def upload_status(cls, upload_status: ZeroOrMany[str]) -> "ProjectsFilter":
        return cls.construct(
            name="upload_status",
            filters={
                cls.DEFAULT: upload_status,
            },
        )

    @classmethod
    def language(cls, language: ZeroOrMany[str]) -> "ProjectsFilter":
        return cls.construct(
            name="language",
            filters={
                cls.DEFAULT: language,
            },
        )

    @classmethod
    def translation_status(cls, translation_status: ZeroOrMany[str]) -> "ProjectsFilter":
        return cls.construct(
            name="translation_status",
            filters={
                cls.DEFAULT: translation_status,
            },
        )

    @classmethod
    def translation_engine(cls, translation_engine: ZeroOrMany[str]) -> "ProjectsFilter":
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
        return cls.construct(
            name="created",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
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
        return cls.construct(
            name="last_modified",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
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
    class Columns:
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
            return RowsFilter.construct(
                name="columns",
                filters={
                    f"{ref}[text].exact.i": exact__i,
                    f"{ref}[text].contains.i": contains__i,
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
        return cls.construct(
            name="created",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
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
        return cls.construct(
            name="last_modified",
            filters={
                "gte": gte,
                "gt": gt,
                "lte": lte,
                "lt": lt,
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
