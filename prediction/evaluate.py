import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

def evaluate_model(model, test_features, test_target):
    """
    Evaluate the model
    """
    # evaluate the model
    test_loss, test_accuracy = model.evaluate(test_features, test_target)
    print(f'Test loss: {test_loss}')
    print(f'Test accuracy: {test_accuracy}')
    
    # get predictions
    predictions = model.predict(test_features)
    predicted_classes = np.argmax(predictions, axis=1)
    
    print("\nClassification Report:")
    print(classification_report(test_target, predicted_classes))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(test_target, predicted_classes)
    print(cm)
    
    print("\nPer-class Accuracy:")
    for i in range(len(np.unique(test_target))):
        class_indices = np.where(test_target == i)[0]
        if len(class_indices) > 0:
            class_accuracy = np.mean(predicted_classes[class_indices] == test_target[class_indices])
            print(f"Class {i}: {class_accuracy:.4f} ({np.sum(predicted_classes[class_indices] == test_target[class_indices])}/{len(class_indices)})")