import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.models import HistoryItem
from backend.database import get_db
from backend.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[HistoryItem])
def get_user_history(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, risk, risk_level, details, timestamp FROM history WHERE username = ? ORDER BY id DESC",
            (username,)
        )
        rows = cursor.fetchall()
        
    results = []
    for r in rows:
        details_val = None
        if r["details"]:
            try:
                details_val = json.loads(r["details"])
            except Exception:
                details_val = {}
                
        results.append({
            "id": r["id"],
            "username": r["username"],
            "risk": r["risk"],
            "risk_level": r["risk_level"] or ("Low" if r["risk"] <= 30 else ("Moderate" if r["risk"] <= 50 else "High")),
            "timestamp": r["timestamp"],
            "details": details_val
        })
    return results

@router.delete("/{item_id}")
def delete_history_item(item_id: int, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM history WHERE id = ? AND username = ?", (item_id, username))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="History record not found")
        cursor.execute("DELETE FROM history WHERE id = ? AND username = ?", (item_id, username))
    return {"message": "Record deleted successfully", "id": item_id}

@router.delete("")
def clear_all_history(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE username = ?", (username,))
    return {"message": "All prediction history cleared successfully"}
