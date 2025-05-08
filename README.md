Flow of Events (Simplified):
You run python app.py. The backend server starts.
You open http://localhost:5000 in your browser.
Browser requests / from the backend.
Backend sends the HTML/CSS/JS page.
Browser displays the page. The light is initially "Checking..." (yellow).
The JavaScript in the browser immediately runs fetchRoverStatus():
a. JS asks the backend at /api/rover_status: "What's the rover's status?"
b. Backend runs ping to the rover's IP.
c. Backend replies to JS with, for example, {"status": "active", ...}.
d. JS receives this, changes the light to green and text to "Connected".
Every 3 seconds (due to setInterval), step 6 repeats, keeping the status updated.
So, it's a continuous loop: JavaScript asks, Python server pings and answers, JavaScript updates the display. This gives you the live status indicator for your rover's antenna connection.
