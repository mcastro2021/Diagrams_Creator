# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker support for development and production
- Comprehensive testing suite with Jest
- ESLint and Prettier for code quality
- Security headers with Helmet.js
- Rate limiting for API endpoints
- Database schema for PostgreSQL
- Redis support for caching and sessions
- Comprehensive documentation
- Contributing guidelines
- Security policy
- Issue and PR templates

### Changed
- Updated to Node.js 18+ requirement
- Improved error handling and logging
- Enhanced API endpoints with proper versioning
- Better security configuration

### Fixed
- Fixed CORS configuration for production
- Improved error messages and responses
- Fixed static file serving

## [2.0.0] - 2024-01-XX

### Added
- AI-powered diagram generation using Groq API
- Advanced Azure service recognition
- Intelligent positioning and connection algorithms
- Enhanced user interface with modern design
- Export functionality for diagrams
- Example templates for common architectures
- Health check endpoint
- Comprehensive API documentation
- Support for multiple Azure service types
- Hub and Spoke architecture support
- Microservices architecture support
- Serverless architecture support

### Changed
- Complete rewrite of the backend architecture
- Improved frontend with better UX
- Enhanced diagram rendering engine
- Better error handling and user feedback
- Optimized performance and scalability

### Fixed
- Fixed diagram generation accuracy
- Improved connection logic
- Better handling of complex architectures
- Fixed positioning issues for large diagrams

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Azure Diagram Generator
- Basic diagram generation from natural language
- Support for common Azure services
- Simple web interface
- Basic export functionality
- Local processing engine

### Features
- Virtual Machine support
- App Service support
- SQL Database support
- Storage Account support
- Basic networking components
- Simple connection logic

---

## Version History

- **v2.0.0**: Major rewrite with AI integration and advanced features
- **v1.0.0**: Initial release with basic functionality

## Migration Guide

### From v1.x to v2.x

1. **Environment Variables**: Update your `.env` file with new variables
2. **API Endpoints**: Update API calls to use `/api/` prefix
3. **Database**: Run the new schema migration if using database features
4. **Dependencies**: Run `npm install` to get new dependencies

### Breaking Changes

- API endpoints now use `/api/` prefix
- Some response formats have changed
- Database schema has been updated
- Node.js 18+ is now required

## Support

For questions about upgrading or migration, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with the "question" label
4. Contact the maintainers

## Contributors

Thank you to all contributors who have helped improve this project!

- [Manuel Castro](https://github.com/mcastro2021) - Project maintainer
- [Your name here] - Add your contributions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
