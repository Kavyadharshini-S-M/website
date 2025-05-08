import subprocess
import platform
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# --- Configuration ---
ROVER_IP = "192.168.1.101"  # IMPORTANT: Change this to your rover's IP address
PING_TIMEOUT_S = 1  # Timeout for each ping attempt in seconds

def check_rover_connection(ip_address):
    """
    Pings the given IP address to check for connectivity.
    Returns True if reachable, False otherwise.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W' # -w for windows is in ms
    
    # For Windows, timeout is in milliseconds
    timeout_ms = PING_TIMEOUT_S * 1000 if platform.system().lower() == 'windows' else PING_TIMEOUT_S

    command = ['ping', param, '1', timeout_param, str(timeout_ms), ip_address]
    
    try:
        # Run the command.
        # stdout and stderr are suppressed for a cleaner output unless debugging.
        # check=True will raise CalledProcessError if the command returns a non-zero exit code.
        # However, ping's exit code behavior can vary, so we'll check explicitly.
        process = subprocess.run(command, capture_output=True, text=True, timeout=PING_TIMEOUT_S + 1)
        # On Linux/macOS, exit code 0 is success.
        # On Windows, exit code 0 is success.
        # If timeout occurs within subprocess.run, it raises TimeoutExpired.
        # If ping command itself times out (e.g. -W on Linux), it usually returns exit code 1.
        return process.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Ping command itself timed out for {ip_address}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Ping command failed for {ip_address} with error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while pinging {ip_address}: {e}")
        return False

@app.route('/')
def index():
    # We'll embed the HTML directly here for simplicity
    # In a larger app, you'd use render_template('index.html')
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rover Connection Status</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
                flex-direction: column;
            }
            .status-container {
                display: flex;
                align-items: center;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            #status-light {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                margin-right: 20px;
                transition: background-color 0.5s ease;
            }
            .active {
                background-color: #28a745; /* Green */
                box-shadow: 0 0 15px #28a745;
            }
            .inactive {
                background-color: #dc3545; /* Red */
                box-shadow: 0 0 15px #dc3545;
            }
            .unknown {
                background-color: #ffc107; /* Yellow / Orange */
                box-shadow: 0 0 15px #ffc107;
            }
            #status-text {
                font-size: 24px;
                font-weight: bold;
            }
            .rover-ip {
                margin-top: 15px;
                font-size: 0.9em;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="status-container">
            <div id="status-light" class="unknown"></div>
            <span id="status-text">Checking...</span>
        </div>
        <div class="rover-ip">Monitoring IP: <span id="rover-ip-display"></span></div>

        <script>
            const statusLight = document.getElementById('status-light');
            const statusText = document.getElementById('status-text');
            const roverIpDisplay = document.getElementById('rover-ip-display');
            const POLLING_INTERVAL_MS = 3000; // Check every 3 seconds

            async function fetchRoverStatus() {
                try {
                    const response = await fetch('/api/rover_status');
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    
                    roverIpDisplay.textContent = data.rover_ip || "N/A";

                    if (data.status === 'active') {
                        statusLight.className = 'active';
                        statusText.textContent = 'Connected';
                    } else if (data.status === 'inactive') {
                        statusLight.className = 'inactive';
                        statusText.textContent = 'Disconnected';
                    } else {
                        statusLight.className = 'unknown';
                        statusText.textContent = 'Unknown';
                    }
                } catch (error) {
                    console.error("Error fetching rover status:", error);
                    statusLight.className = 'inactive'; // Or 'unknown' if preferred
                    statusText.textContent = 'Error';
                    // If the Flask server itself is down, this fetch will fail.
                    // The 'inactive' or 'unknown' state is appropriate here.
                }
            }

            // Initial check
            fetchRoverStatus();
            // Periodic checks
            setInterval(fetchRoverStatus, POLLING_INTERVAL_MS);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/api/rover_status')
def rover_status():
    is_connected = check_rover_connection(ROVER_IP)
    if is_connected:
        return jsonify({"status": "active", "rover_ip": ROVER_IP})
    else:
        return jsonify({"status": "inactive", "rover_ip": ROVER_IP})

if __name__ == '__main__':
    # Make sure to use 0.0.0.0 to be accessible from other devices on your network
    # If you only want to access it from the machine running this script, use '127.0.0.1'
    app.run(host='0.0.0.0', port=5000, debug=True)