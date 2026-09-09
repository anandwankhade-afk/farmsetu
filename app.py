import streamlit as st
import requests
from typing import Optional, Tuple, Dict, Any
import logging
from datetime import datetime

# ---------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# CONFIGURATION CONSTANTS
# ---------------------------------------------------------
class Config:
    """Application configuration constants"""
    # Weather thresholds
    RAIN_PROBABILITY_THRESHOLD = 70
    RAIN_MM_THRESHOLD = 5.0
    HUMIDITY_HIGH = 80
    HUMIDITY_MEDIUM = 65
    TEMP_HEAT_STRESS = 35
    
    # Market thresholds
    TRANSPORT_COST_THRESHOLD = 0.10  # 10% of gross income
    
    # API timeouts
    API_TIMEOUT = 10
    API_MAX_RETRIES = 3
    
    # Cache TTL
    CACHE_TTL = 900  # 15 minutes
    
    # Crop list
    CROPS = [
        "Soybean",
        "Wheat",
        "Rice",
        "Cotton",
        "Maize",
        "Tomato",
        "Onion",
        "Potato",
        "Sugarcane",
        "Other"
    ]
    
    # Soil types
    SOIL_TYPES = [
        "Black Soil",
        "Red Soil",
        "Alluvial Soil",
        "Sandy Soil",
        "Clay Soil",
        "Laterite Soil",
        "Other"
    ]


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="FarmSetu",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌾 FarmSetu")
st.caption("AI-powered agriculture & farmer market assistant")


# ---------------------------------------------------------
# WEATHER FUNCTIONS
# ---------------------------------------------------------
@st.cache_data(ttl=Config.CACHE_TTL)
def geocode(city: str) -> Optional[Tuple[float, float, str, str]]:
    """
    Geocode a city name to latitude and longitude.
    
    Args:
        city: City name
        
    Returns:
        Tuple of (latitude, longitude, city_name, country) or None if not found
    """
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=Config.API_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            logger.warning(f"No results found for city: {city}")
            return None

        location = data["results"][0]

        return (
            location.get("latitude"),
            location.get("longitude"),
            location.get("name", city),
            location.get("country", "Unknown")
        )
        
    except requests.Timeout:
        logger.error(f"Geocoding API timeout for city: {city}")
        st.error("⏱️ Geocoding service timed out. Please try again.")
        return None
    except requests.RequestException as e:
        logger.error(f"Geocoding API error: {e}")
        st.error(f"❌ Geocoding service error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in geocoding: {e}")
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


@st.cache_data(ttl=Config.CACHE_TTL)
def get_weather(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    Fetch weather forecast for given coordinates.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Weather data dictionary or None if failed
    """
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "rain,"
                    "wind_speed_10m"
                ),
                "hourly": (
                    "precipitation_probability,"
                    "precipitation,"
                    "et0_fao_evapotranspiration"
                ),
                "forecast_days": 3,
                "timezone": "auto"
            },
            timeout=Config.API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
        
    except requests.Timeout:
        logger.error(f"Weather API timeout for coordinates: {latitude}, {longitude}")
        st.error("⏱️ Weather service timed out. Please try again.")
        return None
    except requests.RequestException as e:
        logger.error(f"Weather API error: {e}")
        st.error(f"❌ Weather service error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather: {e}")
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


# ---------------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------------
def validate_weather_data(weather: Dict[str, Any]) -> bool:
    """
    Validate weather data structure.
    
    Args:
        weather: Weather data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["current", "hourly"]
    for field in required_fields:
        if field not in weather:
            logger.error(f"Missing required field in weather data: {field}")
            return False
    
    # Validate current data
    current_required = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
    for field in current_required:
        if field not in weather["current"]:
            logger.error(f"Missing field in current weather: {field}")
            return False
    
    # Validate hourly data
    hourly_required = ["precipitation_probability", "precipitation"]
    for field in hourly_required:
        if field not in weather["hourly"]:
            logger.error(f"Missing field in hourly weather: {field}")
            return False
        if not weather["hourly"][field]:
            logger.error(f"Empty hourly data for field: {field}")
            return False
    
    return True


# ---------------------------------------------------------
# FARM ANALYSIS
# ---------------------------------------------------------
def farm_analysis(moisture: float, weather: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze farm conditions based on soil moisture and weather.
    
    Args:
        moisture: Soil moisture percentage (0-100)
        weather: Weather data dictionary
        
    Returns:
        Analysis results dictionary
    """
    if not validate_weather_data(weather):
        logger.error("Invalid weather data")
        return None
    
    try:
        current = weather["current"]
        hourly = weather["hourly"]
        
        # Extract hourly data safely
        precip_prob = hourly.get("precipitation_probability", [])
        precip_mm = hourly.get("precipitation", [])
        
        # Get next 12 hours of data
        rain_probability = max(precip_prob[:12]) if precip_prob else 0
        expected_rain = sum(precip_mm[:12]) if precip_mm else 0
        
        temperature = float(current.get("temperature_2m", 0))
        humidity = float(current.get("relative_humidity_2m", 0))
        wind = float(current.get("wind_speed_10m", 0))
        
        # Validate moisture bounds
        if moisture < 0 or moisture > 100:
            logger.warning(f"Soil moisture out of bounds: {moisture}")
            moisture = max(0, min(100, moisture))
        
        # IRRIGATION LOGIC
        if rain_probability >= Config.RAIN_PROBABILITY_THRESHOLD or expected_rain >= Config.RAIN_MM_THRESHOLD:
            irrigation = "LOW"
            irrigation_note = "🌧️ Rain is likely. Avoid irrigation for now."
        elif moisture < 30:
            irrigation = "HIGH"
            irrigation_note = "⚠️ Soil moisture is critical. Irrigation required urgently."
        elif moisture < 50:
            irrigation = "MEDIUM"
            irrigation_note = "💧 Monitor soil moisture. Moderate irrigation may be needed."
        else:
            irrigation = "LOW"
            irrigation_note = "✅ Soil moisture appears adequate."
        
        # SPRAYING LOGIC
        if rain_probability >= 60:
            spraying = "NOT RECOMMENDED"
            spraying_note = "🚫 Avoid pesticide/fertilizer spraying as rain is likely."
        else:
            spraying = "POSSIBLE"
            spraying_note = "✅ Weather may be suitable for spraying. Follow product label and local advice."
        
        # DISEASE RISK LOGIC
        if humidity >= Config.HUMIDITY_HIGH:
            disease = "HIGH"
        elif humidity >= Config.HUMIDITY_MEDIUM:
            disease = "MEDIUM"
        else:
            disease = "LOW"
        
        # NOTES
        notes = [irrigation_note, spraying_note]
        
        if disease == "HIGH":
            notes.append(
                "🐛 High humidity increases fungal disease risk. Inspect crop regularly."
            )
        
        if disease == "MEDIUM":
            notes.append(
                "🌡️ Moderate humidity. Continue monitoring for disease signs."
            )
        
        if temperature >= Config.TEMP_HEAT_STRESS:
            notes.append(
                f"🔥 High temperature ({temperature}°C). Monitor crop heat stress and soil moisture."
            )
        
        if temperature < 5:
            notes.append(
                f"❄️ Low temperature ({temperature}°C). Risk of frost damage."
            )
        
        if wind >= 40:
            notes.append(
                f"💨 Strong winds ({wind} km/h). Secure loose items and watch for physical damage."
            )
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "rain_probability": rain_probability,
            "expected_rain": expected_rain,
            "wind": wind,
            "irrigation": irrigation,
            "spraying": spraying,
            "disease": disease,
            "notes": notes
        }
        
    except Exception as e:
        logger.error(f"Error in farm analysis: {e}")
        return None


# ---------------------------------------------------------
# MARKET CALCULATOR
# ---------------------------------------------------------
def calculate_market(quantity: float, price: float, transport: float) -> Tuple[float, float, float]:
    """
    Calculate market analysis metrics.
    
    Args:
        quantity: Produce quantity in kg
        price: Market price per kg in rupees
        transport: Transportation cost in rupees
        
    Returns:
        Tuple of (gross_income, net_income, effective_price)
    """
    try:
        quantity = float(quantity)
        price = float(price)
        transport = float(transport)
        
        if quantity <= 0:
            logger.warning("Quantity must be greater than 0")
            return 0, 0, 0
        
        gross_income = quantity * price
        net_income = gross_income - transport
        effective_price = net_income / quantity if quantity > 0 else 0
        
        return gross_income, net_income, effective_price
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating market: {e}")
        return 0, 0, 0


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.header("👨‍🌾 Farmer Information")
    
    city = st.text_input(
        "📍 Your City",
        "Pune",
        help="Enter your city name for weather and location data"
    ).strip()
    
    crop = st.selectbox(
        "🌱 Crop",
        Config.CROPS,
        help="Select the crop you're growing"
    )
    
    quantity = st.number_input(
        "⚖️ Produce Quantity (kg)",
        min_value=1.0,
        value=1000.0,
        step=10.0,
        help="Total quantity of produce you want to sell"
    )
    
    market_price = st.number_input(
        "💰 Expected Market Price (₹/kg)",
        min_value=0.0,
        value=40.0,
        step=0.5,
        help="Current market price per kilogram"
    )
    
    transport_cost = st.number_input(
        "🚚 Transportation Cost (₹)",
        min_value=0.0,
        value=1000.0,
        step=100.0,
        help="Total transportation cost to market"
    )
    
    soil = st.selectbox(
        "🪨 Soil Type",
        Config.SOIL_TYPES,
        help="Select your soil type for recommendations"
    )
    
    moisture = st.slider(
        "💧 Soil Moisture (%)",
        0,
        100,
        45,
        help="Current soil moisture percentage (0-100%)"
    )
    
    farm_size = st.number_input(
        "🌾 Farm Size (acres)",
        min_value=0.1,
        max_value=10000.0,
        value=1.0,
        step=0.1,
        help="Total farm size in acres"
    )
    
    st.divider()
    
    analyze = st.button(
        "🔍 Analyze Farm",
        type="primary",
        use_container_width=True
    )


# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------
if analyze:
    if not city:
        st.error("❌ Please enter a city name.")
        st.stop()
    
    try:
        with st.spinner("🔄 Analyzing your farm..."):
            # LOCATION
            location = geocode(city)
            
            if not location:
                st.error("❌ City not found. Please try another city.")
                st.stop()
            
            latitude, longitude, location_name, country = location
            
            # WEATHER
            weather = get_weather(latitude, longitude)
            
            if not weather:
                st.error("❌ Could not fetch weather data. Please try again.")
                st.stop()
            
            # FARM ANALYSIS
            analysis = farm_analysis(moisture, weather)
            
            if not analysis:
                st.error("❌ Error analyzing farm conditions. Please try again.")
                st.stop()
            
            # MARKET CALCULATION
            gross_income, net_income, effective_price = calculate_market(
                quantity,
                market_price,
                transport_cost
            )
            
            st.success(
                f"✅ Farm analysis completed for {location_name}, {country}"
            )
        
        # -------------------------------------------------
        # MARKET SECTION
        # -------------------------------------------------
        st.header("💰 Farm Market Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "Produce",
            f"{quantity:,.0f} kg"
        )
        
        col2.metric(
            "Market Price",
            f"₹{market_price:,.2f}/kg"
        )
        
        col3.metric(
            "Gross Income",
            f"₹{gross_income:,.0f}"
        )
        
        col4.metric(
            "Net Income",
            f"₹{net_income:,.0f}"
        )
        
        st.subheader("🏆 Selling Analysis")
        
        if net_income > 0:
            st.success(
                f"✅ Estimated net income: ₹{net_income:,.0f}"
            )
            
            st.info(
                f"After transportation costs, your effective selling price is "
                f"approximately **₹{effective_price:,.2f}/kg**."
            )
            
            if transport_cost > gross_income * Config.TRANSPORT_COST_THRESHOLD:
                st.warning(
                    "⚠️ **Transportation Alert**: Transportation is taking a significant "
                    "portion of your expected income. Consider:"
                )
                st.write(
                    "- Finding a closer market\n"
                    "- Using collective transport with other farmers\n"
                    "- Looking for bulk buyer options\n"
                    "- Negotiating transport rates"
                )
            else:
                st.success(
                    "✅ **Good Control**: Transportation cost is well-managed "
                    "compared to your gross income."
                )
        
        elif net_income < 0:
            st.error(
                f"❌ **Not Profitable**: Your estimated transportation cost (₹{transport_cost:,.0f}) "
                f"exceeds gross income (₹{gross_income:,.0f})."
            )
            st.warning(
                "Recommendations:\n"
                "- Increase market price if possible\n"
                "- Reduce transportation costs\n"
                "- Increase production quantity\n"
                "- Consider selling directly to consumers or local markets"
            )
        
        else:
            st.info(
                "⚠️ **Break Even**: Your income equals transportation costs. "
                "Consider the recommendations above."
            )
        
        # -------------------------------------------------
        # AI-STYLE RECOMMENDATION
        # -------------------------------------------------
        st.subheader("🤖 FarmSetu Recommendation")
        
        if net_income > gross_income * 0.30:
            st.success(
                f"✅ **Excellent Opportunity**: Selling {crop} at ₹{market_price:,.2f}/kg "
                f"gives an estimated net income of ₹{net_income:,.0f}. This represents a strong profit margin."
            )
        
        elif net_income > 0:
            st.info(
                f"💡 **Moderate Opportunity**: Selling {crop} at ₹{market_price:,.2f}/kg "
                f"gives an estimated net income of ₹{net_income:,.0f}. Monitor market trends for better prices."
            )
        
        else:
            st.warning(
                f"⚠️ **Consider Alternatives**: With current prices and costs, "
                f"selling at ₹{market_price:,.2f}/kg may not be profitable. "
                f"Explore direct sales or premium markets."
            )
        
        # -------------------------------------------------
        # WEATHER
        # -------------------------------------------------
        st.header("🌦️ Weather-Based Farming Advice")
        
        weather_cols = st.columns(5)
        
        weather_cols[0].metric(
            "Temperature",
            f'{analysis["temperature"]:.1f} °C'
        )
        
        weather_cols[1].metric(
            "Humidity",
            f'{analysis["humidity"]:.0f}%'
        )
        
        weather_cols[2].metric(
            "Rain Probability",
            f'{analysis["rain_probability"]:.0f}%'
        )
        
        weather_cols[3].metric(
            "Expected Rain",
            f'{analysis["expected_rain"]:.1f} mm'
        )
        
        weather_cols[4].metric(
            "Wind",
            f'{analysis["wind"]:.1f} km/h'
        )
        
        # -------------------------------------------------
        # FARM RECOMMENDATIONS
        # -------------------------------------------------
        st.header("🌱 Farm Recommendations")
        
        recommendation_cols = st.columns(3)
        
        recommendation_cols[0].metric(
            "💧 Irrigation",
            analysis["irrigation"]
        )
        
        recommendation_cols[1].metric(
            "🌿 Spraying",
            analysis["spraying"]
        )
        
        recommendation_cols[2].metric(
            "🐛 Disease Risk",
            analysis["disease"]
        )
        
        st.subheader("📋 Action Items")
        for i, note in enumerate(analysis["notes"], 1):
            st.info(note)
        
        # -------------------------------------------------
        # FARM PROFILE
        # -------------------------------------------------
        st.header("🌾 Farm Profile")
        
        profile_data = {
            "Crop": crop,
            "Soil Type": soil,
            "Farm Size": f"{farm_size:.2f} acres",
            "Soil Moisture": f"{moisture}%",
            "Location": f"{location_name}, {country}",
            "Coordinates": f"{latitude:.2f}°N, {longitude:.2f}°E"
        }
        
        col1, col2 = st.columns(2)
        with col1:
            for key, value in list(profile_data.items())[:3]:
                st.write(f"**{key}:** {value}")
        with col2:
            for key, value in list(profile_data.items())[3:]:
                st.write(f"**{key}:** {value}")
        
        # -------------------------------------------------
        # DISCLAIMER
        # -------------------------------------------------
        st.divider()
        st.caption(
            "📋 **Disclaimer**: FarmSetu is an AI-powered prototype. Market prices, "
            "transport costs, and recommendations should be verified with current local "
            "market data and agricultural experts before making financial or farming decisions. "
            "Always consult with local agricultural extension services for region-specific guidance."
        )
        
        st.caption(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Weather data courtesy of Open-Meteo | Location data from OpenStreetMap"
        )
    
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=True)
        st.error(f"❌ Something went wrong: {str(error)}")
        st.info("Please try again or contact support if the issue persists.")

else:
    st.info(
        "👈 **Welcome to FarmSetu!**\n\n"
        "Enter your farm information in the sidebar and click **Analyze Farm** to start. "
        "We'll provide real-time weather-based recommendations and market analysis."
    )
    
    # Show features
    with st.expander("ℹ️ About FarmSetu", expanded=False):
        st.markdown(
            """
            FarmSetu is an AI-powered agriculture assistant that helps farmers with:
            
            🌦️ **Weather Analysis**
            - Real-time weather data for your location
            - Irrigation and spraying recommendations
            - Disease risk assessment based on humidity
            
            💰 **Market Intelligence**
            - Calculate net income after transport costs
            - Understand your effective selling price
            - Identify profitable opportunities
            
            🌱 **Farm Recommendations**
            - Soil moisture monitoring
            - Crop-specific guidance
            - Temperature and wind alerts
            
            **Data Sources:**
            - Weather: Open-Meteo API
            - Location: OpenStreetMap Geocoding
            - Free and no API key required!
            """
        )
