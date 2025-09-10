# Contributing to Azure Diagram Generator

Thank you for your interest in contributing to Azure Diagram Generator! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@example.com](mailto:contact@example.com).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/Diagrams_Creator.git
   cd Diagrams_Creator
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/mcastro2021/Diagrams_Creator.git
   ```

## Development Setup

### Prerequisites

- Node.js 18+ 
- npm 8+
- Git
- (Optional) Docker and Docker Compose
- (Optional) PostgreSQL for local development

### Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run the setup script**:
   ```bash
   npm run setup
   ```

3. **Configure environment**:
   - Copy `env.example` to `.env`
   - Add your Groq API key and other configuration

4. **Start development server**:
   ```bash
   npm run dev
   ```

### Docker Setup (Alternative)

```bash
npm run docker:dev
```

## Making Changes

### Branch Strategy

- Create a new branch for each feature or bugfix
- Use descriptive branch names:
  - `feature/add-new-azure-service`
  - `bugfix/fix-diagram-rendering`
  - `docs/update-readme`

### Code Style

We use ESLint and Prettier for code formatting:

```bash
# Check for linting issues
npm run lint

# Fix linting issues automatically
npm run lint:fix

# Format code
npm run format

# Check formatting
npm run format:check
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Examples:
- `feat(api): add new diagram generation endpoint`
- `fix(ui): resolve diagram rendering issue`
- `docs(readme): update installation instructions`
- `test(api): add tests for diagram generation`

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Writing Tests

- Write tests for new features
- Ensure all tests pass before submitting
- Aim for high test coverage
- Use descriptive test names

### Test Structure

```javascript
describe('Feature Name', () => {
  describe('when condition', () => {
    it('should do something', () => {
      // Test implementation
    });
  });
});
```

## Submitting Changes

### Before Submitting

1. **Ensure all tests pass**:
   ```bash
   npm test
   ```

2. **Check code style**:
   ```bash
   npm run lint
   npm run format:check
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### Pull Request Process

1. **Create a pull request** from your branch to `main`
2. **Fill out the PR template** completely
3. **Link related issues** using keywords like "Fixes #123"
4. **Request review** from maintainers
5. **Address feedback** promptly

### PR Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] New features have tests
- [ ] PR description is complete
- [ ] No merge conflicts

## Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check if it's a bug** or feature request
3. **Gather relevant information**

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (if any)
- Acceptance criteria

## Pull Request Guidelines

### PR Title

Use the conventional commit format:
```
type(scope): brief description
```

### PR Description

Include:
- Summary of changes
- Motivation and context
- Testing performed
- Screenshots (if UI changes)
- Breaking changes (if any)

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in staging environment
4. **Approval** from at least one maintainer

## Development Workflow

### Feature Development

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit PR
5. Address review feedback
6. Merge after approval

### Bug Fixes

1. Create bugfix branch
2. Write failing test
3. Implement fix
4. Ensure test passes
5. Submit PR
6. Merge after approval

## Architecture Guidelines

### Backend

- Follow RESTful API design
- Use proper HTTP status codes
- Implement proper error handling
- Add input validation
- Use environment variables for configuration

### Frontend

- Use semantic HTML
- Implement responsive design
- Follow accessibility guidelines
- Use modern JavaScript features
- Optimize for performance

### Database

- Use migrations for schema changes
- Follow naming conventions
- Add proper indexes
- Implement data validation

## Release Process

1. **Version bump** in package.json
2. **Update CHANGELOG.md**
3. **Create release tag**
4. **Deploy to production**
5. **Announce release**

## Getting Help

- **Documentation**: Check the README and docs
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Email**: Contact maintainers directly

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Azure Diagram Generator! 🎉
