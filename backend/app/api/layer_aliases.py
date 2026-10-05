from fastapi import APIRouter
router=APIRouter(prefix="/api/v1/layers",tags=["layers"])
@router.get("/aliases")
def aliases(): return {"buildings":"building","roads":"road","water":"water","vegetation":"vegetation","parcels":"parcel"}
