# Diagrams Creator - AI-Powered Architecture Diagram Generator

## 🚀 Overview

Diagrams Creator is a comprehensive AI-powered application that generates architecture diagrams from natural language descriptions. It supports multiple cloud providers (Azure, AWS, GCP), on-premise architectures, and hybrid cloud solutions.

## ✨ Features

### 🎯 Core Capabilities
- **Natural Language Processing**: Generate diagrams from plain English descriptions
- **Multi-Cloud Support**: Azure, AWS, Google Cloud Platform
- **On-Premise Architectures**: Traditional data centers, Kubernetes, Docker
- **Hybrid Cloud**: Cloud bursting, multi-cloud, hybrid connectivity
- **Comprehensive Icon Library**: 1000+ icons from major cloud providers
- **Real-time Generation**: Instant diagram creation and visualization
- **Export Options**: Multiple formats (PNG, SVG, PDF, XML)

### 🏗️ Architecture Patterns Supported
- **Microservices**: Container-based and serverless microservices
- **Serverless**: Function-as-a-Service architectures
- **Data Platforms**: Data lakes, warehouses, analytics pipelines
- **AI/ML Platforms**: Machine learning and artificial intelligence workflows
- **IoT Platforms**: Internet of Things architectures
- **Security Architectures**: Zero-trust, defense-in-depth
- **Disaster Recovery**: Backup, replication, and failover systems
- **Network Architectures**: Hub-and-spoke, mesh, hybrid connectivity

### 🎨 Icon Libraries
- **Azure Icons**: Complete Azure service catalog (693+ icons)
- **AWS Icons**: Full AWS service library (500+ icons)
- **General Icons**: Common infrastructure and application icons
- **Connection Icons**: Arrows, lines, and flow indicators
- **Technology Icons**: Programming languages, frameworks, tools

## 🛠️ Installation

### 🚀 Deploy to Render (Recommended)

1. **Fork this repository** to your GitHub account

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Create account or sign in
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - **Name**: `diagrams-creator` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Starter` (free tier)

4. **Set environment variables:**
   - In Render's "Environment Variables" section, add:
   ```
   OPENAI_API_KEY = your_openai_api_key
   FLASK_ENV = production
   SECRET_KEY = your_secure_secret_key
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - You'll get a public URL (e.g., `https://diagrams-creator.onrender.com`)

### 🏠 Local Installation

#### Prerequisites
- Python 3.8+
- pip package manager
- Git

#### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Diagrams_Creator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Configuration
1. Copy `config_example.py` to `config_local.py`
2. Add your API keys:
   ```python
   # OpenAI Configuration
   OPENAI_API_KEY = "your_openai_api_key_here"
   
   # Alternative AI Providers (optional)
   GROQ_API_KEY = "your_groq_api_key_here"
   HUGGINGFACE_API_KEY = "your_huggingface_api_key_here"
   ```

## 🚀 Usage

### Web Interface
1. Open your browser to `http://localhost:5000`
2. Enter your architecture description in natural language
3. Click "Generate Diagram"
4. View, edit, and export your diagram

### API Usage
```bash
# Generate a diagram
curl -X POST http://localhost:5000/api/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Create an Azure microservices architecture with API Gateway, App Service, and Cosmos DB"}'

# Get diagram details
curl http://localhost:5000/api/diagram/{diagram_id}

# Export diagram
curl http://localhost:5000/api/export/{diagram_id}/png
```

### Example Requests

#### Azure Microservices
```
"Create a microservices architecture using Azure services including API Management, App Service for web APIs, Azure Functions for serverless processing, Cosmos DB for data storage, Service Bus for messaging, Key Vault for secrets management, and Application Insights for monitoring"
```

#### AWS Serverless
```
"Create an AWS serverless architecture with API Gateway, Lambda functions, DynamoDB, S3 storage, SQS messaging, and CloudWatch monitoring"
```

#### Hybrid Cloud
```
"Design a hybrid cloud architecture connecting on-premise data center with Azure using ExpressRoute, including VNet peering, VPN Gateway, and hybrid identity with Azure AD Connect"
```

#### Kubernetes Cluster
```
"Create a Kubernetes cluster architecture with master nodes, worker nodes, ingress controller, service mesh, and monitoring stack with Prometheus and Grafana"
```

## 🏗️ Architecture

### Components
- **Flask Web Application**: Main web interface and API
- **AI Processor**: Natural language processing and diagram generation
- **Diagram Generator**: Creates draw.io compatible XML diagrams
- **Libraries Handler**: Manages icon libraries and search
- **Configuration Manager**: Handles settings and API keys

### File Structure
```
Diagrams_Creator/
├── app.py                 # Main Flask application
├── ai_processor.py        # AI processing and analysis
├── diagram_generator.py   # Diagram generation logic
├── libs_handler.py        # Icon library management
├── config.py             # Configuration settings
├── templates/            # HTML templates
├── static/               # CSS, JS, and static assets
├── Libs/                 # Icon libraries
│   ├── azure/           # Azure icons
│   ├── aws/             # AWS icons
│   ├── connections_arrows.xml
│   ├── aws_complete.xml
│   ├── azure_complete.xml
│   └── general_icons.xml
└── outputs/             # Generated diagrams
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key
LOG_LEVEL=INFO

# AI Processing
AI_TEMPERATURE=0.7
MAX_TOKENS=2000
```

### Icon Library Configuration
The application automatically loads icon libraries from the `Libs/` directory:
- XML files with mxlibrary format
- SVG files in subdirectories
- PNG files for raster icons

## 🎨 Customization

### Adding New Icon Libraries
1. Create XML file in `Libs/` directory
2. Use mxlibrary format:
```xml
<mxlibrary>
[
  {
    "data": "data:image/svg+xml;base64,...",
    "w": 48,
    "h": 48,
    "title": "Icon Name",
    "desc": "Icon description"
  }
]
</mxlibrary>
```

### Custom Architecture Patterns
Add new patterns in `ai_processor.py`:
```python
def _create_custom_architecture(self, text: str) -> Dict[str, Any]:
    # Your custom architecture logic
    return {
        'title': 'Custom Architecture',
        'components': [...],
        'connections': [...]
    }
```

## 📊 API Reference

### Endpoints

#### Generate Diagram
- **POST** `/api/generate-diagram`
- **Body**: `{"input_text": "architecture description"}`
- **Response**: Diagram metadata and ID

#### Get Diagram
- **GET** `/api/diagram/{diagram_id}`
- **Response**: Draw.io XML format

#### Export Diagram
- **GET** `/api/export/{diagram_id}/{format}`
- **Formats**: `png`, `svg`, `pdf`, `xml`

#### Health Check
- **GET** `/api/health`
- **Response**: Application status and statistics

#### Library Icons
- **GET** `/api/library-icons/{library_name}`
- **Response**: List of icons in library

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t diagrams-creator .
docker run -p 5000:5000 diagrams-creator
```

### Environment Setup
- **Development**: `FLASK_ENV=development`
- **Production**: `FLASK_ENV=production`
- **Testing**: `FLASK_ENV=testing`

## 🔍 Troubleshooting

### Common Issues

#### Libraries Not Loading
- Check `Libs/` directory exists
- Verify XML files are valid
- Check file permissions

#### AI Provider Errors
- Verify API keys are correct
- Check network connectivity
- Review API quotas and limits

#### Diagram Generation Fails
- Check input text format
- Verify icon libraries are loaded
- Review application logs

### Logging
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linting
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Draw.io**: For the diagram format and inspiration
- **Eraser.io**: For architecture diagram best practices
- **Cloud Providers**: For official icon libraries
- **Open Source Community**: For various libraries and tools

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This README
- **Examples**: Check the `examples/` directory

## 🔮 Roadmap

### Upcoming Features
- [ ] Real-time collaboration
- [ ] Version control for diagrams
- [ ] Advanced AI models integration
- [ ] Custom template support
- [ ] Team workspaces
- [ ] Advanced export options
- [ ] Integration with popular tools
- [ ] Mobile app support

### Performance Improvements
- [ ] Caching for faster generation
- [ ] Background processing
- [ ] Optimized icon loading
- [ ] Database integration
- [ ] CDN for static assets

---

**Made with ❤️ for the architecture community**