import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ProtectedPlaceholder:
    placeholder: str
    text: str


@dataclass(frozen=True)
class ProtectedMaskResult:
    text: str
    placeholders: tuple[ProtectedPlaceholder, ...]


class ProtectedTextMasker:
    PLACEHOLDER_TEMPLATE: str = "<PLACEHOLDER_{INDEX}>"
    PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(r"<PLACEHOLDER_\d+>")
    PLACEHOLDER_CONTAMINATION_PATTERN: re.Pattern[str] = re.compile(
        r"<PLACEHOLDER(?:_\d*)?>?|PLACEHOLDER_\d+>?"
    )

    @classmethod
    def mask(cls, text: str, rule: re.Pattern[str] | None) -> ProtectedMaskResult:
        if rule is None:
            return ProtectedMaskResult(text=text, placeholders=())

        placeholders: list[ProtectedPlaceholder] = []

        def replace(match: re.Match[str]) -> str:
            protected_text = match.group(0)
            if protected_text == "":
                return protected_text

            placeholder = cls.PLACEHOLDER_TEMPLATE.replace(
                "{INDEX}", str(len(placeholders))
            )
            placeholders.append(
                ProtectedPlaceholder(placeholder=placeholder, text=protected_text)
            )
            return placeholder

        return ProtectedMaskResult(
            text=rule.sub(replace, text),
            placeholders=tuple(placeholders),
        )

    @classmethod
    def validate(
        cls, text: str, placeholders: tuple[ProtectedPlaceholder, ...]
    ) -> bool:
        expected = [placeholder.placeholder for placeholder in placeholders]
        actual = cls.PLACEHOLDER_PATTERN.findall(text)
        if actual != expected:
            return False

        remainder = cls.PLACEHOLDER_PATTERN.sub("", text)
        return cls.PLACEHOLDER_CONTAMINATION_PATTERN.search(remainder) is None

    @classmethod
    def unmask(cls, text: str, placeholders: tuple[ProtectedPlaceholder, ...]) -> str:
        text_by_placeholder = {v.placeholder: v.text for v in placeholders}
        return cls.PLACEHOLDER_PATTERN.sub(
            lambda match: text_by_placeholder.get(match.group(0), match.group(0)),
            text,
        )

    @classmethod
    def strip_placeholders(cls, text: str) -> str:
        return cls.PLACEHOLDER_PATTERN.sub("", text)
