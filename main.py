# Projet Sentinel - Étape 17 : API Web (FastAPI)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import json
import datetime
import uuid

app = FastAPI(title="Agent Sentinel API", version="v1.0")

# --- MODÈLES DE DONNÉES (Pydantic) ---
class Transaction(BaseModel):
    date: str
    label: str
    amount: float

class AnalysisRequest(BaseModel):
    user_id: str
    transactions: list[Transaction]

class ApiResponse(BaseModel):
    status: str
    message: str
    data: dict
    signature: str

# --- LOGIQUE MÉTIER (Ton cerveau IA) ---
def detect_subscriptions(transactions: list[Transaction]):
    mots_cles = ["NETFLIX", "FITNESS", "GYM", "SPOTIFY", "PREMIUM", "SUBSCRIPTION"]
    detected = []
    total_loss = 0
    
    for t in transactions:
        if any(k in t.label.upper() for k in mots_cles):
            detected.append(t)
            total_loss += abs(t.amount)
            
    return detected, total_loss

def generate_report(user_id: str, transactions: list[Transaction]):
    subs, monthly_loss = detect_subscriptions(transactions)
    
    if not subs:
        return {
            "summary": "Aucun abonnement détecté.",
            "savings_potential": 0,
            "details": []
        }

    annual_gain = monthly_loss * 12
    commission = monthly_loss * 0.15 # Ta part
    
    report_data = {
        "user_id": user_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "analysis_summary": {
            "total_scanned_lines": len(transactions),
            "subscriptions_detected": len(subs),
            "monthly_loss_identified": round(monthly_loss, 2),
            "yearly_loss_projected": round(annual_gain, 2)
        },
        "financial_action": {
            "service_fee_rate": 0.15,
            "client_savings_net_monthly": round(monthly_loss - commission, 2),
            "platform_revenue_gross": round(commission, 2)
        },
        "detected_items_anonymized": [
            {
                "ref_hash": hashlib.md5((t.label + user_id).encode()).hexdigest()[:8],
                "amount_monthly": abs(t.amount),
                "category_code": "REC_SUB_STREAMING" if "NETFLIX" in t.label or "SPOTIFY" in t.label else "REC_SUB_FITNESS"
            }
            for t in subs
        ]
    }
    
    # Signature de sécurité
    raw_string = json.dumps(report_data, sort_keys=True) + "SENTINEL_SECRET_2026"
    signature = hashlib.sha256(raw_string.encode()).hexdigest()
    
    return {"report": report_data, "signature": signature}

# --- ENDPOINTS API ---

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Agent Sentinel. Utilisez /analyze pour traiter vos données."}

@app.post("/analyze", response_model=dict)
async def analyze_financials(request: AnalysisRequest):
    """
    Endpoint principal : Reçoit les transactions, renvoie le rapport sécurisé.
    """
    try:
        result = generate_report(request.user_id, request.transactions)
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
             
        return {
            "status": "success",
            "message": "Analyse terminée avec succès.",
            "data": result["report"],
            "signature": result["signature"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)