# 🌡️ Temperature Playground

A modern, user-friendly GUI application for real-time temperature monitoring and data collection using serial communication. Built with PyQt6 and designed for educational purposes in the 2025 Configurable Logic Design Challenge.

![Image](https://github.com/user-attachments/assets/d6306262-3ff0-40dd-bacc-722578b2476d)

![Temperature Playground](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Real-time Temperature Display**: Live temperature readings in both Celsius and Fahrenheit
- **Serial Communication**: Easy connection to temperature sensors via serial port
- **Data Collection**: Record temperature data with timestamps for analysis
- **Interactive Plotting**: Real-time temperature history visualization using matplotlib
- **Data Export**: Export collected data to CSV format for further analysis
- **Calibration**: Temperature offset calibration for accurate readings
- **Windows Optimized**: Designed and tested for Windows systems
- **Modern UI**: Beautiful, intuitive interface with Microchip blue theme

## 🚀 Quick Start

### Prerequisites

- Windows 10 or later
- Python 3.8 or higher
- Serial port connection to a temperature sensor
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/cfreitas07/TemperaturePlayground.git
   cd TemperaturePlayground
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python serial_terminal.py
   ```

## 📖 Usage Guide

### Connecting to a Sensor

1. **Select Serial Port**: Choose your device's serial port from the dropdown
2. **Set Baud Rate**: Configure the baud rate (default: 9600)
3. **Connect**: Click "Connect" to establish communication
4. **Calibrate**: Optionally set a temperature offset for calibration

### Collecting Data

1. **Start Collection**: Click "Start Collecting" to begin recording
2. **Monitor**: Watch real-time temperature updates and plot
3. **Stop & Export**: Click "Stop & Export" to save data as CSV

### Data Format

The application expects temperature data in the following format:
```
temp: 25.5
25.5°C
25.5
```

## 🛠️ Building Windows Executable

### Using PyInstaller
```bash
pyinstaller --onefile --windowed --name=TemperaturePlayground --icon=temperature.ico serial_terminal.py
```

### Using the Spec File
```bash
pyinstaller serial_terminal.spec
```

The executable will be created in the `dist/` folder as `TemperaturePlayground.exe`.

## 📁 Project Structure

```
TemperaturePlayground/
├── serial_terminal.py      # Main application file
├── requirements.txt        # Python dependencies
├── temperature.ico        # Application icon
├── serial_terminal.spec   # PyInstaller spec file
├── dist/                  # Built executables
└── build/                 # Build artifacts
```

## 🔧 Configuration

### Serial Port Settings
- **Baud Rate**: 9600, 19200, 38400, 57600, 115200
- **Timeout**: 0.1 seconds
- **Data Format**: ASCII

### Temperature Range
- **Valid Range**: -40°C to 125°C
- **Display Precision**: 2 decimal places
- **Plot Update Rate**: 50ms

## 📊 Data Export

Exported CSV files contain:
- **Seconds**: Elapsed time from collection start
- **Temperature (°C)**: Temperature in Celsius
- **Temperature (°F)**: Temperature in Fahrenheit
- **Timestamp**: Full date and time

## 🎨 UI Features

- **Dual Temperature Display**: Large, easy-to-read Celsius and Fahrenheit displays
- **Real-time Plot**: Dynamic temperature history with automatic scaling
- **Status Indicators**: Connection status and current time
- **Responsive Design**: Adapts to different screen sizes
- **Professional Styling**: Microchip blue theme with modern aesthetics

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Claudio de Freitas**
- 2025 Configurable Logic Design Challenge
- Author of Temperature Playground

## 🙏 Acknowledgments

- PyQt6 team for the excellent GUI framework
- Matplotlib for plotting capabilities
- PySerial for serial communication
- The open-source community for inspiration and tools

## 🐛 Known Issues

- Large executable size due to bundled Python dependencies
- First launch may be slower on some systems
- Serial port detection may vary between Windows versions

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/cfreitas07/TemperaturePlayground/issues) page
2. Create a new issue with detailed information
3. Include your Windows version and Python version

## 🔄 Version History

- **v1.0.0**: Initial release with basic temperature monitoring
- Real-time plotting and data export functionality
- Windows executable support

---

⭐ **Star this repository if you find it useful!**
