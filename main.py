#  HUR MAN KÖR PROJEKTET 
# 1. Skapa och aktivera virtuell miljö:
#    Windows:
#      py -m venv .venv
#      .\.venv\Scripts\activate
#
# 2. Installera beroenden:
#    pip install fastapi uvicorn sympy pydantic
#
# 3. Kör servern (om filen heter main.py):
#    uvicorn main:app --reload
#
# 4. Öppna i webbläsaren:
#    http://127.0.0.1:8000/
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

TEXT = {
  "sv": {
    "parse_error": "Kan inte parse input: {err}",
    "only_one_equals": "Endast ett likhetstecken får användas",
    "multi_vars": "Flera variabler hittades!: {vars}. Välj en variabel att lösa efter istället, eller testa förenkla funktionen",
    "no_equation": "Ingen ekvation finns",

    "op_expand_simplify": "Utöka och förenkla båda sidor",
    "rsn_expand_simplify": "Kombinera lika termer på varje sida",
    "op_sub_rhs": "Subtrahera höger sida från båda sidor",
    "rsn_standardize": "Standardisera ekvationen till = 0",
    "op_combine_terms": "Kombinera lika termer",
    "rsn_simplify_lhs": "Förenkla uttrycket på vänstra sidan",
    "op_isolate_var_term": "Isolera variabelterm",
    "rsn_move_constants": "Flytta konstanterna till andra sidan",
    "op_divide_coeff": "Dela båda sidor med koefficienten",
    "rsn_solve_var": "Lös för variabeln",

    "op_factor": "Faktorisera andragradsekvationen",
    "rsn_factor": "Skriv om andragradsekvationen som en produkt av faktorerna",
    "op_zero_product": "Sätt varje faktor lika med noll och lös",
    "rsn_zero_product": "Om en produkt är noll måste minst en faktor vara noll, så vi löser varje faktor för sig",
    "op_discriminant": "Undersök antalet lösningar",
    "rsn_discriminant": "Uttrycket under rottecknet avgör om ekvationen har två, en eller inga reella lösningar",
    "op_pq": "Använd pq-formeln",
    "rsn_pq": "Formeln x = (−b ± √Δ) / (2a) används för att lösa andragradsekvationen",

    "op_expand_simplify_expr": "Expandera och förenkla",
    "rsn_expand_simplify_expr": "Kombinera lika termer och förenkla uttrycket",
  },

  "en": {
    "parse_error": "Could not parse input: {err}",
    "only_one_equals": "Only one equals sign is allowed",
    "multi_vars": "Multiple variables found: {vars}. Choose one variable to solve for, or try simplify mode.",
    "no_equation": "No equation was provided",

    "op_expand_simplify": "Expand and simplify both sides",
    "rsn_expand_simplify": "Combine like terms on each side",
    "op_sub_rhs": "Subtract the right side from both sides",
    "rsn_standardize": "Standardize the equation to = 0",
    "op_combine_terms": "Combine like terms",
    "rsn_simplify_lhs": "Simplify the left-hand side",
    "op_isolate_var_term": "Isolate the variable term",
    "rsn_move_constants": "Move constants to the other side",
    "op_divide_coeff": "Divide both sides by the coefficient",
    "rsn_solve_var": "Solve for the variable",

    "op_factor": "Factor the quadratic",
    "rsn_factor": "Rewrite the quadratic as a product of factors",
    "op_zero_product": "Set each factor to zero and solve",
    "rsn_zero_product": "If a product is zero, at least one factor must be zero",
    "op_discriminant": "Check the number of solutions",
    "rsn_discriminant": "The discriminant determines whether there are two, one, or no real solutions",
    "op_pq": "Use the quadratic formula",
    "rsn_pq": "x = (−b ± √Δ) / (2a) solves a quadratic equation",

    "op_expand_simplify_expr": "Expand and simplify",
    "rsn_expand_simplify_expr": "Combine like terms and simplify the expression",
  },
    "zh": {
    "parse_error": "无法解析输入：{err}",
    "only_one_equals": "只能使用一个等号",
    "multi_vars": "检测到多个变量：{vars}。请选择一个变量进行求解，或尝试化简模式。",
    "no_equation": "未提供方程",

    "op_expand_simplify": "展开并简化两边",
    "rsn_expand_simplify": "合并每一边的同类项",
    "op_sub_rhs": "两边同时减去右边",
    "rsn_standardize": "将方程标准化为 = 0",
    "op_combine_terms": "合并同类项",
    "rsn_simplify_lhs": "化简左边的表达式",
    "op_isolate_var_term": "隔离变量项",
    "rsn_move_constants": "将常数移到另一边",
    "op_divide_coeff": "两边同时除以系数",
    "rsn_solve_var": "求解变量",

    "op_factor": "对二次方程进行因式分解",
    "rsn_factor": "将二次方程改写为因式乘积",
    "op_zero_product": "令每个因式等于零并求解",
    "rsn_zero_product": "若乘积为零，则至少有一个因式为零",
    "op_discriminant": "判断解的个数",
    "rsn_discriminant": "根号下的判别式决定方程有两个、一个或没有实数解",
    "op_pq": "使用二次公式",
    "rsn_pq": "公式 x = (−b ± √Δ) / (2a) 用于求解二次方程",

    "op_expand_simplify_expr": "展开并化简",
    "rsn_expand_simplify_expr": "合并同类项并化简表达式"
  },

  "yue": {
    "parse_error": "無法解析輸入：{err}",
    "only_one_equals": "只可以使用一個等號",
    "multi_vars": "偵測到多個變量：{vars}。請揀一個變量嚟解，或者試下化簡模式。",
    "no_equation": "未提供方程",

    "op_expand_simplify": "展開並化簡兩邊",
    "rsn_expand_simplify": "合併每一邊嘅同類項",
    "op_sub_rhs": "兩邊同時減去右邊",
    "rsn_standardize": "將方程標準化為 = 0",
    "op_combine_terms": "合併同類項",
    "rsn_simplify_lhs": "化簡左邊嘅表達式",
    "op_isolate_var_term": "分離變量項",
    "rsn_move_constants": "將常數移到另一邊",
    "op_divide_coeff": "兩邊同時除以係數",
    "rsn_solve_var": "解變量",

    "op_factor": "因式分解二次方程",
    "rsn_factor": "將二次方程改寫成因式嘅乘積",
    "op_zero_product": "令每個因式等於零並求解",
    "rsn_zero_product": "如果乘積等於零，最少有一個因式係零",
    "op_discriminant": "判斷解嘅數量",
    "rsn_discriminant": "根號入面嘅判別式決定方程有兩個、一個或者冇實數解",
    "op_pq": "使用二次公式",
    "rsn_pq": "公式 x = (−b ± √Δ) / (2a) 用嚟解二次方程",

    "op_expand_simplify_expr": "展開並化簡",
    "rsn_expand_simplify_expr": "合併同類項並化簡表達式"
  }
}

def t(lang: str, key: str, **kwargs) -> str:
  table = TEXT.get(lang, TEXT["sv"])
  template = table.get(key, TEXT["sv"].get(key, key))
  try:
    return template.format(**kwargs)
  except Exception:
    return template


class SolveRequests(BaseModel):
  input: str = Field(...)
  variable: str = Field("x")
  mode: str = Field("solve")
  lang: str = Field("sv")

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
def parse_input(user_input: str, variable: str, mode: str, lang: str) -> Tuple[Union[sp.Equality, sp.Expr], str]:
    
    try: #för att tolka använderens input så tar den in vad användaren skrev
        cleaned = user_input.replace("\u00a0", " ") #rensar mellanslag
        if "=" in cleaned: #kollar om det är ekv eller inte
            parts = cleaned.split("=") #delar i två delar
            if len(parts) != 2:
                raise ValueError(t(lang, "only_one_equals"))
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
        raise HTTPException(status_code=400, detail=t(lang, "parse_error", err=str(exc)))
    
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
def linear_solver_steps(eq: sp.Equality, var: sp.Symbol, lang: str) -> Tuple[List[Step], sp.Equality]:
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
           operation=t(lang, "op_expand_simplify"),
           reason=t(lang, "rsn_expand_simplify"),
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
           operation=t(lang, "op_sub_rhs"),
           reason=t(lang, "rsn_standardize"),
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
          operation=t(lang, "op_combine_terms"),
          reason=t(lang, "rsn_simplify_lhs"),
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
           operation=t(lang, "op_isolate_var_term"),
           reason=t(lang, "rsn_move_constants")
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
             operation=t(lang, "op_divide_coeff"),
             reason=t(lang, "rsn_solve_var")

          )
       )
      current_eq = new_eq
  return steps, current_eq

#Löser genom förenkling, faktoresering om det går, annars pq formeln
def quadratic_solver_step(eq: sp.Equality, var: sp.Symbol, lang: str) -> Tuple[List[Step], str]:   
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
          operation=t(lang, "op_expand_simplify"),
          reason=t(lang, "rsn_expand_simplify")
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
             operation=t(lang, "op_sub_rhs"),
             reason=t(lang, "rsn_standardize")
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
              operation=t(lang, "op_combine_terms"),
              reason=t(lang, "rsn_simplify_lhs"),
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
                  operation=t(lang, "op_factor"),
                  reason=t(lang, "rsn_factor"),
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
                operation=t(lang, "op_zero_product"),
                reason=t(lang, "rsn_zero_product"),
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
            operation=t(lang, "op_discriminant"),
            reason=t(lang, "rsn_discriminant"),
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
          operation=t(lang, "op_pq"),
          reason=t(lang, "rsn_pq"),
      )
  )
  return steps, final_answer_latex

def simplify_expression(expr: sp.Expr, lang: str) -> Tuple[List[Step], sp.Expr]:
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
        operation=t(lang, "op_expand_simplify_expr"),
        reason=t(lang, "rsn_expand_simplify_expr"),
            )
        )
  return steps, simplified


@app.post("/solve", response_class=JSONResponse)
async def solve(request: SolveRequests) -> SolveResponse:
  lang = request.lang
  parsed, kind = parse_input(request.input, request.variable, request.mode, lang)

  if kind == "equation":
      symbols = (parsed.lhs - parsed.rhs).free_symbols
  else:
      symbols = parsed.free_symbols
  if request.mode == "simplify" and kind == "expression":
      steps, simplified = simplify_expression(parsed, lang)
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
      detail=t(lang, "multi_vars", vars=", ".join(sorted(str(s) for s in symbols)))
    )

  if kind != "equation":
    raise HTTPException(status_code=400, detail=t(lang, "no_equation"))
  
  classification = classify_equation(parsed, var_symbol)
  if classification == "linear":
    steps, final_eq = linear_solver_steps(parsed, var_symbol, lang)
    final_answer = latex_equation(final_eq)
  elif classification == "quadratic":
    steps, final_answer = quadratic_solver_step(parsed, var_symbol, lang)
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