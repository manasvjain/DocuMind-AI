import numpy as np,sys; sys.path.insert(0,'ml'); sys.path.insert(0,'.')
from ml.evaluation.metrics import segmentation_metrics
def test_metrics_perfect_prediction():
    y=np.array([[0,1],[1,0]]); m=segmentation_metrics(y,y,2); assert m['accuracy']==1.0; assert m['mean_iou']==1.0; assert m['dice']==1.0
