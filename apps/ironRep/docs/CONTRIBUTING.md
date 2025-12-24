# Contributing to IronRep

Thank you for your interest in contributing to IronRep! This document provides guidelines and standards for contributions.

## 🎯 Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ironRep.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows project style guide
- [ ] All tests pass (`pnpm test`)
- [ ] TypeScript compiles without errors (`pnpm build`)
- [ ] No linting errors (`pnpm lint`)
- [ ] Documentation updated if needed
- [ ] Commits are well-formatted

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Commented hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass
```

## 💻 Development Guidelines

### Code Style

**TypeScript/React**:
- Use functional components with hooks
- No `any` types without justification
- Prefer named exports
- Use TypeScript strict mode
- Follow [DEVELOPMENT_GUIDE.md](./apps/frontend/DEVELOPMENT_GUIDE.md)

**Python**:
- Follow PEP 8
- Use type hints
- Async/await for I/O operations
- FastAPI best practices

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user profile page
fix: resolve authentication bug
docs: update API documentation
style: format code with prettier
refactor: simplify state management
test: add unit tests for validation
chore: update dependencies
```

### Testing

- Write tests for new features
- Maintain existing test coverage
- Test edge cases
- Use descriptive test names

```typescript
describe('MyComponent', () => {
  it('should render with correct props', () => {
    // test
  });

  it('should handle error states', () => {
    // test
  });
});
```

### Documentation

- Update README for significant changes
- Document complex logic
- Add JSDoc for public APIs
- Update ADRs for architectural decisions

## 🐛 Bug Reports

### Template

```markdown
**Describe the bug**
Clear description

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Arch Linux]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other information
```

## ✨ Feature Requests

### Template

```markdown
**Is your feature request related to a problem?**
Description

**Describe the solution**
How should it work?

**Describe alternatives**
Other approaches considered

**Additional context**
Mockups, examples, etc.
```

## 🔍 Code Review Process

All submissions require review. We aim to:
- Review within 48 hours
- Provide constructive feedback
- Collaborate on improvements

### Review Checklist

- [ ] Code quality and readability
- [ ] Test coverage
- [ ] Documentation
- [ ] Performance considerations
- [ ] Security implications
- [ ] Accessibility compliance

## 🎨 Design Guidelines

- Follow existing UI patterns
- Ensure accessibility (WCAG 2.1 AA)
- Mobile-first responsive design
- Use Tailwind utility classes
- Maintain brand consistency

## 📦 Dependencies

### Adding Dependencies

Frontend:
```bash
pnpm add package-name
pnpm add -D dev-package
```

Backend:
```bash
uv add package-name
uv add --dev dev-package
```

### Dependency Criteria

- Actively maintained
- Good TypeScript support (frontend)
- Small bundle size
- Well-documented
- Compatible with existing stack

## 🔒 Security

- Never commit secrets or API keys
- Use environment variables
- Follow security best practices
- Report vulnerabilities privately

## 📞 Questions?

- Open a GitHub issue
- Check existing documentation
- Review closed issues/PRs

## 🙏 Recognition

Contributors will be recognized in:
- README.md
- Release notes
- Project documentation

---

Thank you for contributing to IronRep! 🎉
