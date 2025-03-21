[![CI](https://github.com/ihabsoliman/gomod-discovery/actions/workflows/ci.yml/badge.svg)](https://github.com/ihabsoliman/gomod-discovery/actions/workflows/ci.yml)

# Gomod-discovery - Private Go Module Discovery Service

A Cloudflare Worker-based service that enables using private Go modules from GitHub repositories with custom domain.

## Overview

This project deploys a Cloudflare Worker that handles Go's module discovery protocol, allowing developers to use private GitHub repositories as Go modules with a custom import path. Since Cloudflare Python Workers currently don't support external packages, this project implements a custom router to handle the necessary endpoints.

## Features

### Currently Implemented
- Custom Router: A lightweight URL routing system for Python Cloudflare Workers
- Basic endpoint handlers for Go module discovery

### Planned Features (Not Yet Implemented)
- **Go Module Discovery**: Handling the `go-get=1` protocol to redirect Go package imports to GitHub repositories
- **Custom Domain Support**: Support for custom domain for Go modules
- **GitHub Integration**: Seamless linking between module imports and GitHub repositories
- **Authentication**: Secure access to private modules

## Technical Details

### Architecture

The project is built around a Python-based Cloudflare Worker with these main components:

- **Router**: A custom routing system that matches URL patterns and routes requests to the appropriate handlers
- **Entry Point**: Manages incoming requests and delegates to the correct handlers
- **Logging**: Provides detailed logging for debugging and monitoring

### How it Works

1. When Go tries to download a module at `<domain>/{pkg}`, it sends a request with `?go-get=1`
2. Our worker responds with HTML containing `<meta>` tags that direct Go to:
   - Use Git protocol
   - Point to the corresponding GitHub repository
   - Provide source code navigation links
3. Go then clones the repository directly from GitHub

## Deployment

### Prerequisites

- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
- Cloudflare account
- Node.js and npm

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ihabsoliman/gomod-discovery.git
   cd gomod-discovery
   ```

2. Install dependencies:
   ```bash
   make sync
   ```

3. Configure your Cloudflare credentials:
   ```bash
   wrangler login
   ```


## Using with Go

Add this to your Go environment configuration:
```bash
go env -w GOPRIVATE=<custom_domain>
```

For authenticated access:
```bash
git config --global url."https://username:token@github.com".insteadOf "https://github.com"
```

Example of importing a private module:
```go
import "<custom_domain>/myproject"
```

## Development

### Project Structure

- `src/entry.py`: Main entry point for the Cloudflare Worker
- `src/router.py`: Custom URL router implementation
- `src/log.py`: Logging utilities
- `tests/`: Unit tests
- `wrangler.jsonc`: Cloudflare Workers configuration

### Local Development

1. Make changes to the source files
2. Run tests: `make test`
3. Test locally: `make dev`
4. Lint code: `make lint`

## Roadmap

1. Implement Go module discovery handler
2. Add support for authentication
3. Add domain validation
4. Implement caching for better performance
5. Add monitoring and analytics
6. Deploy to Cloudflare

## License

See the [LICENSE](LICENSE) file for details.