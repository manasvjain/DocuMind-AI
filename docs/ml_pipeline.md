# ML Pipeline
Classes: background, building, road, water, vegetation, candidate parcel.
U-Net is baseline; DeepLabV3+ and SegFormer-style models share the model factory. Metrics include accuracy, precision, recall, F1, IoU, mean IoU, Dice and confusion matrix. Untrained models must report Not evaluated/N/A.
Roof classification returns Unknown until a real labelled roof checkpoint exists.
