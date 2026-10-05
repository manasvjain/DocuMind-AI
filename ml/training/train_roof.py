import argparse,pandas as pd,joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from ml.roof_classifier import ROOF_CLASSES
from ml.roof_classifier import extract_visual_features

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--csv',required=True);ap.add_argument('--output',default='data/models/roof_rf.joblib');a=ap.parse_args();df=pd.read_csv(a.csv);X=[];y=[]
    for row in df.itertuples():
        import cv2
        img=cv2.imread(row.image_path);img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB);X.append(extract_visual_features(img));y.append(row.roof_type)
    Xtr,Xv,ytr,yv=train_test_split(X,y,test_size=.2,random_state=42,stratify=y if len(set(y))>1 else None);model=RandomForestClassifier(n_estimators=300,random_state=42,class_weight='balanced');model.fit(Xtr,ytr);print(classification_report(yv,model.predict(Xv),zero_division=0));joblib.dump(model,a.output)
if __name__=='__main__':main()
