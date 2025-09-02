from flask import Flask, render_template_string, jsonify
import threading, time, random


from bitcoin import random_key, privtopub, pubtoaddr

app = Flask(__name__)

global_counter = {"attempts": 0, "found": False, "privKey": "", "addr": ""}
target_address = "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
balance = "$320"


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bitcoin Key Cracker</title>
<style>
  body {margin:0; background:black; color:#00ff00; font-family:"Courier New", monospace; font-size:14px; display:flex; flex-direction:column; height:100vh;}
  .status-bar {background:#003300; display:flex; justify-content:flex-end; flex-wrap:wrap; padding:10px; border-bottom:2px solid #00ff00;}
  .status-item {margin-left:30px; font-weight:bold;}
  .terminal {flex:1; padding:10px; overflow-y:auto; white-space:pre;}
  .line-found {color:yellow; font-weight:bold;}
  ::-webkit-scrollbar {width:6px;}
  ::-webkit-scrollbar-thumb {background:#00ff00; border-radius:3px;}
  @media(max-width:600px){.status-bar{flex-direction:column;align-items:flex-end;}.status-item{margin-left:0;margin-bottom:5px;}}
</style>
</head>
<body>
  <div class="status-bar">
    <div class="status-item" id="attempts">Attempts: 0</div>
    <div class="status-item" id="balance">Balance: {{balance}}</div>
    <div class="status-item" id="target">Target: {{target}}</div>
  </div>
  <div class="terminal" id="output"></div>

<script>
const output = document.getElementById('output');
const attemptsDisplay = document.getElementById('attempts');

function logLine(text, cls=""){
  const line = document.createElement('div');
  if(cls) line.classList.add(cls);
  line.textContent = text;
  output.appendChild(line);
  output.scrollTop = output.scrollHeight;
}

// Har 100ms serverdan global counter oladi
function updateStatus(){
  fetch("/status").then(res=>res.json()).then(data=>{
    attemptsDisplay.textContent = "Attempts: "+data.attempts;
    if(data.found && !document.getElementById("found-line")){
      logLine("FOUND MATCH! 🔑", "line-found");
      logLine("Private Key: "+data.privKey, "line-found");
      const div = document.createElement("div"); div.id="found-line"; output.appendChild(div);
    } else if(!data.found){
      // Random muvaffaqiyatsiz log
      const priv = Math.random().toString(16).substring(2,18);
      const addr = "1"+Math.random().toString(36).substring(2,20);
      logLine("["+data.attempts+"] Addr: "+addr+" | Key: "+priv+" - Not passed ❌");
    }
  }).catch(e=>console.log(e));
}

setInterval(updateStatus, 100);
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, target=target_address, balance=balance)

@app.route("/status")
def status():
    return jsonify(global_counter)

def brute_force():

    while not global_counter["found"]:
        global_counter["attempts"] += 1
        privKey = random_key()
        pubKey = privtopub(privKey)
        addr = pubtoaddr(pubKey)

        if addr == target_address:
            global_counter["found"] = True
            global_counter["privKey"] = privKey
            global_counter["addr"] = addr

        time.sleep(0.03)

if __name__ == "__main__":
    threading.Thread(target=brute_force, daemon=True).start()
    print("Server running: http://127.0.0.1:5000")
    app.run(debug=False)
