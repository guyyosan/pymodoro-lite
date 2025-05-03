# Pymodoro Lite
A lightweight Pomodoro timer application built with PySide6.
Q: Why make another timer?
A: I wanted something that's small and stays on top so I can see it while working.

![Pymodoro Lite Preview](preview.jpg)


## Features

-   Minimalist, always-on-top interface
-   Standard Pomodoro timing (25-minute work sessions, 5-minute short breaks, 15-minute long breaks)
-   Sound notifications
-   Visual session tracking with emojis
-   Frameless, draggable window
-   Minimal system resource usage

## Installation

1. Clone this repository:

    ```
    git clone https://github.com/yourusername/pymodoro-lite.git
    cd pymodoro-lite
    ```

2. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Run the application:
    ```
    python pomodoro_timer.py
    ```

## Usage

-   **⏯️** - Start/Pause the timer
-   **🔁** - Reset the timer
-   **×** - Close the application

The timer will automatically switch between work sessions and breaks, with a double sound notification at each transition.

-   🍅 - Work session
-   ☕ - Short break (5 minutes)
-   ☕☕ - Long break (15 minutes, after 4 work sessions)

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to test your changes thoroughly before submitting a PR.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   PySide6 for the Qt framework bindings
-   Sound effects credits goes to: [stijn](https://freesound.org/people/stijn/) and [5ro4](https://freesound.org/people/5ro4/)
