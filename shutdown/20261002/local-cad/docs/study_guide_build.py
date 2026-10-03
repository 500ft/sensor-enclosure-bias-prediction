# -*- coding: utf-8 -*-
"""Learning guide PDF for the sensor-enclosure-thermal-design project."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether)

NAVY = colors.HexColor("#14304F")
BLUE = colors.HexColor("#1F4E79")
ACC  = colors.HexColor("#B4541A")
GREY = colors.HexColor("#5A6472")
LGREY= colors.HexColor("#EEF1F5")
BORD = colors.HexColor("#C6CFDA")
GREEN= colors.HexColor("#1E6F42")
RED   = colors.HexColor("#A32222")

ss = getSampleStyleSheet()
def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.6, leading=13.6, textColor=colors.black,
                spaceAfter=6, alignment=TA_LEFT)
    base.update(kw); return ParagraphStyle(name, **base)

TITLE  = S("t", fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=6)
SUB    = S("s", fontSize=12, leading=16, textColor=GREY, alignment=TA_CENTER, spaceAfter=18)
H1     = S("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=BLUE, spaceBefore=16, spaceAfter=8)
H2     = S("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=5)
H3     = S("h3", fontName="Helvetica-BoldOblique", fontSize=10.3, leading=14, textColor=ACC, spaceBefore=9, spaceAfter=4)
BODY   = S("b")
SMALL  = S("sm", fontSize=8.5, leading=11.8, textColor=GREY)
BULLET = S("bu", leftIndent=14, firstLineIndent=-9, spaceAfter=3.5)
CODE   = S("c", fontName="Courier", fontSize=8.3, leading=11.2, textColor=colors.HexColor("#10243A"))
EQ     = S("eq", fontName="Courier-Bold", fontSize=9.6, leading=14, textColor=NAVY, alignment=TA_CENTER, spaceBefore=5, spaceAfter=5)
TH     = S("th", fontName="Helvetica-Bold", fontSize=8.6, leading=11, textColor=colors.white)
TD     = S("td", fontSize=8.6, leading=11.4)
TDB    = S("tdb", fontName="Helvetica-Bold", fontSize=8.6, leading=11.4)

def bullet(t): return Paragraph("&bull; " + t, BULLET)

def table(rows, widths, header=True, align=None):
    data=[]
    for ri,row in enumerate(rows):
        out=[]
        for c in row:
            if isinstance(c,Paragraph): out.append(c)
            else: out.append(Paragraph(str(c), TH if (header and ri==0) else TD))
        data.append(out)
    t=Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds=[("GRID",(0,0),(-1,-1),0.5,BORD),("VALIGN",(0,0),(-1,-1),"TOP"),
          ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0),BLUE)]
        for r in range(1,len(data)):
            if r%2==0: cmds.append(("BACKGROUND",(0,r),(-1,r),LGREY))
    return Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT",
                 style=TableStyle(cmds))

def box(title, body_paras, color=ACC, bg=colors.HexColor("#FFF6F0")):
    inner=[Paragraph(title, S("bt", fontName="Helvetica-Bold", fontSize=9.8, leading=13, textColor=color, spaceAfter=4))]
    inner += body_paras
    t=Table([[inner]], colWidths=[6.9*inch], hAlign="LEFT",
            style=TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
                              ("BOX",(0,0),(-1,-1),0.9,color),
                              ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
                              ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t

def code(lines):
    inner=[Paragraph(l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"), CODE) for l in lines]
    return Table([[inner]], colWidths=[6.9*inch], hAlign="LEFT",
                 style=TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F4F6F9")),
                                   ("BOX",(0,0),(-1,-1),0.5,BORD),
                                   ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
                                   ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))

STORY=[]
A=STORY.append

# ============================ COVER ============================
A(Spacer(1, 52))
A(Paragraph("Sensor Enclosure Thermal Design", TITLE))
A(Paragraph("A complete study guide to the project, its physics, its code,<br/>and the mistakes it made and corrected", SUB))
A(Spacer(1, 6))
A(table([["Repository","500ft/sensor-enclosure-thermal-design"],
         ["State at writing","main 7e35e41 &mdash; 132 tests passing, 59/59 source coverage"],
         ["Code","~4,400 lines of analysis; ~2,700 lines of decision documents"],
         ["Model","Steady-state lumped thermal balance, 23 declared assumptions"],
         ["Physical data","<b>None.</b> Every number is simulation or external literature"],
         ["Prepared","27 September 2026"]],
        [1.55*inch, 5.35*inch], header=False))
A(Spacer(1, 18))
A(box("How to read this guide",
  [Paragraph("This is not a summary to skim. It is built so that you can <b>regenerate the project from scratch</b> "
             "&mdash; on a whiteboard, in front of your PI, without notes.", BODY),
   Paragraph("Nearly everything here falls out of <b>one equation</b> (Module 1). The five dimensionless groups, the "
             "Biot gate, the night sign reversal, the shield trade-off: all are consequences of it. Learn that equation "
             "properly and the rest becomes derivation rather than memory.", BODY),
   Paragraph("Each module ends with a <b>cold question</b> &mdash; the thing you must be able to answer with no warning. "
             "Module 4 is the most valuable module in this document and the least obvious: it is the record of three "
             "conclusions this project got wrong, and how each was caught.", BODY)]))
A(PageBreak())

# ============================ MODULE 0 ============================
A(Paragraph("Module 0 &mdash; What this project actually is", H1))
A(Paragraph("The problem in one paragraph", H2))
A(Paragraph("Cities deploy thousands of low-cost air-quality sensors. Each sits inside a small plastic box that keeps rain "
            "off. In sun the box heats up, so the sensor measures warm trapped air rather than real ambient air. Two "
            "consequences follow. The obvious one: temperature and humidity readings are wrong. The one that matters more: "
            "those same readings are the inputs to the correction algorithms that clean up the <b>pollution</b> numbers. "
            "A box that runs warm therefore quietly distorts the air-quality data people actually act on.", BODY))
A(Paragraph("What the project has built", H2))
A(table([["Layer","What exists","Status"],
         ["Thermal model","Lumped steady-state solver, 3 enclosure variants, 23 declared assumptions","Simulation only"],
         ["Dimensional reduction","Five-group closed form plus the exact nonlinear balance","Algebraically verified"],
         ["Sensitivity screen","24-case matched-control comparison","Simulation only"],
         ["Intake pipeline","Fail-closed CSV intake, hash-bound, synthetic end-to-end rehearsal","Tested, no real data"],
         ["Uncertainty engine","Linear covariance propagation, 25 known-answer fixtures","Tested"],
         ["Literature base","59 sources, 57 read in full, 2 recorded as pending","Audited"],
         ["Provenance system","40-quantity register, traceability index","Audited"],
         ["CAD","Parametric V0 enclosure, oracle-checked, STEP exported","Design geometry only"]],
        [1.25*inch, 4.1*inch, 1.55*inch]))
A(Spacer(1,8))
A(box("The single most important sentence in this document",
  [Paragraph("<b>Nothing in this project has been validated against a physical measurement of this enclosure.</b> "
             "The parameter register records exactly three field-measured values, and all three belong to other "
             "people's systems. If you remember one thing when speaking about this work, remember that boundary &mdash; "
             "and say it before someone else asks.", BODY)], color=RED, bg=colors.HexColor("#FFF3F3")))
A(PageBreak())

# ============================ MODULE 1 ============================
A(Paragraph("Module 1 &mdash; The energy balance", H1))
A(Paragraph("Every number this project has ever produced is a root of this equation. In steady state, heat in equals "
            "heat out at the sensor surface:", BODY))
A(Paragraph("alpha &middot; phi &middot; G &middot; A_proj  +  Q_int   =   h &middot; A_conv &middot; (T_s - T_local)  +  eps &middot; sigma &middot; A_conv &middot; [ f (T_s<super>4</super> - T_sky<super>4</super>) + (1-f)(T_s<super>4</super> - T_local<super>4</super>) ]", EQ))
A(Paragraph("Reading the terms", H2))
A(table([["Term","Meaning","Typical scale here"],
         ["alpha &middot; phi &middot; G &middot; A_proj","Absorbed solar. alpha = absorptance, phi = shading fraction, G = irradiance, A_proj = sun-facing area","27 W for the dark box at 1000 W/m<super>2</super>"],
         ["Q_int","Internal electronics dissipation reaching the sensor","0.8 W assumed (never measured)"],
         ["h &middot; A_conv &middot; (T_s - T_local)","Convective loss to local air. h rises with wind","h = 5 + 4U assumed"],
         ["eps sigma A_conv f (T_s<super>4</super>-T_sky<super>4</super>)","Radiation to the cold sky. f = sky-view fraction","The night cooling term"],
         ["eps sigma A_conv (1-f)(T_s<super>4</super>-T_local<super>4</super>)","Radiation to surroundings at local air temperature","Keeps a shield from over-cooling"]],
        [2.0*inch, 3.25*inch, 1.65*inch]))
A(Spacer(1,6))
A(Paragraph("Two subtleties that carry most of the meaning", H2))
A(bullet("<b>T_local is not T_air.</b> For a shielded sensor, solar-warmed plates heat the air flowing past it, so "
         "T_local = T_air + delta. The reported bias is still referenced to <i>true</i> ambient, so that pre-heat shows "
         "up as residual shield error. This is the dominant real-world error of a passive screen at low wind."))
A(bullet("<b>The radiation term is split by f.</b> A fraction f of the surface sees the cold sky; the rest exchanges with "
         "surroundings at local air temperature. By deliberately blocking sky view (small f), a shield stops the sensor "
         "radiatively over-cooling. That is why a shield does not simply read cold at night."))
A(Paragraph("How the solver works", H2))
A(Paragraph("<font face='Courier'>solve_surface_temperature()</font> does not invert the equation analytically &mdash; the "
            "T<super>4</super> terms prevent that. It brackets the root and bisects. The residual (heat in minus heat out) "
            "is strictly decreasing in T_s because both loss terms grow with T_s, so the root is unique. The bracket "
            "deliberately extends <i>below</i> sky temperature so a genuinely sub-ambient answer is reported honestly "
            "rather than clamped to zero.", BODY))
A(Spacer(1,4))
A(Paragraph("Verified model outputs (recomputed 2026-09-27)", H2))
A(table([["Variant","What it is","Day bias","Night bias"],
         ["V0","Dark closed box, alpha 0.90","<b>+19.416 degC</b>","-4.028 degC"],
         ["V0P","<b>Same geometry</b>, white finish, alpha 0.30","+4.480 degC","-4.028 degC"],
         ["V1","Passive vented shield","+3.003 degC","-0.012 degC"]],
        [0.8*inch, 3.0*inch, 1.55*inch, 1.55*inch]))
A(Paragraph("Day = 1000 W/m<super>2</super>, wind 0.5 m/s, air 30 degC, sky 10 degC. Night = zero solar, calm, clear sky.", SMALL))
A(Spacer(1,6))
A(box("Why the night numbers are the interesting ones",
  [Paragraph("V0 and V0P are <b>identical at night (-4.028 degC)</b>. That is not a coincidence and not a bug: at zero "
             "solar, absorptance multiplies zero, so the only parameter distinguishing them vanishes. The painted box is "
             "the dark box after dark.", BODY),
   Paragraph("Both read <b>below ambient</b>. The sky behaves as a radiative sink roughly 20 K colder than air, and with "
             "half the surface viewing it, radiative loss beats the 0.8 W of internal heating. So 'the enclosure reads hot' "
             "is an incomplete description of the problem &mdash; it reads hot in sun and cold at night.", BODY),
   Paragraph("V1 sits at only -0.012 degC because its sky-view fraction is 0.05 instead of 0.50. The shield works at night "
             "by <i>blocking the sky</i>, not by adding heat.", BODY)]))
A(Spacer(1,6))
A(Paragraph("And the sign is conditional on an assumption", H2))
A(Paragraph("Change only the sky temperature from 10 degC to 29 degC &mdash; a cloudy night rather than a clear one &mdash; "
            "and V0's night bias moves from <b>-4.028 degC to +0.566 degC</b>. The sign flips. This is why the fixed "
            "'sky is 20 K below air' assumption is one of the most consequential unverified numbers in the whole model, and "
            "why Module 6 treats it as a correction target rather than a fact.", BODY))
A(Paragraph("Exercise 1.1 &mdash; predict, then run", H3))
A(Paragraph("Write down answers before executing anything. Getting these wrong is more instructive than reading the table above.", BODY))
A(bullet("(a) V0 in full sun: sign and order of magnitude &mdash; 2 degC or 20 degC?"))
A(bullet("(b) V0 at night, clear sky: sign?"))
A(bullet("(c) Which single term, if deleted, flips your answer to (b)?"))
A(bullet("(d) V0P has 1/3 the absorptance of V0. Is its day bias 1/3 of V0's? Why not?"))
A(Spacer(1,4))
A(code(["cd ~/Developer/repo-professionalization-20260910/sensor-enclosure-thermal-design",
        "PYTHONPATH=. python -c \"",
        "from analysis import thermal_bias as M",
        "i={n:v for n,v,*_ in M.ASSUMPTIONS}; V={v.vid:v for v in M.build_variants()}",
        "for vid in ('V0','V0P','V1'):",
        "    for lbl,G,w in (('day',1000,0.5),('night',0,0.0)):",
        "        h=M.h_external(w,i['h_free_floor'],i['h_wind_slope'])",
        "        d=M.solve_surface_temperature(V[vid],G,i['T_air'],i['T_air']-i['T_sky_offset'],h)-i['T_air']",
        "        print(vid,lbl,round(d,3))\""]))
A(Spacer(1,5))
A(Paragraph("Answer to (d), because it is the one most people miss: no. Absorbed solar drops by a factor of three, but the "
            "loss side is unchanged and the internal 0.8 W is still there, so the bias does not scale linearly with "
            "absorptance. 19.416 to 4.480 is a factor of 4.3, not 3. Non-linear loss terms do that.", BODY))
A(Spacer(1,8))
A(box("Cold question for Module 1",
  [Paragraph("<i>\"Why does a plastic box make a sensor read wrong?\"</i>", BODY),
   Paragraph("Answer in three sentences using the balance. Not \"because it heats up\" &mdash; name which term dominates, "
             "say what the sensor is actually in equilibrium with, and state that the sign reverses at night.", BODY)],
  color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 2 ============================
A(Paragraph("Module 2 &mdash; Variants, and why a shield is not free", H1))
A(Paragraph("The four variants", H2))
A(table([["ID","alpha","phi","A_proj","A_conv","Q_int","f_sky","conv boost","Role"],
         ["V0","0.90","1.00","0.030","0.090","0.80","0.50","1.0","Dark baseline"],
         ["V0P","0.30","1.00","0.030","0.090","0.80","0.50","1.0","<b>Matched-geometry painted control</b>"],
         ["V1","0.30","0.18","0.012","0.020","0.10","0.05","1.4","Passive vented shield"],
         ["V2","0.30","0.18","0.012","0.020","0.10","0.05","1.0","Aspirated (not in scope)"]],
        [0.45*inch,0.45*inch,0.42*inch,0.6*inch,0.62*inch,0.55*inch,0.5*inch,0.72*inch,1.99*inch]))
A(Spacer(1,6))
A(Paragraph("Why V0P exists &mdash; the most important design decision in the study", H2))
A(Paragraph("If you compare a dark box against a shield, you change <b>everything at once</b>: colour, geometry, "
            "ventilation, sensor position, internal heat coupling. Any difference you measure is uninterpretable. "
            "V0P is V0 with <b>only the finish changed</b>. Comparing V0P against V1 at least holds colour constant, so "
            "the remaining difference is attributable to the shield rather than to paint.", BODY))
A(Paragraph("This is the difference between a controlled comparison and a demo. Most of the shield literature compares "
            "whole designs and reports the winner; this project deliberately cannot do that without saying so.", BODY))
A(box("A caveat you must volunteer, not concede",
  [Paragraph("V0 to V0P is an <b>alpha-only</b> change <i>in the model</i>. Real paint changes long-wave emissivity too. "
             "So the physical experiment estimates a joint (alpha, eps) effect, not an absorptance effect. If you present "
             "V0 vs V0P as isolating absorptance, that is an overclaim &mdash; and an examiner who knows coatings will "
             "spot it immediately.", BODY)]))
A(Paragraph("The shield trade-off and how it reverses", H2))
A(Paragraph("A shield blocks solar but introduces a new error: solar-warmed plates heat the air flowing over the sensor "
            "(the pre-heat term). The project quantified how fragile the shield's advantage is with a 24-case screen. "
            "Advantage is defined as |bias of V0P| minus |bias of V1| &mdash; positive means the shield is closer to true "
            "ambient.", BODY))
A(table([["Perturbation applied to V1","V1 bias","Advantage retained"],
         ["<b>None (nominal)</b>","+3.003 degC","<b>+1.477 degC</b>"],
         ["Shading factor 0.18 -&gt; 0.30 (worse shading)","+4.379 degC","+0.101 degC"],
         ["Convection boost 1.4 -&gt; 1.0 (no chimney effect)","+3.449 degC","+1.031 degC"],
         ["Calm pre-heat 1.2 -&gt; 2.4 K (weak venting)","+3.930 degC","+0.549 degC"],
         ["<b>All three together</b>","<b>+6.033 degC</b>","<b>-1.553 degC (REVERSED)</b>"]],
        [3.15*inch, 1.35*inch, 2.4*inch]))
A(Spacer(1,6))
A(box("What this result does and does not mean",
  [Paragraph("<b>Does:</b> one-at-a-time sensitivity is not robustness. Each change individually leaves the shield ahead; "
             "combined, the painted box wins. A study that had only varied parameters singly would have concluded the "
             "shield was safely better.", BODY),
   Paragraph("<b>Does not:</b> prove the shield is worse. These are <i>selected illustrative</i> values, not measured "
             "bounds, not a confidence interval, and not a probability of superiority.", BODY),
   Paragraph("<b>And the sting:</b> all three perturbed parameters are <b>uncited</b> in the register &mdash; no source was "
             "located for any of them. The reversal that reshaped this project's research direction is driven largely by "
             "numbers nobody has justified. That is precisely why they became the top measurement priorities.", BODY)],
  color=RED, bg=colors.HexColor("#FFF3F3")))
A(Spacer(1,6))
A(box("Cold question for Module 2",
  [Paragraph("<i>\"Is the shield better?\"</i>", BODY),
   Paragraph("The correct answer is not yes or no. It is: better under nominal assumptions by about 1.5 degC, but the "
             "advantage reverses when three plausible assumptions move together, and those three assumptions are "
             "currently unsourced &mdash; so the honest answer is that we do not know, and here is the measurement that "
             "would settle it.", BODY)], color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 3 ============================
A(Paragraph("Module 3 &mdash; Dimensional analysis (Study A)", H1))
A(Paragraph("The idea", H2))
A(Paragraph("Buckingham's Pi theorem: a complete physical relation among n quantities requiring k independent units "
            "reduces to <b>i = n - k</b> dimensionless groups. If you hold all groups but one fixed, the remaining one "
            "is fixed too &mdash; regardless of the unknown form of the relation. That is the formal basis for expecting "
            "results to 'collapse' onto a curve.", BODY))
A(Paragraph("The reduction", H2))
A(Paragraph("Linearise the radiation term about ambient using h_r = 4 &middot; eps &middot; sigma &middot; T_air<super>3</super> "
            "(= <b>5.687 W/m<super>2</super>K</b> at 30 degC, eps 0.90). With theta = deltaT / deltaT_sky, the balance "
            "collapses to a closed form in five groups:", BODY))
A(Paragraph("theta = [ Pi_G (1 + N_Q) - N_r f + Pi_d (1 + N_r (1-f)) ] / (1 + N_r)", EQ))
A(table([["Group","Definition","Physical meaning"],
         ["Pi_G","alpha phi G A_proj / (h A_conv deltaT_sky)","Heating number: absorbed solar vs convective removal"],
         ["N_Q","Q / (alpha phi G A_proj)","Internal dissipation vs solar &mdash; <b>the axis shield physics never had</b>"],
         ["N_r","h_r / h","Radiation vs convection coupling"],
         ["f","f_sky","Fraction of the element seeing cold sky"],
         ["Pi_d","delta / deltaT_sky","Ventilation / plate pre-heat, wind dependent"]],
        [0.62*inch, 2.45*inch, 3.83*inch]))
A(Spacer(1,6))
A(Paragraph("The exact nonlinear form &mdash; and why it matters", H2))
A(Paragraph("The linearisation above is an approximation. The <b>exact</b> balance, with no linearisation, also "
            "nondimensionalises &mdash; it just needs one more group, tau = deltaT_sky / T_air, which captures the "
            "T<super>4</super> nonlinearity:", BODY))
A(Paragraph("Pi_G + Pi_Q = theta - d + N_r/(4 tau) &middot; { f[(1+tau theta)<super>4</super> - (1-tau)<super>4</super>] + (1-f)[(1+tau theta)<super>4</super> - (1+tau d)<super>4</super>] }", EQ))
A(Paragraph("Evaluated at all 1,944 design-of-experiments points, the maximum residual is <b>5.478e-9</b> &mdash; solver "
            "tolerance. The model collapses onto dimensionless groups <b>exactly</b>. Remember this: it is the correction "
            "at the centre of Module 4.", BODY))
A(Paragraph("What the linear approximation costs", H2))
A(table([["Regime","n","Median abs error","p95 abs error"],
         ["solar_driven (the design regime)","1220","0.101 degC","0.462 degC"],
         ["near_zero (|deltaT| &lt; 1 degC)","169","0.046 degC","0.469 degC"],
         ["radiation_dominated (deltaT &lt; 0)","349","0.362 degC","0.468 degC"],
         ["<b>high_nonlinearity (deltaT &gt; 20 degC)</b>","206","<b>1.938 degC</b>","<b>14.184 degC</b>"]],
        [2.85*inch, 0.6*inch, 1.7*inch, 1.7*inch]))
A(Paragraph("Overall R<super>2</super> = 0.97217. The linear form is excellent where the project operates and degrades "
            "badly at large bias, exactly as the dropped T<super>4</super> terms predict.", SMALL))
A(Spacer(1,6))
A(box("Two cautions Buckingham himself states",
  [Paragraph("<b>1. The group set is not unique.</b> Buckingham (1914, p.350) notes several equivalent sets exist; only "
             "the <i>count</i> i = n - k is invariant. So 'the five groups' are <i>a</i> valid set, not <i>the</i> set. "
             "Say this before a reviewer does.", BODY),
   Paragraph("<b>2. Completeness is a precondition.</b> Omit a relevant variable and the analysis is wrong. Sonin adds "
             "the converse: superfluous variables add groups that do nothing. A failed collapse therefore means either a "
             "missing variable <i>or</i> a regime change &mdash; never automatically 'similarity fails'.", BODY)]))
A(Spacer(1,6))
A(box("Cold question for Module 3",
  [Paragraph("<i>\"Can you list the parameters in advance, and how far does the reduction go?\"</i> (This is your PI's "
             "actual question &mdash; see Appendix A for the full answer.)", BODY),
   Paragraph("Trap to avoid: the assumptions ledger has 23 entries, but those are <b>not</b> 23 independent physical "
             "variables &mdash; it mixes operating conditions, per-variant settings, empirical closures and sweep ranges. "
             "Claiming '23 reduce to 5' conflates a bookkeeping count with the independent variables of one relation.", BODY)],
  color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 4 ============================
A(Paragraph("Module 4 &mdash; What went wrong, and how it was caught", H1))
A(box("Why this is the most valuable module here",
  [Paragraph("Three conclusions this project published internally were <b>wrong</b>. Each was caught, verified "
             "numerically, and withdrawn in writing with the original record preserved. Most students cannot name a "
             "single error in their own work. You can name three, explain the physics of each, and show the commit that "
             "fixed it. In an interview that is worth more than any result in this repository.", BODY)],
  color=GREEN, bg=colors.HexColor("#F1F8F3")))
A(Paragraph("Error 1 &mdash; \"The collapse failed; there is no universal law\"", H2))
A(table([["What was claimed","Dimensionless collapse was falsified: a preregistered 3% band was exceeded, so no universal law exists and the project is only a ranking study."],
         ["Why it is wrong","The comparison was a <b>linearised</b> closed form against the <b>nonlinear solver derived from the same balance</b>. That measures <b>approximation error</b>, not whether similarity holds. The exact nonlinear balance collapses to 5.478e-9 &mdash; similarity was never in question."],
         ["Second defect","It was called 'preregistered'. No dated pre-run record existed. The exercise was exploratory and is now labelled so."],
         ["Third defect","The 3% band was <b>relative</b>, which is ill-conditioned near zero bias. Absolute degC is the right primary metric."],
         ["Lesson","When a model disagrees with a simplified version of itself, you have measured the simplification &mdash; not the world."]],
        [1.35*inch, 5.55*inch], header=False))
A(Spacer(1,7))
A(Paragraph("Error 2 &mdash; \"Zero bias at night proves there is no self-heating\"", H2))
A(Paragraph("The pilot was designed around a discriminator: self-heating should leave a bias floor that persists after "
            "dark, while solar loading does not. Therefore night convergence to ambient would indicate solar dominance.", BODY))
A(Paragraph("<b>This is false, and the model itself disproves it.</b> At night the electronics heat a sensor up while "
            "long-wave loss to the sky cools it down. The two have opposite sign and can cancel exactly. Concretely, using "
            "V1 geometry: a heat input of", BODY))
A(Paragraph("Q = eps &middot; sigma &middot; A_conv &middot; f_sky &middot; (303.15<super>4</super> - 283.15<super>4</super>) = <b>0.102972 W</b>", EQ))
A(Paragraph("produces a night bias of <b>-1.2e-8 degC</b> &mdash; a nonzero heat source with essentially zero observable "
            "effect. Near-zero night bias is therefore consistent with substantial self-heating.", BODY))
A(Paragraph("<b>The replacement:</b> night/day observations constrain the combined heat balance only. Causal attribution "
            "requires a <b>controlled power intervention</b> &mdash; at least two measured load states with airflow held "
            "fixed, estimating degC per watt. Note the trap that makes this hard: powering down a PM sensor usually stops "
            "its fan too, changing heat <i>and</i> ventilation, which identifies neither.", BODY))
A(Spacer(1,4))
A(Paragraph("Error 3 &mdash; \"Ignoring a shared reference is anti-conservative by 3x\"", H2))
A(Paragraph("The uncertainty budget cited the GUM's worked example of ten resistors calibrated against the same standard: "
            "because the errors are perfectly correlated, they add <b>linearly</b> (1 ohm) rather than in quadrature "
            "(0.316 ohm), so ignoring correlation understates uncertainty by a factor of about three.", BODY))
A(Paragraph("<b>The example is a sum. This pilot's primary comparison is a difference.</b> For simultaneous readings "
            "against the same reference R:", BODY))
A(Paragraph("b_A - b_B = (A - R) - (B - R) = A - B &nbsp;&nbsp;&mdash;&nbsp;&nbsp; R cancels exactly", EQ))
A(Paragraph("Var(b_A - b_B) = Var(b_A) + Var(b_B) - 2 Cov(b_A, b_B). Positive covariance <b>reduces</b> the uncertainty of "
            "a difference. Ignoring it therefore <b>overstates</b> the difference &mdash; the opposite direction from what "
            "was claimed. For an <i>absolute</i> bias the reference still enters in full. The sign depends on the "
            "measurand, and this is now pinned by a regression test.", BODY))
A(Spacer(1,6))
A(box("The pattern across all three",
  [Paragraph("Every one of these survived review because it <b>sounded rigorous</b>. \"Kill criterion tripped.\" "
             "\"Preregistered.\" \"GUM says.\" Each invoked a correct principle in the wrong place. Green tests and a "
             "confident tone detect none of them.", BODY),
   Paragraph("What caught them: <b>deriving the thing independently</b> rather than trusting the summary. The exact "
             "balance was re-derived by hand and checked at 1,944 points. The night counterexample was constructed by "
             "solving for the Q that cancels. The covariance sign was checked by writing out the measurement equation.", BODY)],
  color=NAVY, bg=LGREY))
A(Spacer(1,6))
A(box("Cold question for Module 4",
  [Paragraph("<i>\"Tell me about a time your analysis was wrong.\"</i>", BODY),
   Paragraph("Pick Error 1. It is the most technically impressive because the correction required deriving the exact "
             "nonlinear nondimensionalisation. Structure: what I claimed, why it was wrong, how I verified the "
             "correction, what changed as a result, and what I now do differently.", BODY)], color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 5 ============================
A(Paragraph("Module 5 &mdash; Measurement, uncertainty, and why you cannot validate from a desk", H1))
A(Paragraph("Prediction versus measurement", H2))
A(Paragraph("The hardest discipline in this project is refusing to let a calculation masquerade as a measurement. The "
            "repository enforces four evidence classes and never blurs them:", BODY))
A(table([["Class","Meaning","Example here"],
         ["ANALYTICAL","Model output","Every bias number in Module 1"],
         ["SYNTHETIC","Generated fixture for testing code paths","The intake rehearsal CSVs"],
         ["HISTORICAL-EXTERNAL","Old logs whose provenance is unverified","Prior deployment percentages"],
         ["PHYSICAL-PILOT","Newly acquired measurement","<b>Does not exist</b>"]],
        [1.5*inch, 2.8*inch, 2.6*inch]))
A(Spacer(1,6))
A(Paragraph("The uncertainty engine", H2))
A(Paragraph("<font face='Courier'>analysis/uncertainty.py</font> propagates uncertainty linearly: u_c<super>2</super> = "
            "c<sup>T</sup> Sigma c, with the Jacobian form for several outputs. It is deliberately small &mdash; no "
            "distribution inference, no symbolic algebra, no Monte Carlo. Its value is in what it <b>refuses</b>:", BODY))
A(bullet("<b>A missing uncertainty never defaults to zero.</b> Silence is not precision."))
A(bullet("<b>A covariance matrix that is pairwise legal but jointly impossible is rejected.</b> Correlations of "
         "(0.9, 0.9, -0.9) are each individually valid and collectively non-positive-semidefinite. Checked by eigenvalue."))
A(bullet("<b>The shared-reference cancellation cannot be applied to nodes that are not the same node.</b>"))
A(bullet("<b>It never prints '95%'</b> without a supplied coverage basis. Expanded uncertainty with an unjustified "
         "coverage probability is a false claim dressed as a number."))
A(Paragraph("What U95 &lt;= 0.5 degC actually demands", H2))
A(Paragraph("U = k &middot; u_c. So a target of U95 &lt;= 0.5 degC means <b>u_c &lt;= 0.25 degC</b> at k = 2 &mdash; and "
            "k = 2 corresponds to roughly 95% <b>only</b> under the four GUM G.6.6 conditions: well-behaved input "
            "distributions, <i>comparable</i> contributions, adequate linear approximation, and effective degrees of "
            "freedom above about ten. Those must be <b>demonstrated</b>, not assumed.", BODY))
A(Paragraph("The components you must budget", H2))
A(Paragraph("Sensor calibration; reference calibration; <b>reference radiation/aspiration error</b> (the reference is not "
            "truth); sensor-to-reference location mismatch; clock alignment; drift between pre- and post-checks; solar and "
            "wind measurement uncertainty; model-input uncertainty; and the covariance from one reference serving several "
            "arms. Note that h_c dominates the model-input term &mdash; and the literature states that 10% accuracy in "
            "(h_r + h_c) is <b>not achievable</b>.", BODY))
A(Paragraph("The answer to \"why can't you just validate it?\"", H2))
A(Paragraph("Three partial routes exist without deployment: internal consistency of the reduction (done); cross-model "
            "comparison against CHT (tests numerics, not reality); and held-out geometries against a post-build baseline "
            "&mdash; <b>which requires deployment</b>. So the honest answer is that you cannot, fully, and that is exactly "
            "why the pilot exists.", BODY))
A(Spacer(1,6))
A(box("Cold question for Module 5",
  [Paragraph("<i>\"How will you know your instrument is good enough?\"</i>", BODY),
   Paragraph("Required: the target as a standard uncertainty (0.25 degC), the components that go into it, the shared-"
             "reference covariance treatment, and the statement that the application tolerance is <b>still unresolved</b> "
             "&mdash; so no fit-for-purpose verdict is possible yet.", BODY)], color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 6 ============================
A(Paragraph("Module 6 &mdash; Literature, competitors, and the honest size of the gap", H1))
A(Paragraph("What is already established (and therefore not your contribution)", H2))
A(table([["Source","What it established","Why it constrains you"],
         ["Nakamura &amp; Mahrt 2005","Shield error correlates with a single dimensionless forcing ratio Rad/(rho Cp T U); R<super>2</super> 0.98; RMSE 0.29 -&gt; 0.13 degC","<b>A dimensionless group is not novel.</b> Your Pi_G generalises their X"],
         ["Bernard et al. 2019","Energy-balance shelter model reduced to two fitted coefficients","<b>The direct competitor.</b> But fits <i>after</i> building"],
         ["Shlipak et al. 2025 (Air-STORM)","Transient AQ-enclosure model from materials, weather and internal heat; design planning <i>before</i> build","Overlaps 'forward model of an enclosure' directly"],
         ["Couzo et al. 2024","PurpleAir onboard bias +2.6 degC, RH -17.4 pp over 553 days","The magnitude is known; the cause is not"],
         ["Holder 2020 / Malings 2020","The original +5.23 degC and +2.7 degC figures","Both <b>assert</b> the mechanism; neither measures it"]],
        [1.5*inch, 2.75*inch, 2.65*inch]))
A(Spacer(1,6))
A(box("Three citation traps this project fell into and fixed",
  [Paragraph("<b>1. Wrong authors.</b> The competitor was cited as 'Barbaresco' for months; it is <b>Bernard et al.</b> "
             "The PurpleAir T/RH paper was cited as 'Cha'; it is <b>Couzo, Valencia &amp; Gittis</b>. Both errors came "
             "from an abstract-level scan and survived until someone read the papers.", BODY),
   Paragraph("<b>2. A citation for something the source does not contain.</b> Barkjohn 2021 was cited for a +2.6 degC "
             "temperature bias. <b>It contains no temperature measurement at all</b> &mdash; it quotes other papers.", BODY),
   Paragraph("<b>3. A range that is not a range.</b> The widely repeated '2.7 to 5.3 degC' is two single numbers from two "
             "different papers welded together, asserting <b>two different mechanisms</b> (electronics heat vs shell "
             "trapping heat). Neither paper reports a range.", BODY)], color=RED, bg=colors.HexColor("#FFF3F3")))
A(Paragraph("Where the defensible gap actually is", H2))
A(Paragraph("After reading the competitors properly, the broad claim &mdash; 'forward-modelling enclosure temperature' "
            "&mdash; is <b>occupied</b> by Air-STORM. What survives is narrower and must be stated in bounded language:", BODY))
A(box("The claim, phrased so it survives scrutiny",
  [Paragraph("Can design-known geometry, characterised finish and material properties, and <b>measured electronics "
             "power</b> predict the ambient temperature and RH <b>measurement error</b> of a previously untested printed "
             "enclosure &mdash; and where does that prediction break down?", BODY),
   Paragraph("Air-STORM's endpoint is enclosure <i>temperature</i>. This project's endpoint is calibrated <i>measurement "
             "bias</i>, with quantified uncertainty and a transfer test. Note 'previously untested' must be defined: no "
             "calibration on that <i>unit</i>, on that <i>geometry</i>, or no measurement <i>after fabrication</i> are "
             "three different claims.", BODY)]))
A(Paragraph("How to phrase novelty without lying", H2))
A(bullet("Never: \"no one has done this.\" You have not searched everywhere."))
A(bullet("Instead: \"not found in the checked sources\" &mdash; and state the search boundary."))
A(bullet("The strongest bounded claim available: <b>no source located in this project's search record reports a measured "
         "internal dissipation for a low-cost AQ enclosure together with an attribution of the observed bias to it.</b> "
         "That is defensible, and it names the experiment that would matter."))
A(Spacer(1,6))
A(box("Cold question for Module 6",
  [Paragraph("<i>\"What is new here?\"</i>", BODY),
   Paragraph("Lead with the competitor, not the claim. \"Air-STORM already forward-models enclosure temperature, so a new "
             "thermal model is not the contribution. What is missing is X\" &mdash; naming your strongest rival first is "
             "the single most credible move available to you.", BODY)], color=NAVY, bg=LGREY))
A(PageBreak())

# ============================ MODULE 7 ============================
A(Paragraph("Module 7 &mdash; Process, provenance, and the tooling", H1))
A(Paragraph("Provenance versus evidence status", H2))
A(Paragraph("These are <b>independent</b>, and conflating them is the commonest documentation failure. Provenance says "
            "<i>what kind of number</i> it is; evidence status says <i>how well established</i> it is. A selected design "
            "value can be unverified, analytically assessed, or bench-measured.", BODY))
A(table([["Provenance","Evidence status"],
         ["requirement / measured input / sourced assumption / calculated result / selected design value / measured result / provisional estimate",
          "UNCITED / CONTRADICTED_BY_SOURCE / LAB_REQUIRED / literature_sourced / analytically_assessed / field_measured / UNRESOLVED"]],
        [3.45*inch, 3.45*inch], header=False))
A(Spacer(1,6))
A(Paragraph("What the register reveals", H2))
A(table([["Category","Count","Reading"],
         ["provisional estimate","13","Design or placeholder values"],
         ["UNCITED","7","<b>No source located</b> &mdash; includes 3 of the reversal axes"],
         ["LAB_REQUIRED","6","Cannot be researched; must be measured"],
         ["CONTRADICTED_BY_SOURCE","5","A source exists and <b>disagrees</b>"],
         ["field measured","3","<b>All three belong to other people's systems</b>"]],
        [2.35*inch, 0.8*inch, 3.75*inch]))
A(Spacer(1,5))
A(Paragraph("The five contradicted inputs are worth knowing by name, because each is a live correction: the fixed 20 K "
            "sky depression (actually dewpoint-dependent, roughly 4-34 K); h = 5 + 4U (it is Jurges' correlation with "
            "intercept 5.6, valid only below 5 m/s, and referenced to free-stream not weather-station wind &mdash; where "
            "measured slopes are 0.90 to 2.9); eps = 0.90 (measured polymer films give 0.86-0.89); and alpha = 0.90 for "
            "black (measured blacks are 0.95, so the value is <b>non-conservative</b> for a self-heating model).", BODY))
A(Paragraph("The CAD method &mdash; why a clean rebuild is not evidence", H2))
A(Paragraph("The parametric V0 enclosure was authored on the CAD host and <b>refused unless its measured geometry matched "
            "an independently computed expectation</b>. One <font face='Courier'>geometry.json</font> is read by both the "
            "authoring script and the oracle, so they cannot disagree about inputs &mdash; only about geometry. The oracle "
            "deliberately does <b>not</b> import CadQuery, so the expectation is independent of the authoring path.", BODY))
A(Paragraph("This matters because CAD tools report success while producing wrong geometry: jobs returning status ok with "
            "the template's original volume, silently rejected equations, feature cuts returning None and yielding a solid "
            "block with no features. A screenshot passes every one of those. <b>The number does not.</b>", BODY))
A(box("A live example from this project",
  [Paragraph("The first parameter re-drive <i>appeared</i> to pass &mdash; but the volume had not moved. A shell quoting "
             "error meant the new value never reached the file. The oracle caught it. Redone properly, changing vent width "
             "40 to 55 mm moved the volume by exactly 2,880 mm<super>3</super> = 16 slots x 15 x 4 x 3, which the oracle "
             "predicted independently.", BODY),
   Paragraph("<b>Equations existing is not the test. Re-driving is.</b>", BODY)]))
A(Paragraph("Working practices worth absorbing", H2))
A(bullet("<b>Record corrections; never rewrite history.</b> Dated evidence keeps its original numbers and gains a "
         "correction notice. Current summaries get fixed in place."))
A(bullet("<b>An erratum at the bottom of a document is not a correction.</b> A repo-wide search after one fix found six "
         "documents still asserting the withdrawn claim in their <i>bodies</i> &mdash; readers hit the body first."))
A(bullet("<b>Preregister judgement.</b> State what you expect to matter <i>before</i> you can be told; afterwards you "
         "will rationalise whatever emerged."))
A(bullet("<b>Separate a decision from a fact from a permission.</b> A 21-row 'decision list' mixing all three is "
         "unanswerable; split into evidence packets."))
A(PageBreak())

# ============================ APPENDIX A ============================
A(Paragraph("Appendix A &mdash; Your PI's three questions, answered", H1))
A(Paragraph("These are the questions actually asked. Answer them in this shape.", BODY))
A(Paragraph("Q1. \"Can you list a finite list of parameters in advance?\"", H2))
A(Paragraph("<b>Yes &mdash; with one correction I should make myself.</b> The assumptions ledger has 23 entries, but those "
            "are not 23 independent physical variables: it mixes operating conditions, per-variant settings, empirical "
            "closures and sweep ranges. So I would not claim Buckingham takes 23 parameters to five.", BODY))
A(Paragraph("For the stated steady single-node model, linearising radiation gives five input groups: absorbed solar vs "
            "convection; internal heat vs solar; radiation vs convection; sky-view fraction; and normalised air pre-heat. "
            "Two caveats I would volunteer: the exact nonlinear balance needs a sixth group (sky depression over absolute "
            "ambient), which is fixed in our sweep; and Buckingham states the group set is <b>not unique</b>.", BODY))
A(Paragraph("Q2. \"Can you identify, before building a model, the variables that carry the biggest weight?\"", H2))
A(Paragraph("<b>Partly &mdash; and the honest answer is more useful than a clean one.</b> At the reference daytime point "
            "the painted box is +4.48 degC and the shield +3.00 degC, so the shield leads by about 1.48 degC. Changing "
            "the three uncertain assumptions one at a time leaves it ahead by 0.10, 1.03 and 0.55 degC respectively. "
            "Applying all three together gives +6.03 degC &mdash; the shield is now <b>1.55 degC worse</b>.", BODY))
A(Paragraph("So single-effect ranking is identifiable in advance, but the conclusion is <b>not robust to combinations</b>. "
            "Those are selected illustrative scenarios, not measured bounds. Their value is naming the measurement "
            "priorities: shading, airflow coupling, plate-to-air heat transfer.", BODY))
A(Paragraph("Q3. \"How can you validate this predictive model without deployment?\"", H2))
A(Paragraph("<b>I cannot, and I would not claim to.</b> The model plus an uncontrolled day/night comparison cannot "
            "uniquely attribute the bias: night-time radiative cooling can offset electronics heating, so near-zero night "
            "bias does not establish zero self-heating. In our own model a 0.103 W heat input gives a 1e-8 degC night "
            "bias.", BODY))
A(Paragraph("What is possible without deployment is bounded &mdash; internal consistency of the reduction, and "
            "cross-model comparison &mdash; and neither touches physical accuracy. The smallest informative experiment is "
            "one enclosure, independently logged probe and characterised reference, two or more <b>measured</b> load "
            "states, airflow and exposure held fixed, blocks repeated and counterbalanced, estimating <b>degC per watt</b>. "
            "Transfer to an untested geometry is a separate study.", BODY))
A(box("The move that makes this answer land",
  [Paragraph("Do not defend. Concede the limit immediately, then show you have already designed the experiment that "
             "resolves it, and name what would kill the direction. A student who says \"it cannot be validated from a "
             "desk, here is the smallest experiment that would, and here is what would falsify me\" is doing research. "
             "One who defends the simulation is not.", BODY)], color=GREEN, bg=colors.HexColor("#F1F8F3")))
A(Spacer(1,8))

# ============================ APPENDIX B ============================
A(Paragraph("Appendix B &mdash; Command cookbook", H1))
A(Paragraph("Run these from the repository root. Everything writes to temporary paths; nothing overwrites committed output.", BODY))
A(Paragraph("Full verification (what CI runs)", H3))
A(code(["python -m compileall -q analysis",
        "PYTHONPATH=. python -m unittest discover -s analysis/tests    # 132 tests",
        "python analysis/check_literature_coverage.py                  # 59/59",
        "python tools/check_presentation.py . \"Sensor Enclosure Thermal Design\" sensor-enclosure-thermal-design"]))
A(Paragraph("The analyses", H3))
A(code(["PYTHONPATH=. python -m analysis.nondimensional            # regime table + exact-balance note",
        "PYTHONPATH=. python -m analysis.matched_control_sensitivity --out /tmp/mcs.csv",
        "python analysis/thermal_bias.py --no-figure --table /tmp/day.csv --night-table /tmp/night.csv"]))
A(Paragraph("Reproduce the three corrections yourself", H3))
A(code(["# Error 2: nonzero heat, zero night bias",
        "PYTHONPATH=. python -c \"",
        "from dataclasses import replace",
        "from analysis import thermal_bias as M",
        "i={n:v for n,v,*_ in M.ASSUMPTIONS}; v=[x for x in M.build_variants() if x.vid=='V1'][0]",
        "S=5.670374419e-8",
        "Q=v.eps*S*v.a_conv*v.f_sky*((30+273.15)**4-(10+273.15)**4)",
        "h=M.h_external(0.0,i['h_free_floor'],i['h_wind_slope'])*v.conv_boost",
        "b=M.solve_surface_temperature(replace(v,q_internal=Q),0.0,30.0,10.0,h)-30.0",
        "print('Q =',round(Q,6),'W  ->  night bias =',b)\""]))
A(Paragraph("Files worth reading, in order", H3))
A(table([["File","Why"],
         ["analysis/thermal_bias.py (lines 168-248)","The solver docstring is the best physics writing in the repo"],
         ["docs/studyA_nondimensional.md","The reduction, the corrected verdict, the Biot worked example"],
         ["docs/PARAMETER_REGISTER.csv","Every consequential number and how well it is known"],
         ["docs/TRACEABILITY_INDEX.md","Decision -&gt; analysis -&gt; inputs -&gt; validation, on one page"],
         ["literature/REVIEW_2026-09-22.md","The competitor analysis and the model-input provenance table"],
         ["analysis/tests/test_uncertainty.py","25 hand-derived fixtures; the clearest teaching in the codebase"]],
        [2.85*inch, 4.05*inch]))
A(PageBreak())

# ============================ APPENDIX C ============================
A(Paragraph("Appendix C &mdash; Self-test", H1))
A(Paragraph("Answer without notes. If you can do all fifteen, you own this project.", BODY))
A(Paragraph("Physics", H2))
A(bullet("1. Write the steady energy balance and name every term."))
A(bullet("2. Why do V0 and V0P have identical night bias?"))
A(bullet("3. Why is V0's night bias negative, and what single change makes it positive?"))
A(bullet("4. V0P has one third the absorptance of V0. Why is its day bias not one third?"))
A(bullet("5. Why does a shield not read cold at night, given that it blocks the sky?"))
A(Paragraph("Analysis", H2))
A(bullet("6. State the Pi theorem and the group count. Name the five groups and what each compares."))
A(bullet("7. Why does the exact nonlinear balance need a sixth group?"))
A(bullet("8. What does the 3% band measure &mdash; and what does it <b>not</b> measure?"))
A(bullet("9. What is the Biot number screening, and why does it matter for printed enclosures?"))
A(bullet("10. Why is 'shield better by 1.48 degC' an incomplete statement?"))
A(Paragraph("Method and evidence", H2))
A(bullet("11. Why does zero night bias fail to prove there is no self-heating?"))
A(bullet("12. A shared reference serves three arms. What happens to its uncertainty in an absolute bias, and in a "
         "difference? Which direction does ignoring it err?"))
A(bullet("13. What does U95 &lt;= 0.5 degC require of u_c, and under what conditions is k = 2 legitimate?"))
A(bullet("14. Name the direct competitor and say precisely what it does that this project must not re-claim."))
A(bullet("15. A calculation agrees with a simulation to nine decimal places. What has been validated?"))
A(Spacer(1,8))
A(box("The answer to question 15, because it is the whole point",
  [Paragraph("<b>Nothing physical.</b> Agreement between a model and a rearrangement of the same model is algebra, not "
             "evidence about the world. That confusion produced Error 1 in Module 4, and it is the single most common way "
             "computational work overclaims.", BODY)], color=GREEN, bg=colors.HexColor("#F1F8F3")))
A(Spacer(1,10))
A(Paragraph("Where the project stands", H2))
A(table([["Settled","The physics of the balance; the dimensionless reduction; the uncertainty machinery; the literature position"],
         ["Open on you","Application tolerance; hardware inventory; calibration records; permission for a controlled power intervention"],
         ["Open on measurement","Internal dissipation in watts; solar absorptance of a printed wall; the six lab-required geometry inputs"],
         ["Deliberately unresolved","Five model inputs that a source contradicts &mdash; changing them moves every published number"]],
        [1.5*inch, 5.4*inch], header=False))
A(Spacer(1,12))
A(Paragraph("Prepared 27 September 2026 &mdash; all numerical values recomputed against main 7e35e41 at time of writing. "
            "Every figure in this document is a model output or a literature value; none is a measurement of this enclosure.",
            SMALL))

# ============================ BUILD ============================
def decorate(canv, doc):
    canv.saveState()
    canv.setStrokeColor(BORD); canv.setLineWidth(0.5)
    canv.line(0.9*inch, 0.72*inch, 7.6*inch, 0.72*inch)
    canv.setFont("Helvetica", 7.6); canv.setFillColor(GREY)
    canv.drawString(0.9*inch, 0.55*inch, "Sensor Enclosure Thermal Design — study guide")
    canv.drawRightString(7.6*inch, 0.55*inch, "Page %d" % doc.page)
    canv.restoreState()

doc = BaseDocTemplate("/tmp/pdfbuild/out.pdf", pagesize=LETTER,
                      leftMargin=0.9*inch, rightMargin=0.9*inch,
                      topMargin=0.85*inch, bottomMargin=0.95*inch,
                      title="Sensor Enclosure Thermal Design - Study Guide",
                      author="Project documentation")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=decorate)])
doc.build(STORY)
print("built")
