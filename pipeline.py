import time
import threading
import requests
from scapy.all import sniff, TCP, IP
import numpy as np
from scapy.utils import wrpcap
from featureExt.FEmodule import extract_features, align_to_model
import pandas as pd
import xgboostModule as xgbm

# ==== GLOBAL BUFFER ====
packet_buffer = []
buffer_lock = threading.Lock()

# ==== CONFIG ====
BATCH_INTERVAL = 10  # seconds
PORT = 1883
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/ids-alert"

# ==== FEATURE EXTRACTOR ====
def process(packets):
    temp_file = "temp.pcapng"
    wrpcap(temp_file, packets)
    pre_aligned_df = extract_features(temp_file)
    aligned_df = align_to_model(pre_aligned_df)
    return aligned_df

# ==== MODEL ====
model = xgbm.load_model("binaryClassParams.pkl")

# ==== ALERT SENDER ====
def send_alert(attack_count, total_packets):
    try:
        payload = {
            "attack_count": int(attack_count),
            "total_packets": int(total_packets),
            "attack_rate": round(attack_count / total_packets * 100, 1),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "severity": "HIGH" if attack_count > 100 else "MEDIUM"
        }
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        print(f"[ALERT] Sent to n8n → status {response.status_code}")
    except Exception as e:
        print(f"[ALERT] Failed to send to n8n: {e}")

# ==== PACKET HANDLER ====
def packet_callback(pkt):
    if pkt.haslayer(TCP):
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        if sport == PORT or dport == PORT:
            with buffer_lock:
                packet_buffer.append(pkt)

# ==== SNIFFER THREAD ====
def start_sniffing():
    print("[SNIFFER] Starting packet capture on port 1883...")
    sniff(
        iface="\\Device\\NPF_Loopback",
        filter=f"tcp port {PORT}",
        prn=packet_callback,
        store=False
    )

# ==== BATCH PROCESSOR ====
def batch_processor():
    print("[PROCESSOR] Batch processor started (10s window)...")
    while True:
        time.sleep(BATCH_INTERVAL)
        with buffer_lock:
            if not packet_buffer:
                print("[PROCESSOR] No packets in this batch.")
                continue
            batch = packet_buffer.copy()
            packet_buffer.clear()

        print(f"[+] Processing batch of {len(batch)} packets")

        X = process(batch)
        if len(X) == 0:
            print("[PROCESSOR] No features extracted.")
            continue

        preds = model.predict(X)
        attack_count = (preds == 1).sum()
        total = len(preds)

        if attack_count > 0:
            print(f"[+] Attack count: \033[91m{attack_count}\033[0m / {total} ⚠️ SENDING ALERT...")
            send_alert(attack_count, total)
        else:
            print(f"[+] Attack count: \033[92m0\033[0m / {total} ✅ Normal")

# ==== MAIN ====
if __name__ == "__main__":
    print("[SYSTEM] IDS Pipeline starting...")
    t1 = threading.Thread(target=start_sniffing, daemon=True)
    t2 = threading.Thread(target=batch_processor, daemon=True)
    t1.start()
    print("[SYSTEM] Sniffer thread started")
    t2.start()
    print("[SYSTEM] Batch processor thread started")
    print("[SYSTEM] Running... press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopping IDS...")