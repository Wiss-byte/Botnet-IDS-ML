import requests

requests.post('http://localhost:5678/webhook/ids-alert', json={
    'attack_count': 927,
    'total_packets': 1041,
    'attack_rate': 89.0,
    'timestamp': '2026-05-07 12:56:00',
    'severity': 'HIGH'
})
print('Sent!')