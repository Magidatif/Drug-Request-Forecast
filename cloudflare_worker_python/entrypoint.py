# Cloudflare Workers Python Entrypoint
# MediDemand Application - MAG Healthcare Solutions
from js import Response, Headers, JSON
import json
from datetime import datetime

# Read the synchronized HTML template
with open("index.html", "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()

def calculate_forecast(avg_monthly: float, current_stock: float = 0.0, lead_days: float = 45.0, safety_buffer_pct: float = 10.0) -> int:
    daily_demand = avg_monthly / 30.0
    raw_demand = daily_demand * lead_days
    safety_stock = raw_demand * (safety_buffer_pct / 100.0)
    total_needed = raw_demand + safety_stock
    net_order = total_needed - current_stock
    return max(0, round(net_order))

async def on_fetch(request, env):
    url = request.url
    method = request.method
    
    headers = Headers.new()
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")

    if method == "OPTIONS":
        return Response.new("", headers=headers, status=204)

    # API Endpoint: /api/forecast
    if "/api/forecast" in url:
        if method == "POST":
            try:
                body_text = await request.text()
                payload = json.loads(body_text) if body_text else {}
                
                avg_monthly = float(payload.get("avg_monthly_consumption") or payload.get("avgMonthlyConsumption", 0))
                current_stock = float(payload.get("current_stock") or payload.get("currentStock", 0))
                
                if "lead_days" in payload:
                    lead_days = float(payload["lead_days"])
                elif "leadDays" in payload:
                    lead_days = float(payload["leadDays"])
                elif "lead_time_months" in payload:
                    lead_days = float(payload["lead_time_months"]) * 30.0
                elif "leadMonths" in payload:
                    lead_days = float(payload["leadMonths"]) * 30.0
                else:
                    lead_days = 45.0

                safety_buffer = float(payload.get("safety_buffer_percent") or payload.get("safetyBuffer", 10))

                rec_qty = calculate_forecast(avg_monthly, current_stock, lead_days, safety_buffer)

                response_data = {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "facility": payload.get("facility_name") or payload.get("facilityName"),
                    "drug": payload.get("drug_name") or payload.get("drugName"),
                    "recommended_qty": rec_qty,
                    "recommendedQty": rec_qty
                }
                
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(response_data), headers=headers, status=200)
            except Exception as e:
                err_response = {"status": "error", "message": str(e)}
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(err_response), headers=headers, status=400)
        
        headers.set("Content-Type", "application/json")
        return Response.new(json.dumps({"message": "MediDemand Python API Ready"}), headers=headers, status=200)

    # Serve Main Frontend HTML
    headers.set("Content-Type", "text/html; charset=utf-8")
    return Response.new(HTML_CONTENT, headers=headers, status=200)
