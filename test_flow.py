import urllib.request
import urllib.parse
import json

def test_flow():
    # 1. Create startup
    data = json.dumps({"name": "Test", "idea": "Test idea"}).encode('utf-8')
    req = urllib.request.Request("http://localhost:8000/api/startups", data=data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    startup = json.loads(res.read())['startup']
    print("Created startup:", startup['id'])

    # 2. Get Analysis (should be missing)
    try:
        urllib.request.urlopen(f"http://localhost:8000/api/startups/{startup['id']}/analysis")
    except Exception as e:
        print("Analysis not found (expected):", e)

    # 3. Generate Dashboard
    data2 = json.dumps({"id": startup['id'], "idea": "Test idea"}).encode('utf-8')
    req2 = urllib.request.Request("http://localhost:8000/api/generate-dashboard", data=data2, headers={'Content-Type': 'application/json'})
    try:
        res2 = urllib.request.urlopen(req2)
        print("Generate dashboard success!")
    except Exception as e:
        print("Generate dashboard error:", e.read() if hasattr(e, 'read') else e)

test_flow()
