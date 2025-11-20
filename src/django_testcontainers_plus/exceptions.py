class DjangoTestcontainersError(Exception): ...


class MissingDependencyError(DjangoTestcontainersError):
    def __init__(
        self,
        provider_name: str,
        extra_name: str,
        detected_in: str | None = None,
        original_error: Exception | None = None,
    ):
        """Initialize the error with helpful context.

        Args:
            provider_name: Name of the provider (e.g., "MySQL", "Redis")
            extra_name: Name of the pip extra to install (e.g., "mysql", "redis")
            detected_in: Where the need was detected (e.g., "DATABASES['default']")
            original_error: The original ImportError that triggered this
        """
        self.provider_name = provider_name
        self.extra_name = extra_name
        self.detected_in = detected_in
        self.original_error = original_error

        message = self._build_message()
        super().__init__(message)

    def _build_message(self) -> str:
        """Build a helpful error message with installation instructions."""
        lines = [
            f"\n{'=' * 70}",
            f"{self.provider_name} Support Not Installed",
            "=" * 70,
        ]

        if self.detected_in:
            lines.extend(
                [
                    f"\n{self.provider_name} was detected in your Django settings:",
                    f"  → {self.detected_in}",
                ]
            )
        else:
            lines.append(f"\n{self.provider_name} is configured but dependencies are missing.")

        lines.extend(
            [
                f"\nTo enable {self.provider_name} support, install the required dependencies:",
                f"  pip install django-testcontainers-plus[{self.extra_name}]",
                "\nOr install all providers:",
                "  pip install django-testcontainers-plus[all]",
            ]
        )

        if self.original_error:
            error_type = type(self.original_error).__name__
            lines.extend(
                [
                    f"\nOriginal error: {error_type}: {self.original_error}",
                ]
            )

        lines.extend(
            [
                "\nFor more information, see:",
                "  https://github.com/woodywoodster/django-testcontainers-plus#installation",
                "=" * 70,
            ]
        )

        return "\n".join(lines)
