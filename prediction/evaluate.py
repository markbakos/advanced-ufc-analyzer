
def evaluate_model(model, test_features, test_target):
    """
    Evaluate the model
    """

    test_loss, test_accuracy = model.evaluate(test_features, test_target)

    print(f'Test loss: {test_loss}')
    print(f'Test accuracy: {test_accuracy}')
    
if __name__ == '__main__':
    evaluate_model()