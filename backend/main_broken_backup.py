# backend/main.py
"""
EchoBI v2.0 Backend API

This backend implements intelligent dataset analysis with:
- Dataset classification (Financial, Sales, Time-Series, Healthcare, Generic)
- Column profiling with statistics and quality metrics
- Data quality scoring across multiple dimensions
- Context-aware preprocessing pipelines
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import io
import plotly.express as px
import requests
import os
import uuid
from datetime import datetime

# Import core v2.0 modules
from core import ColumnProfiler, DatasetClassifier, QualityScorer

LM_STUDIO_API = os.getenv("LM_STUDIO_API", "http://localhost:1234/v1/chat/completions")

app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0"# backend/main.py
"""
EchoBI v2.0 Backend API

This backend implements intelligent dataset analysis with:
- Dataset classification (ls"""
EchoBI v2.0 _mEcho
This backend implemenade- Dataset classification (Financial, Sales, Time-Series, de- Column profiling with statistics and quality metrics
- Data quality scorin  - Data quality scoring across multiple dimensions
- C,
- Context-aware preprocessing pipelines
"""

froes"""

from fastapi import FastAPI, Uploim
fut=from fastapi.middleware.cors import CORSMiddleware
from pydicfrom pydantic import BaseModel
from typing importe from typing import Dict, Listnfimport pandas as pd
import io
importbody for import io
import pfiimport p""import requests
import os
coimport os
impo  import udefrom datetio
# Import core v2.0 modules
 Enfrom core import ColumnPr1/
LM_STUDIO_API = os.getenv("LM_STUDIO_API", "http://localhost:12  "
app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0"# backend/main.py
"""
EchoBrea"""
EchoBI v2.0 Backend API

This backend implements intelligent dataset ad.Ecad
This backend implements)- Dataset classification (ls"""
EchoBI v2.0 _mEcho
This b
 EchoBI v2.0 _mEcho
This backenioThis backend impl))- Data quality scorin  - Data quality scoring across multiple dimensions
- C,
- Context-aware preprocessing pipelines
"""

froes"""

froxc- C,
- Context-aware preproail="Unsupported file format")
        
      - Ces"""

froes"""

from fastapi import Fasss
fns[
from f_idfut=from fastapi.middleware.cors if.from pydicfrom pydantic import BaseModel
from typing   from typing importe from typing import   import io
importbody for import io
import pfiimport p""import requestn'importbo  import pfiimport p""imponimport os
coimport os
impo  importrecoimportngimpo  impo [# Import core v2.0 modules
   Enfrom core import ColumsiLM_Sd": session_id,
           app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0"# backe  """
EchoBrea"""
EchoBI v2.0 Backend API

This backend implements intelmns),
    EchoBI v2.ta
This backend implemen   This backend implements)- Dataset classification (laEchoBI v2.0 _mEcho
This b
 EchoBI v2.0 _mEcho
This bacaiThis b
 EchoBI v2st EchocoThis backenioThis pl- C,
- Context-aware preprocessing pipelines
"""

froes"""

froxc- C,
- Context-aware preproail="Unsupp s- C:
"""

froes"""

froxc- C,
- Context-awain
fv2.
froxc-lig- Co modul        
      - Ces"""

froes"""

from fastapi impai      -Ex
froes"""

frs_c
from f, dfns[
from f_idfut=from f")fro  from typing   from typing importe from typing import   import io
importbody for impo  importbody for import io
import pfiimport p""import requestn'imetimport pfiimport p""impclcoimport os
impo  importrecoimportngimpo  impo [# Import core v2.0 modules
   E =impo  impo     Enfrom core import ColumsiLM_Sd": session_id,
           ass           app = FastAPI(title="EchoBI v2.0 Bac: EchoBrea"""
EchoBI v2.0 Backend API

This backend implements intelmns),
    Echo  EchoBI v2.gg
This backend implemenon.    EchoBI v2.ta
This backend imp  This backend ime This b
 EchoBI v2.0 _mEcho
This bacaiThis b
 EchoBI v2st EchocoThis bac profiler.profile_all_co Echo()This bacaiThis b
 #  EchoBI v2st Ecty- Context-aware preprocessing pipelines
""_p"""

froes"""

froxc- C,
- Context-awaer
fsse
froxc-ity- Contex  """

froes"""

froxc- C,
- Context-awa  
f  c
froxc-ion- Contex  fv2.
froxc-ligolfro [      - Ces"""

froes"""

lu
froes"""

frtem
from f   froes"""

frs_c
from f, dfle
frs_c
] =fromumfrom f_i      importbody for impo  importbody for import io
import pfiimport p""import requestn'imetimp  import pfiimport p""import requestn'imetimpos)impo  importrecoimportngimpo  impo [# Import core v2.0 modules
   E =impo  va   E =impo  impo     Enfrom core import ColumsiLM_Sd": sessioco           ass           app = FastAPI(title="EchoBI v2.0 Bac: Ec  EchoBI v2.0 Backend API

This backend implements intelmns),
    Echo  Echum
This backend implemen       Echo  EchoBI v2.gg
This backe_vThis backend implemen  This backend imp  This backend ime This   EchoBI v2.0 _mEcho
This bacaiThis b
 Ec  This bacaiThis b
 ": EchoBI v2st Ecif #  EchoBI v2st Ecty- Context-aware pumn_profiles,
            "quality": {""_p"""

froes"""

froxc- C,
- Context-awaer
fsse
froxc-it  
froes   
froxc-rea- Contex{
fsse
froxc-ity  fro "
froes"""

froxc- C,
y_r
froxc-omp- Contex,
f  c
froxc-ion  fro "froxc-ligolfro [      or
froes"""

lu
froes"""

frtem   
lu
frotenfy"
frtem
ty_fromrt
frs_c
from f, d   from  frs_c
] =frni] =fesimpoquality_report.uniqueness
                },
                "iss   E =impo  va   E =impo  impo     Enfrom core import ColumsiLM_Sd": sessioco           ass           app = FastAPI(title="EchoBI v2.0 Bac: Ec  EchoBI v
 
This backend implements intelmns),
    Echo  Echum
This backend implemen       Echo  EchoBI v2.gg
This backe_vThis backend implemen  This backend imp  This backend i"
     Echo  Echum
This backend imple:This backendse HThis backe_vThis backend implemen  This backeisThis bacaiThis b
 Ec  This bacaiThis b
 ": EchoBI v2st Ecif #  EchoBI v2st Ecty- Context-awareio Ec  This bacai C ": EchoBI v2st Ecifat            "quality": rms or overrides dataset classification."""
    
froes"""

froxc- C,
- Context in
froxcons:- Contex rfsse
froxc-it tifrostfroes   
=4froxc-raifsse
froxc-ity  funfro
 froes"""

froxc =
froxc-ns[y_r
froxtifr.sf  c
froxc-ion  f  fro nfroes"""

lu
froes"""

frtem   
lu
frot  
lu
froHTTfEx
frteon(stlu
frotdef40frtem
tyl=ty_fasft not anafromd ] =frni] =fesimpoqualiir                },
                "iss ifi                "]  
This backend implements intelmns),
    Echo  Echum
This backend implemen       Echo  EchoBI v2.gg
This backe_vThis backend implemen  This backend imp  This backend i"
  nfid    Echo  Echum
This backend impl'cThis backend i][This backe_vThis backend implemen  This backenf     Echo  Echum
This backend imple:This backendse HThis backe_vThituThis backend im,
 Ec  This bacaiThis b
 ": EchoBI v2st Ecif #  EchoBI v2st Ecty- Context-awareio E "message": f"Clas ": EchoBI v2st Ecif.     
froes"""

froxc- C,
- Context in
froxcons:- Contex rfsse
froxc-it tifrostfroes   
=4froxc-raifsse
froxc-ity  funfro
 froes"""

froxc =
froxc-ns[y_r
froxtifratfro: 
froxc-ed"- Contex  froxcons:- e"froxc-it tifrostfroes ct=4froxc-raifsse
froxc-iy.froxc-ity  fun " froes"""

froxc: 
froxc =ialfroxc-lefroxtifr.sferfroxc-ion  f ca
lu
froes"""

frtem   
lu
