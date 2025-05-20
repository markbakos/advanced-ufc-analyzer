from fastapi import APIRouter
from prediction.predict_fight import UFCPredictor
from pydantic import BaseModel

class FightPredictionRequest(BaseModel):
    fighter1: str
    fighter2: str

router = APIRouter()

@router.get("/")
async def root():
    """Health Check"""
    return {"status": "OK", "message": "Predict API"}

@router.get("/fight")
async def predict(fighters: FightPredictionRequest):
    """Predict match outcome between 2 fighters"""
    predictor = UFCPredictor(fighter1=fighters.fighter1, fighter2=fighters.fighter2)
    prediction = predictor.main()

    return {
        "winner": prediction["result"]["winner"],
        "result_probability": str(prediction["result"]["probability"]),
        "win_method": prediction['win_method']['method'],
        "method_probability": str(prediction['win_method']['probability']),
    }

