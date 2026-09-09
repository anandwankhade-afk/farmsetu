# 🌾 FarmSetu

**AI-powered Agriculture & Farmer Market Assistant**

FarmSetu is a web-based application designed to help farmers make informed decisions about irrigation, crop spraying, disease management, and market sales. Using real-time weather data and market analysis, FarmSetu provides actionable recommendations tailored to your farm's specific conditions.

## ✨ Features

### 🌦️ Weather-Based Farming Advice
- Real-time weather data fetched from Open-Meteo API
- Irrigation recommendations based on soil moisture and rainfall
- Spraying advisories considering weather conditions
- Disease risk assessment based on humidity levels
- Temperature and wind alerts

### 💰 Market Analysis
- Calculate net income after transportation costs
- Determine effective selling price per kilogram
- Identify profitable selling opportunities
- Transportation cost optimization insights

### 🌱 Farm Profile Management
- Track crop type and soil conditions
- Monitor soil moisture levels
- Record farm size and location
- Get location-specific recommendations

### 🤖 AI-Powered Recommendations
- Personalized farming advice based on current conditions
- Market opportunity assessment
- Risk indicators and alerts
- Actionable next steps

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for weather and geocoding APIs)

### Step 1: Clone the Repository

```bash
git clone https://github.com/anandwankhade-afk/farmsetu.git
cd farmsetu
```

### Step 2: Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your custom settings if needed
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 Usage Guide

### Starting an Analysis

1. **Enter Your Location**
   - Type your city name in the "Your City" field
   - The app will automatically fetch weather data for your location

2. **Select Your Crop**
   - Choose from popular crops: Soybean, Wheat, Rice, Cotton, Maize, Tomato, Onion, Potato, Sugarcane

3. **Provide Produce Information**
   - Enter quantity in kilograms
   - Input expected market price per kilogram
   - Specify transportation cost

4. **Farm Details**
   - Select your soil type
   - Adjust soil moisture slider (0-100%)
   - Enter your total farm size in acres

5. **Analyze**
   - Click the "🔍 Analyze Farm" button
   - Wait for real-time data processing

### Understanding Results

#### Market Analysis
- **Gross Income**: Quantity × Market Price
- **Net Income**: Gross Income - Transportation Cost
- **Effective Price**: Net Income ÷ Quantity

#### Weather Metrics
- **Temperature**: Current ambient temperature
- **Humidity**: Current relative humidity percentage
- **Rain Probability**: Chance of precipitation in next 12 hours
- **Expected Rain**: Predicted rainfall amount in mm
- **Wind Speed**: Current wind speed in km/h

#### Farm Recommendations
- **Irrigation**: LOW/MEDIUM/HIGH based on soil moisture and rainfall forecast
- **Spraying**: POSSIBLE/NOT RECOMMENDED based on weather
- **Disease Risk**: LOW/MEDIUM/HIGH based on humidity levels

## 📊 Data Sources

- **Weather Data**: [Open-Meteo](https://open-meteo.com/) - Free weather API, no authentication required
- **Location Data**: [OpenStreetMap](https://www.openstreetmap.org/) Geocoding API
- **Market Prices**: User-provided based on local market conditions

## 🔒 Privacy & Security

- No personal data is stored on our servers
- All analysis is performed locally in your browser
- Weather API requests only contain location coordinates
- No authentication or account creation required
- All data is cached locally to reduce API calls

## ⚠️ Disclaimer

FarmSetu is an AI-powered prototype application. The recommendations and market analysis provided are based on general agricultural practices and real-time weather data. **Always verify:**

- Current local market prices before selling
- Transportation costs with actual providers
- Recommendations with local agricultural extension services
- Crop-specific guidance with agricultural experts
- Weather data with official meteorological services

**Use at your own discretion and consult with agricultural professionals before making major decisions.**

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Python web app framework
- **Backend**: Python 3.8+
- **APIs**: Open-Meteo, OpenStreetMap
- **Package Management**: pip

## 📝 Project Structure

```
farmsetu/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── README.md             # This file
├── .env.example          # Environment configuration template
└── .gitignore            # Git ignore rules
```

## 🔧 Configuration

### Adjusting Thresholds

Edit the `Config` class in `app.py` to customize agricultural thresholds:

```python
class Config:
    RAIN_PROBABILITY_THRESHOLD = 70      # % chance of rain
    HUMIDITY_HIGH = 80                   # High humidity limit
    TEMP_HEAT_STRESS = 35                # Heat stress temperature
    # ... more settings
```

## 🐛 Troubleshooting

### Issue: "City not found" error
- **Solution**: Check spelling of city name and try a larger city

### Issue: "Weather service error" message
- **Solution**: Check internet connection and try again
- **Note**: Open-Meteo API is very reliable; the issue is usually connection-related

### Issue: Application runs slowly
- **Solution**: Clear Streamlit cache by running `streamlit cache clear`

### Issue: Numbers don't look right
- **Solution**: Ensure you're entering values in correct units (kg, ₹, acres)

## 📞 Support & Feedback

- **Report Issues**: [GitHub Issues](https://github.com/anandwankhade-afk/farmsetu/issues)
- **Suggestions**: Create a GitHub Discussion or Issue
- **Email**: Open an issue on GitHub for contact information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Weather data provided by [Open-Meteo](https://open-meteo.com/)
- Geocoding by [OpenStreetMap](https://www.openstreetmap.org/) Nominatim
- UI framework by [Streamlit](https://streamlit.io/)

## 🚀 Future Enhancements

- [ ] Historical data analysis
- [ ] Predictive modeling for crop yields
- [ ] Multi-language support
- [ ] Mobile application
- [ ] User accounts and data persistence
- [ ] Integration with agricultural price databases
- [ ] Pest identification with image recognition
- [ ] Export recommendations as PDF

---

**Made with ❤️ for Indian Farmers** 🌾
