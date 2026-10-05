import numpy as np,torch
def confusion_matrix(y_true,y_pred,num_classes):
    cm=np.zeros((num_classes,num_classes),dtype=np.int64)
    for t,p in zip(y_true.ravel(),y_pred.ravel()):
        if 0<=t<num_classes and 0<=p<num_classes: cm[int(t),int(p)]+=1
    return cm
def segmentation_metrics(y_true,y_pred,num_classes):
    cm=confusion_matrix(y_true,y_pred,num_classes);tp=np.diag(cm).astype(float);fp=cm.sum(0)-tp;fn=cm.sum(1)-tp
    precision=np.divide(tp,tp+fp,out=np.zeros_like(tp),where=(tp+fp)!=0);recall=np.divide(tp,tp+fn,out=np.zeros_like(tp),where=(tp+fn)!=0);f1=np.divide(2*precision*recall,precision+recall,out=np.zeros_like(tp),where=(precision+recall)!=0);iou=np.divide(tp,tp+fp+fn,out=np.zeros_like(tp),where=(tp+fp+fn)!=0);dice=np.divide(2*tp,2*tp+fp+fn,out=np.zeros_like(tp),where=(2*tp+fp+fn)!=0)
    return {"accuracy":float(tp.sum()/max(cm.sum(),1)),"precision":float(np.mean(precision)),"recall":float(np.mean(recall)),"f1":float(np.mean(f1)),"mean_iou":float(np.mean(iou)),"dice":float(np.mean(dice)),"per_class_iou":{str(i):float(v) for i,v in enumerate(iou)},"confusion_matrix":cm.tolist()}
def compute_batch_metrics(logits:torch.Tensor,masks:torch.Tensor,num_classes:int)->dict:return segmentation_metrics(masks.detach().cpu().numpy(),logits.argmax(1).detach().cpu().numpy(),num_classes)
