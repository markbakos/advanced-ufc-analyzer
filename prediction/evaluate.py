import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

def evaluate_model(model, test_features, test_target):
    """
    Evaluate the model
    """
    # evaluate the model
    
    # get predictions
    predictions = model.predict(test_features)

    result_pred = np.argmax(predictions[0], axis=1)
    win_method_pred = np.argmax(predictions[1], axis=1)

    result_target = test_target[0]
    win_method_target = test_target[1]

    print("\nResult Prediction Metrics:")
    print(classification_report(result_target, result_pred))
    print("\nConfusion Matrix for Result:")
    print(confusion_matrix(result_target, result_pred))

    print("\nWin Method Prediction Metrics:")
    print(classification_report(win_method_target, win_method_pred, zero_division=""))
    print("\nConfusion Matrix for Win Method:")
    print(confusion_matrix(win_method_target, win_method_pred))