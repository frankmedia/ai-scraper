# Contributing to AI Scraper

Thank you for your interest in contributing to AI Scraper! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** and test thoroughly
5. **Submit a pull request**

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## 💡 How Can I Contribute?

### 🐛 Bug Reports

- **Check existing issues** before creating new ones
- **Use the bug report template** if available
- **Include detailed steps** to reproduce the issue
- **Provide error messages** and screenshots if relevant
- **Test on both sites** (Perplexity and ChatGPT) if applicable

### ✨ Feature Requests

- **Describe the feature** clearly and concisely
- **Explain the use case** and benefits
- **Consider implementation complexity**
- **Check if it aligns** with project goals

### 🔧 Code Contributions

We welcome contributions in these areas:

#### Core Functionality
- **Improved selectors** for better element detection
- **Enhanced anti-bot detection** techniques
- **Better error handling** and recovery
- **Performance optimizations**

#### New Platforms
- **Additional AI platforms** (Claude, Gemini, etc.)
- **Platform-specific optimizations**
- **Citation extraction** for new platforms

#### Citation Intelligence
- **Better URL detection** algorithms
- **Company name recognition** improvements
- **Source pattern matching** enhancements
- **Citation filtering** and deduplication

#### User Experience
- **Command-line interface** improvements
- **Configuration options** and flexibility
- **Output format** enhancements
- **Progress reporting** and logging

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Git

### Local Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-scraper.git
   cd ai-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Test the scraper:**
   ```bash
   python3 scraper.py --site perplexity --limit 2
   ```

## 🧪 Testing Guidelines

### Testing Requirements

- **Test on both sites** (Perplexity and ChatGPT) when making changes
- **Use small test datasets** (2-3 prompts) for development
- **Verify citation extraction** works correctly
- **Check error handling** with invalid inputs
- **Test timing and delays** are appropriate

### Test Commands

```bash
# Test Perplexity with 2 prompts
python3 scraper.py --site perplexity --limit 2

# Test ChatGPT with 2 prompts  
python3 scraper.py --site chatgpt --limit 2

# Test with custom prompts
python3 scraper.py --site perplexity --prompts-csv test_prompts.csv --limit 3

# Test in headful mode for debugging
python3 scraper.py --site perplexity --headful --limit 1
```

### Test Data

Create `test_prompts.csv` with simple, reliable prompts:
```csv
What is artificial intelligence?
How does machine learning work?
What are the benefits of automation?
```

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure your code works** on both sites
2. **Test with different prompt types**
3. **Update documentation** if needed
4. **Follow the code style** guidelines
5. **Include error handling** for edge cases

### Pull Request Template

```markdown
## Description
Brief description of changes and why they're needed.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested on Perplexity
- [ ] Tested on ChatGPT
- [ ] Tested with custom prompts
- [ ] Verified citation extraction

## Screenshots/Examples
If applicable, include screenshots or examples.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Error handling included
- [ ] Documentation updated
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing verification** on both sites
4. **Documentation review** if applicable
5. **Final approval** and merge

## 📝 Code Style

### Python Conventions

- **Follow PEP 8** style guidelines
- **Use meaningful variable names**
- **Add docstrings** for functions and classes
- **Keep functions focused** and under 50 lines
- **Use type hints** where helpful

### Example Code Style

```python
def extract_citations(driver, site_type: str) -> set:
    """
    Extract citations from the current answer.
    
    Args:
        driver: Selenium WebDriver instance
        site_type: Either 'perplexity' or 'chatgpt'
        
    Returns:
        Set of citation strings (URLs, company names, etc.)
    """
    links = set()
    
    try:
        # Site-specific citation extraction logic
        if site_type == "perplexity":
            links.update(_extract_perplexity_citations(driver))
        elif site_type == "chatgpt":
            links.update(_extract_chatgpt_citations(driver))
            
    except Exception as e:
        print(f"⚠️  Error extracting citations: {e}")
        
    return links
```

### Error Handling

- **Use specific exception types** when possible
- **Provide meaningful error messages**
- **Include context** for debugging
- **Handle edge cases** gracefully
- **Log errors** for troubleshooting

## 📚 Documentation

### Code Documentation

- **Document complex logic** with clear comments
- **Explain selectors** and why they're used
- **Document timing values** and their purpose
- **Include examples** for configuration options

### User Documentation

- **Update README.md** for new features
- **Add usage examples** for new options
- **Document configuration** changes
- **Include troubleshooting** tips

### API Documentation

- **Document function parameters** and return values
- **Include usage examples** for key functions
- **Explain error conditions** and handling
- **Document configuration** options

## 🎯 Project Goals

### Primary Objectives

1. **Reliable scraping** of AI platforms
2. **Intelligent citation extraction** from various formats
3. **Anti-bot detection** avoidance
4. **Easy configuration** and customization
5. **Cross-platform compatibility**

### Future Directions

- **Support for more AI platforms**
- **Advanced machine learning** for citation detection
- **Distributed scraping** capabilities
- **Real-time monitoring** and alerts
- **Integration APIs** for other tools

## 🆘 Getting Help

### Questions and Support

- **Check existing issues** for similar problems
- **Search documentation** for solutions
- **Ask in discussions** or issues
- **Provide context** when asking for help

### Communication Channels

- **GitHub Issues** for bug reports and feature requests
- **GitHub Discussions** for questions and ideas
- **Pull Requests** for code contributions
- **Documentation** for usage guidance

## 🙏 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **Project documentation** where applicable

Thank you for contributing to making AI Scraper better for everyone!
