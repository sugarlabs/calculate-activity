# Calculate Activity

A powerful infix-notation graphing calculator for the Sugar desktop environment that enables mathematical exploration and learning.

## Features

- **Infix Notation**: Type mathematical expressions naturally
- **Graphing Capabilities**: Visualize mathematical functions
- **Toolbars**: Quick access to mathematical functions and operators
- **Educational Focus**: Designed for learning mathematics concepts
- **Sugar Integration**: Seamlessly integrates with the Sugar desktop

## How to use?

### Basic Usage

1. **Launch Calculate** from the Sugar activity launcher
2. **Type expressions** using standard mathematical notation (e.g., `2+2*3`)
3. **Use toolbars** to insert mathematical functions and symbols
4. **Press Return** to evaluate expressions
5. **Graph functions** by entering expressions with variables

### Advanced Features

- **Function Graphing**: Plot mathematical functions in 2D
- **Mathematical Functions**: Access trigonometric, logarithmic, and statistical functions
- **Variable Support**: Use variables in expressions
- **Expression History**: Recall previous calculations

## Installation

### Sugar Desktop

Calculate is part of the Sugar desktop environment. Please refer to:

- [How to Get Sugar on sugarlabs.org](https://sugarlabs.org/)
- [How to use Sugar](https://help.sugarlabs.org/)
- [How to use Calculate](https://help.sugarlabs.org/calculate.html)

### Linux Distributions

#### Debian/Ubuntu

```bash
sudo apt install sugar-calculate-activity
```

#### Fedora

```bash
sudo dnf install sugar-calculate
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sugarlabs/calculate-activity
cd calculate-activity

# Install dependencies (Ubuntu/Debian)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Run the activity
python3 calculate.py
```

## Development

### File Structure

```
calculate-activity/
├── activity/
│   └── activity.info          # Sugar activity manifest
├── calculate.py               # Main application entry point
├── astparser.py               # Abstract syntax tree parser
├── constants.py               # Mathematical constants
├── functions.py               # Mathematical functions
├── layout.py                  # UI layout management
├── mathlib.py                 # Core mathematical library
├── numerals.py                # Number system support
├── plotlib.py                 # Graphing functionality
├── rational.py                # Rational number arithmetic
├── toolbars.py                # Toolbar definitions
└── icons/                     # Activity icons
```

### Dependencies

- Python 3
- GTK+ 3
- PyGObject
- Cairo (for graphing)
- Sugar Toolkit

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m "Add feature description"`
5. **Push to your branch**: `git push origin feature-name`
6. **Create a Pull Request** to the `dev` branch

### Development Guidelines

- Follow PEP 8 Python style guidelines
- Test mathematical functions thoroughly
- Ensure Sugar UI consistency
- Update documentation as needed

## Mathematical Capabilities

### Supported Operations

- Basic arithmetic: `+`, `-`, `*`, `/`, `^`
- Parentheses for grouping
- Mathematical functions: `sin`, `cos`, `tan`, `log`, `sqrt`, etc.
- Constants: `pi`, `e`, etc.

### Graphing Features

- 2D function plotting
- Multiple functions on same graph
- Axis configuration
- Zoom and pan capabilities

## Support

### Getting Help

- **Documentation**: [Sugar Labs Wiki](https://wiki.sugarlabs.org/)
- **Community**: [Sugar Labs Mailing Lists](https://lists.sugarlabs.org/)
- **Issues**: [GitHub Issues](https://github.com/sugarlabs/calculate-activity/issues)

### Common Issues

- **Expression not evaluating**: Check syntax and parentheses
- **Graph not displaying**: Ensure expression contains variables
- **Activity not starting**: Verify Sugar dependencies are installed

## License

This project is licensed under the GNU General Public License v3.0. See the [COPYING](COPYING) file for details.

## Credits

- **Sugar Labs**: Maintainer of the Sugar learning platform
- **Contributors**: All developers who have helped improve this activity
- **Mathematical Libraries**: Contributors to the mathematical engine

## Version History

### Current Version

- Enhanced mathematical expression parser
- Improved graphing capabilities
- Better integration with Sugar UI
- Support for additional mathematical functions

---

For more information about Sugar Labs and educational activities, visit [sugarlabs.org](https://sugarlabs.org/).
