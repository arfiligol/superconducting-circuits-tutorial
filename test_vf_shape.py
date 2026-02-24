import numpy as np

from core.analysis.domain.math.s_parameters import MultiResonanceVectorFitter, notch_s21

f = np.linspace(6.2e9, 6.3e9, 1000)
# Create a dummy notch resonance: fr=6.25 GHz, Ql=1000, Qc=1200
s21 = notch_s21(f, fr=6.25e9, Ql=1000, Qc_real=1200, Qc_imag=0, a=1.0, alpha=0, tau=0)

fitter = MultiResonanceVectorFitter(f, s21)
res = fitter.fit(n_resonators=1)

vf = fitter.vf_engine
print("Type of residues:", type(vf.residues))
print("Shape of residues:", np.shape(vf.residues))

# Print the actual object to see what it is
import pprint

pprint.pprint(vf.residues)
