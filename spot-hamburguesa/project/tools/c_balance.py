import sys, numpy as np, soundfile as sf, pyloudnorm as pyln
x,sr=sf.read(sys.argv[1]); m=pyln.Meter(sr); y=x.copy()
for f in m._filters.values(): y=f.apply_filter(y)
def mx(a,b,w=0.1):
    w=int(w*sr); h=int(0.01*sr); return max(-0.691+10*np.log10(np.sum(np.mean(y[i:i+w]**2,axis=0))+1e-12) for i in range(int(a*sr),int(b*sr)-w,h))
ref=mx(17.05,17.5)
print('integrated',round(m.integrated_loudness(x),2),'| bite(100ms)',round(ref,1),'| relative to bite:')
print(' | '.join(f'{n} {mx(a,b)-ref:+.1f}' for n,a,b in [('ASMR',0,0.9),('impacto',0.95,1.4),('ASMR2',1.5,3.3),('pan',3.7,7.3),('drop',7.4,7.9),('motion',7.9,10.6),('T3',10.6,11.0),('3D',11,13.4),('T4',13.4,13.9),('org',13.9,15.6),('regreso',15.7,16.9),('plato',18.6,19.7),('copy',19.9,22.3),('firma',22.7,24),('fin',24.6,25)]))
