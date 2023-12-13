# Venue Management System - Event Manager

Welcome to the Event Manager Portal! This project, built using the Django framework, serves as an efficient platform for managing conferences, meetings, and events within Tata Steel. Users can log in, access their meetings and schedules, and review today's events, past events, and upcoming events. The integration with Microsoft Outlook ensures seamless calendar synchronization.

## Features

- **User Authentication:** Secure login system for accessing the conference portal.
- **Meetings and Scheduling:** View and manage scheduled meetings.
- **Event Overview:** Get an overview of today's, past, and upcoming events.
- **Outlook Integration:** Sync conference schedule with Microsoft Outlook calendar.

## Installation

To get started with the Tata Steel Conference Portal, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/pulcova/-MSGraph-EventManager-Django
    ```

2. Navigate to the project directory:

    ```bash
    cd portal-main
    ```

3. Install the required dependencies from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Open `oauth_settings.yml` in the project directory.

2. Modify the following values:
   - `client_id`: Your Azure app's client ID.
   - `client_secret`: Your Azure app's client secret.
   - `authority_url`: Authority URL for your Azure app.

## Registering the App on Azure

1. Go to [Azure Portal](https://portal.azure.com/) and log in.

2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**.

3. Fill in details and create the app.

4. Note down the **Client ID** and **Client Secret**.

5. Under **API permissions**, add necessary permissions to read Outlook calendar.

## Usage

1. Run the Django development server:

    ```bash
    python manage.py runserver_plus
    ```

2. Access the Tata Steel Conference Portal at `https://localhost:8000` in your web browser.

3. Log in using your credentials to access meetings, schedule, and events.

## Support

For assistance, contact cloudythought9@outlook.com.

## Contributing

Fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Thank you for choosing the Tata Steel Conference Portal. Enhance your conference management experience with our platform. For questions or suggestions, reach out to us. Happy conferencing! 🎉
