#Imports
import machine
import time
import network
import socket
import esp
import urequests
try:
    import usocket as socket
except:
    import socket
import _thread
import gc

def delay(n):
  time.sleep(n / 1000)

#Turn off debug mode
esp.osdebug(None)
#Garbage collector
gc.collect()

def wifi():
  ap = network.WLAN(network.AP_IF) # create access-point interface
  ap.config(essid='ESP-AP') # set the ESSID of the access point
  ap.config(max_clients=10) # set how many clients can connect to the network
  ap.active(True)         # activate the interface

  print('Connection successful')
  print(ap.ifconfig())

def web_page(count):
  html = """
  <html>
    <head>
      <title>ESP Web Server</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {
          background: #eee;
        }
        .container {
          width: min(700px, 90vw);
          margin: 100px auto;
          text-align: center;
          display: flex;
          flex-direction: column
        }
        .count {
          font-size: 80px;
        }
        .buttons {
          margin: 20px;
          display: flex;
          justify-content: center;
        }
        button {
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          border: none;
          margin: 10px;
        }
        a {
          color: #000;
          text-decoration: none;
        }
        .increment {
          background-color: #3B5998;
        }
        .increment:hover {
          background-color: #0F3B76;
        }
        .decrement {
          background-color: #43C5A5;
        }
        .decrement:hover {
          background-color: #20ACA2;
        }
        .reset {
          background-color: #D0021B;
        }
        .reset:hover {
          background-color: #c00010;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="count">
          """+ str(count) + """
        </div>
        <div class="buttons">
          <a href="/?action=increment" ><button class="increment">Increment</button></a>
          <a href="/?action=reset" ><button class="reset">Reset</button></a>
          <a href="/?action=decrement" ><button class="decrement">Decrement</button></a>
        </div>
      </div>
    </body>
     <script>
      let currentCount = 0;
      let xhttp = new XMLHttpRequest();
      function updateCount() {
        let newCount = 0;
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            newCount = xhttp.responseText;
            if (newCount != currentCount) {
              document.querySelector('.count').innerHTML = newCount;
              currentCount = newCount;
            }
          }
        };
        xhttp.open('GET', '?action=getCount', true);
        xhttp.send();
        setTimeout(updateCount, 500);
      }
      updateCount();
      </script>
  </html>"""
  return html

count = 0

def increment_interrupt(pin):
  global count
  if count == 15:
    count = 0
  else:
    count += 1
  displayNumber(count)
  delay(1000)

def decrement_interrupt(pin):
  global count
  if count == 0:
      count = 15
  else:
    count -= 1
  displayNumber(count)
  delay(1000)

def reset_interrupt(pin):
  global count
  count = 0
  displayNumber(count)
  delay(1000)

def server():
  global count
  increment_button = machine.Pin(23, machine.Pin.IN, machine.Pin.PULL_UP)
  increment_button.irq(handler=increment_interrupt, trigger=machine.Pin.IRQ_FALLING)
  decrement_button = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
  decrement_button.irq(handler=decrement_interrupt, trigger=machine.Pin.IRQ_FALLING)
  reset_button = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
  reset_button.irq(handler=reset_interrupt, trigger=machine.Pin.IRQ_FALLING)
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(('', 80))
  s.listen(5)
  while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = str(request)
    increment = request.find('/?action=increment')
    decrement = request.find('/?action=decrement')
    reset = request.find('/?action=reset')
    getCount = request.find('/?action=getCount')
    if increment == 6:
      if (count == 15):
        count = 0
      else:
        count += 1
    if decrement == 6:
      if count == 0:
        count = 15
      else:
        count -= 1
    if reset == 6:
      count = 0
    if getCount == 6:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall('%s' % count)
      conn.close()
      continue

    displayNumber(count)
    response = web_page(count)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

def displayNumber(count):
  #VCC
  vcc = machine.Pin(5, machine.Pin.OUT)
  vcc.on()
  #7 segment pins
  a = machine.Pin(13, machine.Pin.OUT)
  b = machine.Pin(12, machine.Pin.OUT)
  c = machine.Pin(14, machine.Pin.OUT)
  d = machine.Pin(27, machine.Pin.OUT)
  e = machine.Pin(26, machine.Pin.OUT)
  f = machine.Pin(25, machine.Pin.OUT)
  g = machine.Pin(33, machine.Pin.OUT)
  if count == 0:
    a.off()
    b.off()
    c.off()
    d.off()
    e.off()
    f.off()
    g.on()
  elif count == 1:
    a.on()
    b.off()
    c.off()
    d.on()
    e.on()
    f.on()
    g.on()
  elif count == 2:
    a.off()
    b.off()
    c.on()
    d.off()
    e.off()
    f.on()
    g.off()
  elif count == 3:
    a.off()
    b.off()
    c.off()
    d.off()
    e.on()
    f.on()
    g.off()
  elif count == 4:
    a.on()
    b.off()
    c.off()
    d.on()
    e.on()
    f.off()
    g.off()
  elif count == 5:
    a.off()
    b.on()
    c.off()
    d.off()
    e.on()
    f.off()
    g.off()
  elif count == 6:
    a.off()
    b.on()
    c.off()
    d.off()
    e.off()
    f.off()
    g.off()
  elif count == 7:
    a.off()
    b.off()
    c.off()
    d.on()
    e.on()
    f.on()
    g.on()
  elif count == 8:
    a.off()
    b.off()
    c.off()
    d.off()
    e.off()
    f.off()
    g.off()
  elif count == 9:
    a.off()
    b.off()
    c.off()
    d.off()
    e.on()
    f.off()
    g.off()
  elif count == 10:
    a.off()
    b.off()
    c.off()
    d.on()
    e.off()
    f.off()
    g.off()
  elif count == 11:
    a.on()
    b.on()
    c.off()
    d.off()
    e.off()
    f.off()
    g.off()
  elif count == 12:
    a.off()
    b.on()
    c.on()
    d.off()
    e.off()
    f.off()
    g.on()
  elif count == 13:
    a.on()
    b.off()
    c.off()
    d.off()
    e.off()
    f.on()
    g.off()
  elif count == 14:
    a.off()
    b.on()
    c.on()
    d.off()
    e.off()
    f.off()
    g.off()
  elif count == 15:
    a.off()
    b.on()
    c.on()
    d.on()
    e.off()
    f.off()
    g.off()

wifi()
server()
