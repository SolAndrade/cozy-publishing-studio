# Persistence and artifacts

Development now includes durable JSON project persistence and hashed private artifact storage.

These modules are intentionally backend-only. Generated art, masters, interiors, covers and unpublished commercial data must not be committed to this public repository.

The local adapters make restarts testable. Cloud deployment will replace them with a managed database/object store without changing the production-domain rules.
