from __future__ import annotations

from typing import List, Tuple, Union

from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import os
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

app = FastAPI(title="Algebra Solver", version="0.1.0")

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static", html=False), name="static")

@app.get("/script.js")
def script():
    return FileResponse("script.js", media_type="application/javascript")

@app.get("/index.css")
def css():
    return FileResponse("index.css", media_type="text/css")

#tar en sympy ekvation och gör den bättre visbar i webbläsare, LaText hjälpare


LATEX_KW = {
    "mul_symbol": r"\cdot ",   # gör multiplikation tydlig: 210·y istället för 210 y
    # du kan lägga fler senare om du vill
}

def latex_expr(expr: sp.Expr) -> str:
    return sp.latex(expr, **LATEX_KW)

def latex_equation(eq: sp.Equality) -> str:
    return f"{latex_expr(eq.lhs)} = {latex_expr(eq.rhs)}"

def latex_aligned_lines(lines: List[str]) -> str:
    
    #Tar en lista av LaTeX-rader och gör dem till ett aligned-block som KaTeX renderar snyggt.
    #Varje rad ska redan vara latex (utan $).

    body = r" \\ ".join(lines)
    return r"\begin{aligned}" + body + r"\end{aligned}"

def latex_two_solutions(var: sp.Symbol, s1: sp.Expr, s2: sp.Expr) -> str:
    v = latex_expr(var)
    l1 = latex_expr(sp.simplify(s1))
    l2 = latex_expr(sp.simplify(s2))
    return latex_aligned_lines([rf"{v}_1 &= {l1}", rf"{v}_2 &= {l2}"])
#returnerar antingen en ekvation eller ett uttryck + en sträng som beskriver typen
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


#här skriv def linear_solver_steps, def quadratic_solver_step och def simplify_expression


#Löser linjera ekv steg för steg
#Först utökar den och förenklar
#Sedan Flyytar den allt till vänster
#Förenklar uttrycket
#Isolerar variabeln
#Löser
def linear_solver_steps(eq: sp.Equality, var: sp.Symbol) -> Tuple[List[Step], sp.Equality]:
  steps: List[Step] = [] 
  step_idx = 1
  current_eq = eq

  lhs_simp = sp.simplify(sp.expand(current_eq.lhs))
  rhs_simp = sp.simplify(sp.expand(current_eq.rhs))
  new_eq = sp.Eq(lhs_simp, rhs_simp)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
    steps.append(
        Step(
           step_number=step_idx,
           before=latex_equation(current_eq),
           after=latex_equation(new_eq),
           operation="Utöka och förenkla båda sidor",
           reason="Kombinera lika termer på varje sida",
        )
    ) 

    step_idx += 1
    current_eq = new_eq

  new_eq = sp.Eq(current_eq.lhs - current_eq.rhs, 0)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
    steps.append(
       Step(
           step_number=step_idx,
           before=latex_equation(current_eq),
           after=latex_equation(new_eq),
           operation="Subtrahera höger sida från båda sidor",
           reason="Standardisera ekvationen till = 0",
       )
    )

    step_idx += 1
    current_eq = new_eq

  lhs_simp = sp.simplify(current_eq.lhs)
  new_eq = sp.Eq(lhs_simp, 0)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
    steps.append(
     Step(
          step_number=step_idx,
          before=latex_equation(current_eq),
          after=latex_equation(new_eq),
          operation="Kombinera lika termer",
          reason="Förenkla uttrycket på vänstra sidan",
      )
    )

    step_idx += 1
    current_eq = new_eq

  
  expr = sp.expand(current_eq.lhs)
  coef = expr.coeff(var)
  const = expr.subs(var, 0)

  new_eq = sp.Eq(coef * var, -const)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
    steps.append(
        Step(
           step_number=step_idx,
           before=latex_equation(current_eq),
           after=latex_equation(new_eq),
           operation="Isolera variabelterme",
           reason="Flytta konstanterna till andra sidan"
        )
     )
    step_idx += 1
    current_eq = new_eq

  if coef != 0:
    solution = sp.simplify(-const / coef)
    new_eq = sp.Eq(var, solution)
    if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
      steps.append(
          Step(
             step_number=step_idx,
             before=latex_equation(current_eq),
             after=latex_equation(new_eq),
             operation="Dela båda sidor med koefficienten",
             reason="Lös för variabeln"

          )
       )
      current_eq = new_eq
  return steps, current_eq

#Löser genom förenkling, faktoresering om det går, annars pq formeln
def quadratic_solver_step (
    eq: sp.Equality, var: sp.Symbol
) -> Tuple[List[Step], str]:
   
  steps: List[Step] = []
  step_idx = 1
  current_eq = eq

  lhs_simp = sp.simplify(sp.expand(current_eq.lhs))
  rhs_simp = sp.simplify(sp.expand(current_eq.rhs))
  new_eq = sp.Eq(lhs_simp, rhs_simp)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
      steps.append(
         Step(
          step_number=step_idx,
          before=latex_equation(current_eq),
          after=latex_equation(new_eq),
          operation="Utöka och förenkla båda sidor",
          reason="Kombinera lika termer på varje sida"
         )
      )
      step_idx += 1
      current_eq = new_eq

  new_eq = sp.Eq(current_eq.lhs - current_eq.rhs, 0)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
     steps.append(
          Step(
             step_number=step_idx,
             before=latex_equation(current_eq),
             after=latex_equation(new_eq),
             operation="Subtrahera höger sida från båda sidor",
             reason="Standardisera ekvationen till = 0",
            )
      )
     step_idx += 1
     current_eq = new_eq
  expr_simp = sp.simplify(sp.expand(current_eq.lhs))
  new_eq = sp.Eq(expr_simp, 0)
  if new_eq != current_eq and verify_equivalence(current_eq, new_eq, var):
      steps.append(
          Step(
              step_number=step_idx,
              before=latex_equation(current_eq),
              after=latex_equation(new_eq),
              operation="Kombinera lika termer",
              reason="Förenkla andragradsekvationen",
            )
      )
      step_idx += 1
      current_eq = new_eq

  poly = sp.Poly(current_eq.lhs, var)
  coeffs = poly.all_coeffs()
  while len(coeffs) < 3:
      coeffs.append(0)
  a, b, c = coeffs[0], coeffs[1], coeffs[2]
    
  factor_expr = sp.factor(poly.as_expr())
  factor_data = sp.factor_list(poly.as_expr())
  linear_factors = [
      (base, exp)
      for base, exp in factor_data[1]
      if sp.Poly(base, var).degree() == 1
    ]
  if linear_factors:
      factored_eq = sp.Eq(factor_expr, 0)
      if verify_equivalence(current_eq, factored_eq, var):
          steps.append(
              Step(
                  step_number=step_idx,
                  before=latex_equation(current_eq),
                  after=latex_equation(factored_eq),
                  operation="Faktorisera andragradsekvationen",
                    reason="Skriv om andragradsekvationen som en produkt av faktorerna",
                )
            )
          step_idx += 1
          current_eq = factored_eq
      solutions: List[sp.Expr] = []
      for base, exp in factor_data[1]:
          if not base.has(var):
              continue
          sol = sp.solve(sp.Eq(base, 0), var)
          solutions.extend(sol)
      solutions_unique = list(dict.fromkeys([sp.simplify(s) for s in solutions]))
      if len(solutions_unique) == 1:
          sol_latex = latex_aligned_lines([
              rf"{latex_expr(var)} &= {latex_expr(solutions_unique[0])}"
          ])
      else:
          # Visa alla lösningar i flera rader för every scenario
          lines = [rf"{latex_expr(var)}_{i+1} &= {latex_expr(s)}"
                  for i, s in enumerate(solutions_unique)]
          sol_latex = latex_aligned_lines(lines)
      steps.append(
            Step(
                step_number=step_idx,
                before=latex_equation(current_eq),
                after=sol_latex,
                operation="Sätt varje faktor lika med noll och lös",
                reason="Om en produkt är noll måste minst en faktor vara noll, så vi löser varje faktor för sig",
            )
        )
      return steps, sol_latex
    
  discriminant = sp.simplify(b ** 2 - 4 * a * c)
  disc_expr = sp.simplify(discriminant)
  steps.append(
        Step(
            step_number=step_idx,
            before=latex_equation(current_eq),
            after=rf"\Delta = {latex_expr(disc_expr)}",
            operation="Undersök antalet lösningar",
            reason="Uttrycket under rottecknet avgör om ekvationen har två, en eller inga reella lösningar",
        )
    )
  step_idx += 1
  sqrt_disc = sp.sqrt(discriminant)
  sol_plus = sp.simplify((-b + sqrt_disc) / (2 * a))
  sol_minus = sp.simplify((-b - sqrt_disc) / (2 * a))

  if sp.simplify(sol_plus - sol_minus) == 0:
      #En lösning
      final_answer_latex = latex_aligned_lines([
          rf"{latex_expr(var)} &= {latex_expr(sol_plus)}"
      ])
  else:
      #Alla fall (två rötter) bra aligned
      final_answer_latex = latex_two_solutions(var, sol_plus, sol_minus)

  steps.append(
      Step(
          step_number=step_idx,
          before=rf"\Delta = {latex_expr(disc_expr)}",
          after=final_answer_latex,
          operation="Använd pq-formeln",
          reason="Formeln x = (−b ± √Δ) / (2a) används för att lösa andragradsekvationen",
      )
  )
  return steps, final_answer_latex

def simplify_expression(expr: sp.Expr) -> Tuple[List[Step], sp.Expr]:

  steps: List[Step] = []
  step_idx = 1
  original = expr
  expanded = sp.expand(expr)
  simplified = sp.simplify(expanded)
  if simplified != original:
    steps.append(
      Step(
        step_number=step_idx,
        before=latex_expr(original),
        after=latex_expr(simplified),
        operation="Expandera och förenkla",
        reason="Kombinera lika termer och förenkla uttrycket",
            )
        )
  return steps, simplified


@app.post("/solve", response_class=JSONResponse)
async def solve(request: SolveRequests) -> SolveResponse:

  parsed, kind = parse_input(request.input, request.variable, request.mode)

  if kind == "equation":
      symbols = (parsed.lhs - parsed.rhs).free_symbols
  else:
      symbols = parsed.free_symbols
  if request.mode == "simplify" and kind == "expression":
      steps, simplified = simplify_expression(parsed)
      final_answer = latex_expr(simplified)
      return SolveResponse(
          original_input=request.input,
          mode=request.mode,
          steps=steps,
          final_answer=final_answer,
        )
  if len(symbols) == 1:
     var_symbol = next(iter(symbols))
  elif len(symbols) == 0:
     var_symbol = sp.Symbol(request.variable or "x")
  else:
     raise HTTPException(
        status_code=400,
        detail=(
           f"Felra variabler hittades! : {', '.join(sorted(str(s) for s in symbols))}. "
           "Välj en variabel att lösa efter istället, eller testa förenkla funktionen"
        )
     )
  if kind != "equation":
     raise HTTPException(status_code=400, detail="Ingen ekvation finns")
  
  classification = classify_equation(parsed, var_symbol)
  if classification == "linear":
    steps, final_eq = linear_solver_steps(parsed, var_symbol)
    final_answer = latex_equation(final_eq)
  elif classification == "quadratic":
    steps, final_answer = quadratic_solver_step(parsed, var_symbol)
  else:
    sol = sp.solve(parsed, var_symbol)
    steps = []
    if len(sol) == 0:
      final_answer = f"{sp.latex(var_symbol)} \\in \\emptyset"
    elif len(sol) == 1:
      final_answer = f"{sp.latex(var_symbol)} = {sp.latex(sol[0])}"
    else:
      sol_latex = ", ".join(sp.latex(s) for s in sol)
      final_answer = f"{sp.latex(var_symbol)} \\in \\{{{sol_latex}\\}}"


  return SolveResponse(
    original_input=request.input,
    mode=request.mode,
    steps=steps,
    final_answer=final_answer,
    )

app.mount("/", StaticFiles(directory=".", html=True), name="site")