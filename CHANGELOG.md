# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-rule JWT configuration via `JWT_AUTHENTICATION_RULES` dict
- Singleton `JWTAuthenticationRules` for centralized rule management
- `TokenFactory` for generating and validating access and refresh tokens
- `@authenticate` decorator for protecting Flask routes
- `BlackListed` class for token revocation
- `Database` singleton for bridging Flask-SQLAlchemy
- `import_handler` utility for dynamic dotted-path imports
- `PyJWT` proxy wrapper for encode/decode operations
- Pydantic-backed `JWTRuleDetails` validator for rule configuration
- `initialize_jwt_authentication()` bootstrap entry point
- MIT License

### Fixed
- `parse_token()` was a stub — now correctly extracts token from `Authorization` header
- `get_rule(None)` was returning the rule name string instead of the rule dict
- `@authenticate` decorator had misplaced `return wrapper` causing it to never execute the view
- `table` / `table_path` field aliases were misspelled as `"tabel"` / `"tabel_path"` in the Pydantic validator
- `is_blacklisted()` was ignoring `rule_name`, always reading the default rule's blacklist setting
- Added `_reset()` class methods to `Database` and `JWTAuthenticationRules` singletons for test isolation

## [0.1.0] - TBD

_Initial public release._
