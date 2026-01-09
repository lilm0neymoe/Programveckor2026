from __future__ import annotations

from typing import List, Tuple, Union

from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

#hjälper med att input blir riktiga mattefunktioner
TRANSFORMATIONS = standard_transformations + (
  implicit_multiplication_application,
  convert_xor
)

class SolveRequests(BaseModel):
  input: str = Field(...)
  variable: str = Field("x")
  mode: str = Field("solve")

class Step(BaseModel):
  step_number: int
  before: str
  after: str
  operation: str
  reason: str

class SolveResponse(BaseModel):
  original_input: str
  mode: str
  steps: List[Step]
  final_answer: str

app = FastAPI(title="Local Algebra Solver", version="0.1.0")

app.mount("/static", StaticFiles(directory=".", html=False), name="static")

@app.get("/script.js")
async def get_script() -> FileResponse:
  return FileResponse("script.js", media_type="application/javascript")

@app.get("/", response_class=HTMLResponse)
async def get_index() -> str:
    
  with open("index.html", "r", encoding="utf-8") as f:
    return f.read()


#från documentation, tar en sympy ekvation och gör den bättre visbar i webbläsare
#standerdizes att "vänster = höger"
def latex_equation(eq: sp.Equality) -> str:
  return f"{sp.latex(eq.lhs)} = {sp.latex(eq.rhs)}"
#Samma sak men med en expression istället för ekvation
def latex_expr(expr: sp.Expr) -> str:
  return sp.latex(expr)

# Returnerar antingen en ekvation eller ett uttryck + en sträng som beskriver typen
def parse_input(
    user_input: str, 
    variable: str, 
    mode: str
) -> Tuple[Union[sp.Equality, sp.Expr], str]: 
    
    try: #för att tolka använderens input så tar den in vad användaren skrev
        cleaned = user_input.replace("\u00a0", " ") #rensar mellanslag
        if "=" in cleaned: #kollar om det är ekv eller inte
            parts = cleaned.split("=") #delar i två delar
            if len(parts) != 2:
                raise ValueError("Endast ett likehetstecken får användas")
            #här tolkas båda sidorna med sympy
            left_str, right_str = parts
            left_expr = parse_expr(left_str, transformations=TRANSFORMATIONS)
            right_expr = parse_expr(right_str, transformations=TRANSFORMATIONS)
            return sp.Eq(left_expr, right_expr), "equation"
        
        expr = parse_expr(cleaned, transformations=TRANSFORMATIONS)
        if mode == "solve":
            return sp.Eq(expr, 0), "equation"
        return expr, "expression"
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Kan inte parse input: {exc}")
    
    #funktionen ska omvandla input från använderen till matte som programmet kan sedan hantera
    #tar bort onödiga delar och ser till att programmet vet hur man hanterar

def classify_equation(eq: sp.Equality, var: sp.Symbol) -> str: #tar emot sympy ekvationen, och variablen (t.ex x)

    expr = sp.simplify(eq.lhs - eq.rhs) #flyttar till vänsterled
    poly = sp.Poly(expr, var) #tolkar som en polynom
    try:
        deg = poly.degree()
    except Exception:
        return "generic"
    if deg == 1:
        return "linear"
    if deg == 2:
        return "quadratic"
    return "generic"
#kollar graderna för att se vilken sorts ekv det är för att sedan hanteras

def verify_equivalence(
    eq_before: sp.Equality, eq_after: sp.Equality, var: sp.Symbol #före vs efter
) -> bool:
    
    try:
        sol_before = sp.solveset(eq_before, var, domain=sp.S.Complexes)
        sol_after = sp.solveset(eq_after, var, domain=sp.S.Complexes)
         #complexes används som ett verktyg att man inte missar något
        if isinstance(sol_before, sp.ConditionSet) or isinstance(
            sol_after, sp.ConditionSet
        ):
        #om den kan inte hitta uttrycket exakt
            return True
        return sol_before == sol_after
    except Exception:
        return True
#kollar att alla steg har samma lösning, från doc


#här skriv def linear_solver_steps, def quadratic_solver_steps och def simplify_expression
