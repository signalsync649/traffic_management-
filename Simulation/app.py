from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simulation Runner</title>
    </head>
    <body>
        <h1>Simulation Runner</h1>
        <h2>Fixed Timer</h2>
        <button onclick="runScript('fixed_timer', 'simulation')">Run Simulation</button>
        <button onclick="runScript('fixed_timer', 'vehicle_detection')">Run Vehicle Detection</button>
        <h2>SignalSync's Timer</h2>
        <button onclick="runScript('signalsync', 'simulation')">Run Simulation</button>
        <button onclick="runScript('signalsync', 'vehicle_detection')">Run Vehicle Detection</button>

        <script>
            function runScript(folder, script) {
                fetch('/run/' + folder + '/' + script)
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                    });
            }
        </script>
    </body>
    </html>
    """

@app.route('/run/<folder>/<script>')
def run_script(folder, script):
    script_folder = ''
    if folder == 'fixed_timer':
        script_folder = 'fixed_timer'
    elif folder == 'signalsync':
        script_folder = "SignalSync's_Timer"

    if not script_folder:
        return jsonify({"message": "Invalid folder"}), 400

    script_path = os.path.join(script_folder, script + '.py')

    if not os.path.exists(script_path):
        return jsonify({"message": "Script not found"}), 400

    try:
        # Using cwd to run the script in its own directory
        result = subprocess.run(['python', script + '.py'], cwd=script_folder, capture_output=True, text=True, check=True)
        return jsonify({"message": f"Script {script}.py in {folder} executed successfully.\nOutput:\n{result.stdout}"})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"Error running script {script}.py in {folder}.\nError:\n{e.stderr}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
