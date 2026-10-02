import numpy as np, json
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
rng=np.random.default_rng(1); N=50; DT=.02; CL=["normal","bump","hard_brake","shake"]
def window(c):
    h=rng.normal(0,.3,(N,2)); v=rng.normal(0,.4,N); i=np.arange(N)
    if c==0: h[:,0]+=rng.uniform(0,2.5)*np.sin(i/rng.uniform(6,20)+rng.uniform(0,6))
    if c==1:
        s=rng.integers(5,35); k=np.arange(8); v[s:s+8]+=rng.uniform(5,15)*np.exp(-k/3)*np.cos(k*1.2); h[s:s+8]+=rng.normal(0,1.2,(8,2))
    if c==2:
        s=rng.integers(0,30); d=rng.integers(15,45); a=rng.uniform(4,9); d=min(d,N-s); h[s:s+d,0]+=a*np.minimum(1,np.arange(d)/4)
    if c==3: h=rng.normal(0,rng.uniform(3,8),(N,2)); v=rng.normal(0,rng.uniform(3,8),N)
    th=rng.uniform(0,6.28); R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
    return h@R.T, v
def feats(h,v):
    hm=np.linalg.norm(h,axis=1); mh=hm.mean()
    return [hm.max(),mh,(hm>3).mean(),np.abs(v).max(),v.std(),np.linalg.norm(h.mean(0))/(mh+1e-6),np.abs(np.diff(hm)).max()/DT/100]
X=[];y=[]
for c in range(4):
    for _ in range(2500): X.append(feats(*window(c))); y.append(c)
X=np.array(X);y=np.array(y)
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,stratify=y,random_state=1)
sc=StandardScaler().fit(Xtr); m=MLPClassifier((16,),max_iter=800,random_state=1).fit(sc.transform(Xtr),ytr)
pr=m.predict(sc.transform(Xte)); acc=accuracy_score(yte,pr)
print("test accuracy:",round(acc,4)); print(CL); print(confusion_matrix(yte,pr))
json.dump({"classes":CL,"arch":"7-16-4","acc":acc,"mean":sc.mean_.tolist(),"scale":sc.scale_.tolist(),
 "W":[w.tolist() for w in m.coefs_],"b":[b.tolist() for b in m.intercepts_]},open("public/model.json","w"))
