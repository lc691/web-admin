from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityPolicy:
    public_paths: frozenset[str]
    public_prefixes: frozenset[str]

    def is_public(self, path: str) -> bool:
        path = (path or "").rstrip("/") or "/"

        # exact match
        if path in self.public_paths:
            return True

        # prefix match
        for prefix in self.public_prefixes:
            if path == prefix or path.startswith(prefix):
                return True

        return False