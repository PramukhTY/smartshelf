import paho.mqtt.client as mqtt
import smtplib
from email.message import EmailMessage
import winsound  # Standard Windows module for playing simple sounds
import time      # Required to pause between beeps

# --- 🎯 Configuration: UPDATE THESE VALUES! 🎯 ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
# Must match your Arduino/Wokwi code
MQTT_TOPIC = "smart-shelf/alert/project-sit-123"

# Email Configuration 
SENDER_EMAIL = "pramukhty2005@gmail.com" # SENDER EMAIL ADDRESS
SENDER_PASSWORD = "ebchoifrdcidlqvg" # SENDER APP PASSWORD
RECEIVER_EMAIL = "rvirat154@gmail.com"# RECIPIENT EMAIL ADDRESS
SMTP_SERVER = "smtp.gmail.com" # Gmail SMTP server
SMTP_PORT = 587  # Standard port for TLS

# -------------------------------------------------------------------

# --- Email Function ---
def send_alert_email(subject, body):
    """Handles the actual connection and sending of the email."""
    print("Attempting to send email...")
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg.set_content(body)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Secure the connection with TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            print("✅ Email alert sent successfully!")

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("Please check your email configuration, App Password, and SMTP details.")

# --- Sound Function (Plays 5 times) ---
def play_alert_sound():
    """Plays a built-in Windows system beep 5 times for an audible alert."""
    print("🔈 Playing alert beep 5 times...")
    try:
        # Loop 5 times to repeat the beep
        for i in range(5):
            # Plays a beep at 1000 Hz for 200 milliseconds
            winsound.Beep(frequency=1000, duration=200) 
            
            # Pause for 0.1 seconds between beeps
            time.sleep(0.1) 
            
    except Exception as e:
        # This catch is mostly for systems that aren't Windows
        print(f"❌ Error playing sound using winsound. (Only works on Windows): {e}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    """The callback for when the client connects to the MQTT broker."""
    if reason_code == 0:
        print("✅ Connected to MQTT Broker.")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Connection failed with result code {reason_code}")

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    payload = msg.payload.decode()
    print(f"\n--- MQTT ALERT RECEIVED ---")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {payload}")
    print("---------------------------")
    
    # 1. Trigger the email
    email_subject = "🚨 LOW STOCK ALERT from Smart Shelf"
    email_body = f"The smart shelf is running LOW on stock.\n\nMessage from device: {payload}\n\nAction Required: Please restock the items."
    send_alert_email(email_subject, email_body)
    
    # 2. Trigger the sound alert
    play_alert_sound()

# --- Main Execution ---
if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "WokwiEmailAlertClient")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # Start the non-blocking loop to handle incoming MQTT messages
        print(f"Listening for alerts on {MQTT_BROKER}...")
        client.loop_forever() 
    except Exception as e:
        print(f"An error occurred during MQTT connection: {e}")