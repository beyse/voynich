"""Colour features of the page illustrations (PDF pages 3..116 = f1r..f58v, f12 missing) as external 'content' variables.
Classification is relative to each page's parchment tone (median colour)."""
import fitz, json
import numpy as np
from PIL import Image
doc=fitz.open("Voynich_Manuscript.pdf")
present=[f for f in range(1,59) if f!=12]
def folio_of_page(p):
    i=p-3; return f"f{present[i//2]}{'r' if i%2==0 else 'v'}"
feats={}
for p in range(3,117):
    pix=doc[p-1].get_pixmap(dpi=50); a=np.asarray(Image.frombytes("RGB",(pix.width,pix.height),pix.samples)).astype(float)/255
    h,w,_=a.shape; a=a[int(.06*h):int(.94*h), int(.06*w):int(.94*w)]
    med=np.median(a.reshape(-1,3),0); dev=np.linalg.norm(a-med,axis=-1)
    r,g,b=a[...,0],a[...,1],a[...,2]; off=dev>0.12
    green=off&(g>r+0.03)&(g>=b-0.02)
    blue=off&(b>r+0.03)&(b>g+0.01)
    red=(dev>0.18)&(r>g+0.08)&(g>b)&(r<med[0])&(a.max(-1)>0.3)
    def centroid(mask):
        ys,xs=np.nonzero(mask); return (float(ys.mean()/mask.shape[0]) if len(ys) else 0.5, float(xs.mean()/mask.shape[1]) if len(xs) else 0.5)
    gc=centroid(green); bc=centroid(blue); rc=centroid(red); tot=max(1,green.sum()+blue.sum()+red.sum())
    gh=np.degrees(np.arctan2(np.sqrt(3)*(g-b),2*r-g-b))[green]
    feats[folio_of_page(p)]=dict(page=p,green=float(green.mean()),blue=float(blue.mean()),red=float(red.mean()),
        green_y=gc[0],green_x=gc[1],red_y=rc[0],blue_y=bc[0],green_hue=float(gh.mean()) if len(gh) else 0.0,
        blue_frac=float(blue.sum()/tot),red_frac=float(red.sum()/tot),colour_total=float((green|blue|red).mean()))
json.dump(feats,open('results/page_colors.json','w'),indent=1)
import statistics
for k in ('green','blue','red','colour_total'):
    vals=[f[k] for f in feats.values()]; print(f"{k}: mean {statistics.mean(vals):.3f} sd {statistics.pstdev(vals):.3f} min {min(vals):.3f} max {max(vals):.3f}")
for f in ('f1r','f2r','f26r','f27r','f58r'): print(f,{k:round(v,3) for k,v in feats[f].items() if k!='page'})
