import sys, glob, csv, cv2, torch
torch.set_num_threads(1)
from facenet_pytorch import MTCNN
m=MTCNN(select_largest=True, post_process=False, min_face_size=64, device='cpu')
man=[r for r in csv.DictReader(open('/mnt/t7/smad_next/RS1/athena/athena_manifest.csv'))]
for s in ['M_mordiff','a43_E','a43_D20','M_facemorpher','G_raw']:
    rows=[r for r in man if r['set']==s][:6]
    out=[]
    for r in rows:
        img=cv2.imread(r['src_path'])
        b,p,l=m.detect(img, landmarks=True)
        if l is None: out.append('noface'); continue
        x1,y1,x2,y2=b[0]; w=x2-x1; h=y2-y1
        x1-=.05*w; y1-=.05*h; x2+=.05*w; y2+=.05*h
        c=img[round(y1):round(y2), round(x1):round(x2)]
        out.append('%s img%s box(%d,%d,%d,%d)->crop%s'%(r['id'][-4:],img.shape[:2],round(x1),round(y1),round(x2),round(y2),c.shape[:2]))
    print(s); [print('  ',o) for o in out]
