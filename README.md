# Weather Project

This is a Django-based weather application that fetches and displays current weather data and forecasts for a given city or location using the [WeatherAPI](https://www.weatherapi.com) service.

## Features

- **Backend API Processing**: All API processing is handled on the backend.
- **Search Weather**: Search for a city or country and display weather information including temperature, wind speed, humidity, etc., for the present day.
- **Weather Forecast**: Show a 4-day weather forecast with an option to load more.
- **Weather History**: Save temporary weather information history and allow display again during the day.
- **Email Subscription**: Register and unsubscribe to receive daily weather forecast information via email. Email confirmation is required.
- **Deployment**: Deploy the application to go live.

### Link Website: https://weather-app-0cfs.onrender.com/

### Frontend

- simple HTML + CSS + JavaScript

### Backend

- Use Django (Python) for the backend.
- Implement form validation and logic tightening.
- Follow OOP programming principles.
- User Login,Register,authenticate throught Gmail

### Deployment

### Database

The PostgreSQL database is deployed on [Railway](https://railway.app).

### Django Application

The Django application is deployed on [Render](https://render.com).

1. **Deploy to Render:**

   - Create a new web service on Render.
   - Connect your GitHub repository.
   - Set the build and start commands:

     ```sh
     # Build command
     pip install -r requirements.txt
     python manage.py collectstatic --noinput
     python manage.py migrate

     # Start command
     gunicorn weather_project.wsgi:application
     ```

   - Set the environment variables in the Render dashboard.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/DuyHuynh153/weather_app.git
   cd weather_project
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install the dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory of the project and add the following variables:

   ```env
   SECRET_KEY=your_secret_key
   WEATHER_API_KEY=your_weather_api_key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   MAIL=your_email
   PASSWORD=your_email_password
   ```

5. **Apply database migrations:**

   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**

   ```sh
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```sh
   python manage.py runserver
   ```

8. **Access the application:**

   Open your web browser and go to `http://127.0.0.1:8000`.

## Deployment

2. **Access the deployed application:**

   Open your web browser and go to the URL provided by Render.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any inquiries or feedback, please contact [hlduy1503@example.com](mailto:your-email@example.com).
