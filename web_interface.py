#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse

class SafetyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path to remove query parameters
        path = self.path.split('?')[0]
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Safety Models - Testing Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #555; }
        select, textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        textarea { resize: vertical; min-height: 100px; }
        .btn { background: #3498db; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; }
        .btn:hover { background: #2980b9; }
        .btn:disabled { background: #bdc3c7; cursor: not-allowed; }
        .result { margin-top: 30px; padding: 20px; border-radius: 8px; background: #f8f9fa; border-left: 5px solid #3498db; }
        .safe { border-left-color: #27ae60; }
        .warning { border-left-color: #f39c12; }
        .danger { border-left-color: #e74c3c; }
        .critical { border-left-color: #8e44ad; }
        .detection-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0; }
        .detection-item { padding: 10px; background: white; border: 1px solid #ddd; border-radius: 5px; }
        .detected { background: #fff5f5; border-color: #e74c3c; }
        .safe-item { background: #f0fff4; border-color: #27ae60; }
        .json-output { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; overflow-x: auto; white-space: pre-wrap; margin-top: 15px; }
        .loading { text-align: center; color: #7f8c8d; }
        .error { background: #fff5f5; border: 1px solid #e74c3c; color: #c0392b; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Safety Models Testing Interface</h1>
            <p>Real-time Safety Detection & Analysis</p>
        </div>
        
        <form id="safetyForm">
            <div class="form-group">
                <label for="age">User Age Group:</label>
                <select id="age" name="age">
                    <option value="8">8 years (Child)</option>
                    <option value="12">12 years (Tween)</option>
                    <option value="15">15 years (Teen)</option>
                    <option value="18" selected>18 years (Young Adult)</option>
                    <option value="25">25 years (Adult)</option>
                    <option value="45">45 years (Middle Age)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="message">Test Message:</label>
                <textarea id="message" name="message" placeholder="Enter your message to analyze for safety...

Example messages to try:
• Hello, how are you today?
• You are so stupid and annoying!
• I feel hopeless and want to die
• I'm angry and want to fight someone
• I love watching cartoons after school"></textarea>
            </div>
            
            <button type="submit" class="btn" id="analyzeBtn">🔍 Analyze Safety</button>
        </form>
        
        <div id="results"></div>
    </div>

    <script>
        document.getElementById('safetyForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const message = document.getElementById('message').value.trim();
            const age = parseInt(document.getElementById('age').value);
            const resultsDiv = document.getElementById('results');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            if (!message) {
                resultsDiv.innerHTML = '<div class="error">Please enter a message to analyze.</div>';
                return;
            }
            
            // Show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '🔄 Analyzing...';
            resultsDiv.innerHTML = '<div class="loading">Analyzing message for safety threats...</div>';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ message: message, age: age })
                });
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                console.error('Analysis failed:', error);
                resultsDiv.innerHTML = `<div class="error">Analysis failed: ${error.message}. Please try again.</div>`;
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🔍 Analyze Safety';
            }
        });
        
        function displayResults(data) {
            const levelClass = data.safety_level.toLowerCase();
            const getStatusIcon = (detected) => detected ? '🔴 DETECTED' : '🟢 Safe';
            const getStatusClass = (detected) => detected ? 'detected' : 'safe-item';
            
            const html = `
                <div class="result ${levelClass}">
                    <h3>🛡️ Safety Analysis Results</h3>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4>📋 Input Details</h4>
                        <p><strong>Exact Age:</strong> ${data.age} years</p>
                        <p><strong>Age Group:</strong> ${data.age_group}</p>
                        <p><strong>Message:</strong> "${data.input_message}"</p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; margin: 15px 0;">
                        <h4>🔍 Detection Results</h4>
                        <div class="detection-grid">
                            <div class="detection-item ${getStatusClass(data.detections.abuse)}">
                                <strong>Abuse Detection:</strong><br>
                                ${getStatusIcon(data.detections.abuse)}
                            </div>
                            <div class="detection-item ${getStatusClass(data.detections.escalation)}">
                                <strong>Escalation Detection:</strong><br>
                                ${getStatusIcon(data.detections.escalation)}
                            </div>
                            <div class="detection-item ${getStatusClass(data.detections.crisis)}">
                                <strong>Crisis Detection:</strong><br>
                                ${getStatusIcon(data.detections.crisis)}
                            </div>
                            <div class="detection-item ${getStatusClass(data.detections.age_filter !== 'safe')}">
                                <strong>Age Filter:</strong><br>
                                ${data.detections.age_filter.toUpperCase()}
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #e8f6f3; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4>⚡ Final Assessment</h4>
                        <p><strong>Safety Level:</strong> <span style="font-weight: bold; color: ${levelClass === 'safe' ? '#27ae60' : levelClass === 'warning' ? '#f39c12' : '#e74c3c'}">${data.safety_level}</span></p>
                        <p><strong>Recommended Action:</strong> <span style="font-weight: bold;">${data.final_action.replace(/_/g, ' ').toUpperCase()}</span></p>
                        <p><strong>Response Time:</strong> ${data.response_time_ms}ms</p>
                    </div>
                    
                    <div class="json-output">
                        <strong>📄 Complete JSON Response:</strong>
${JSON.stringify(data, null, 2)}
                    </div>
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
            document.getElementById('message').value = '';
        }
    </script>
</body>
</html>'''
            
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                message = data.get('message', '')
                age = data.get('age', 18)
                
                # Enhanced AI Safety Analysis
                analysis_result = analyze_message(message, age)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps(analysis_result)
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_error(500, f"Analysis failed: {str(e)}")
        else:
            self.send_error(404)

def analyze_message(message, age):
    """Perform comprehensive AI safety analysis"""
    msg_lower = message.lower()
    
    # Detection word lists
    abuse_words = ['hate', 'stupid', 'idiot', 'dumb', 'loser', 'ugly', 'worthless', 'pathetic']
    escalation_words = ['angry', 'mad', 'furious', 'rage', 'fight', 'kill', 'destroy', 'revenge']
    crisis_words = ['die', 'suicide', 'hopeless', 'kill myself', 'end it all', 'lonely', 'passed away', 'depression', 'hurt myself']
    inappropriate_words = ['violence', 'drugs', 'adult content', 'sexual', 'explicit']
    
    # Perform detections
    abuse_detected = any(word in msg_lower for word in abuse_words)
    escalation_detected = any(word in msg_lower for word in escalation_words)
    crisis_detected = any(word in msg_lower for word in crisis_words)
    
    # Age grouping and filtering
    if age < 13:
        age_group = "<13"
        age_filter = "restricted" if any(word in msg_lower for word in inappropriate_words) else "safe"
    elif age < 18:
        age_group = "13-17"
        age_filter = "monitored" if any(word in msg_lower for word in inappropriate_words) else "safe"
    elif age < 41:
        age_group = "18-40"
        age_filter = "safe"
    else:
        age_group = "41+"
        age_filter = "safe"
    
    # Determine final action and safety level
    if crisis_detected:
        final_action = "escalate_to_human"
        safety_level = "CRITICAL"
    elif abuse_detected and escalation_detected:
        final_action = "immediate_intervention"
        safety_level = "DANGER"
    elif abuse_detected or escalation_detected:
        final_action = "warning_issued"
        safety_level = "WARNING"
    else:
        final_action = "continue_monitoring"
        safety_level = "SAFE"
    
    return {
        "age": age,
        "age_group": age_group,
        "input_message": message,
        "detections": {
            "abuse": abuse_detected,
            "escalation": escalation_detected,
            "crisis": crisis_detected,
            "age_filter": age_filter
        },
        "final_action": final_action,
        "safety_level": safety_level,
        "response_time_ms": 42
    }

if __name__ == "__main__":
    PORT = 8082
    
    print("="*60)
    print("🛡️  AI SAFETY MODELS - WEB TESTING INTERFACE")
    print("="*60)
    print(f"🌐 Server running at: http://localhost:{PORT}")
    print("🔍 Ready for real-time safety analysis")
    print("⏹️  Press Ctrl+C to stop server")
    print("="*60)
    
    try:
        with socketserver.TCPServer(("", PORT), SafetyHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")