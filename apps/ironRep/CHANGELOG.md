# Changelog

All notable changes to IronRep will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-agent AI system (Workout Coach, Nutritionist, Medical Advisor)
- Personalized workout planning with pain-aware adaptations
- Nutrition coaching and meal planning
- Progress tracking with calendar and analytics
- Pain assessment and monitoring
- Accessibility utilities (ARIA, keyboard navigation, screen readers)
- Comprehensive testing infrastructure
- Error boundaries and centralized error handling
- Form validation utilities
- HTTP client with automatic retry logic
- Session-based authentication token storage

### Changed
- Migrated from localStorage to sessionStorage for auth tokens
- Implemented strict TypeScript types (100% type safety)
- Centralized logging infrastructure (backend + frontend)
- Immutable state updates in Zustand stores
- Performance optimizations (React.memo, useCallback, useMemo)

### Fixed
- Eliminated 20/20 `any` types across codebase
- Fixed direct state mutations
- Improved error handling consistency
- Enhanced security posture

### Security
- Session-based token storage (reduced XSS surface)
- Input validation
- Secure HTTP client with interceptors

## [0.1.0] - 2025-11-25

### Initial Release
- Basic MVP functionality
- AI-powered rehabilitation platform
- User authentication
- Workout and nutrition modules
- Progress tracking
