import json
import pandas as pd
import os
from keras import callbacks
from prediction.model import prediction_model
from evaluate import evaluate_model

def train_model():
    """
    Train the model
    """
    os.makedirs('models', exist_ok=True)

    # load train data
    train_features_df = pd.read_csv('data/splits/train_features.csv')
    train_target_df = pd.read_csv('data/splits/train_target.csv')
    train_target = train_target_df['result']
    train_win_method = train_target_df['win_method']

    # load val data
    val_features_df = pd.read_csv('data/splits/val_features.csv')
    val_target_df = pd.read_csv('data/splits/val_target.csv')
    val_target = val_target_df['result']
    val_win_method = val_target_df['win_method']

    # load test data
    test_features_df = pd.read_csv('data/splits/test_features.csv')
    test_target_df = pd.read_csv('data/splits/test_target.csv')
    test_target = test_target_df['result']
    test_win_method = test_target_df['win_method']

    result_class_counts = train_target.value_counts()
    win_method_class_counts = train_win_method.value_counts()

    total_result_samples = len(train_target)
    total_win_method_samples = len(train_win_method)

    # calculate class weights for both output

    result_class_weights = {cls: total_result_samples / (len(result_class_counts) * count) for cls, count in result_class_counts.items()}
    win_method_class_weights = {cls: total_win_method_samples / len(win_method_class_counts) * count for cls, count in win_method_class_counts.items()}

    # convert to numpy arrays
    X_train = train_features_df.to_numpy()
    X_val = val_features_df.to_numpy()
    X_test = test_features_df.to_numpy()

    y_train_result = train_target.to_numpy()
    y_train_win_method = train_win_method.to_numpy()

    y_val_result = val_target.to_numpy()
    y_val_win_method = val_win_method.to_numpy()

    y_test_result = test_target.to_numpy()
    y_test_win_method = test_win_method.to_numpy()

    # define callbacks
    early_stopping = callbacks.EarlyStopping(
        monitor='val_result_accuracy',
        patience=10,
        mode='max',
        restore_best_weights=True,
        verbose=1
    )

    reduce_lr = callbacks.ReduceLROnPlateau(
        monitor='val_result_accuracy',
        factor=0.2,
        patience=5,
        min_lr=1e-5,
        verbose=1
    )

    model_checkpoint = callbacks.ModelCheckpoint(
        'models/model.keras',
        monitor='val_result_accuracy',
        save_best_only=True,
        verbose=1
    )

    # create and train model
    model = prediction_model(X_train.shape[1], len(result_class_counts), len(win_method_class_counts))
    model.summary()

    history = model.fit(
        X_train,
        [y_train_result, y_train_win_method],
        validation_data=(X_val, [y_val_result, y_val_win_method]),
        epochs=100,
        batch_size=32,
        callbacks=[early_stopping, reduce_lr, model_checkpoint],
        verbose=1
    )
    
    # save history
    with open('history.json', 'w') as f:
        json.dump(history.history, f)

    # evaluate model
    evaluate_model(model, X_test, [y_test_result, y_test_win_method])

if __name__ == '__main__':
    train_model()