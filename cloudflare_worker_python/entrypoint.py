# Cloudflare Workers Python Entrypoint
# MediDemand Application - MAG Healthcare Solutions
from js import Response, Headers
import json
from datetime import datetime

with open("index.html", "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()

def calculate_forecast(m1: float, m2: float, m3: float, lead_days: float, safety_days: float, current_stock: float):
    avg_monthly = (m1 + m2 + m3) / 3.0
    daily_demand = avg_monthly / 30.0
    total_days = lead_days + safety_days
    total_needed = daily_demand * total_days
    net_order = total_needed - current_stock
    return max(0, round(net_order)), round(avg_monthly, 2), round(daily_demand, 2), total_days

async def on_fetch(request, env):
    url = request.url
    method = request.method
    
    headers = Headers.new()
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")

    if method == "OPTIONS":
        return Response.new("", headers=headers, status=204)

    if "/api/forecast" in url:
        if method == "POST":
            try:
                body_text = await request.text()
                payload = json.loads(body_text) if body_text else {}
                
                m1 = float(payload.get("m1_consumption") or payload.get("m1") or 0)
                m2 = float(payload.get("m2_consumption") or payload.get("m2") or 0)
                m3 = float(payload.get("m3_consumption") or payload.get("m3") or 0)
                lead_days = float(payload.get("lead_days") or payload.get("leadDays") or 30)
                safety_days = float(payload.get("safety_days") or payload.get("safetyDays") or 15)
                current_stock = float(payload.get("current_stock") or payload.get("currentStock") or 0)

                rec_qty, avg_monthly, daily_demand, total_days = calculate_forecast(m1, m2, m3, lead_days, safety_days, current_stock)

                response_data = {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "facility": payload.get("facility_name") or payload.get("facilityName"),
                    "drug": payload.get("drug_name") or payload.get("drugName"),
                    "recommended_qty": rec_qty,
                    "avg_monthly": avg_monthly,
                    "daily_demand": daily_demand,
                    "total_days": total_days
                }
                
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(response_data), headers=headers, status=200)
            except Exception as e:
                err_response = {"status": "error", "message": str(e)}
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(err_response), headers=headers, status=400)
        
        headers.set("Content-Type", "application/json")
        return Response.new(json.dumps({"message": "MediDemand Python API Ready"}), headers=headers, status=200)

    headers.set("Content-Type", "text/html; charset=utf-8")
    return Response.new(HTML_CONTENT, headers=headers, status=200)
