from math import pi

def compactness(area_m2:float,perimeter_m:float)->float:
    if perimeter_m<=0: return 0.0
    return float((4.0*pi*area_m2)/(perimeter_m**2))
