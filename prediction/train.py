import json
import pandas as pd
import os
from keras import callbacks
from model import prediction_model

def train_model():
    """
    Train the model
    """
    os.makedirs('models', exist_ok=True)
    
    # load train data
    train_features = pd.read_csv('data/splits/train_features.csv')
    train_target = pd.read_csv('data/splits/train_target.csv')
    
    # load val data
    val_features = pd.read_csv('data/splits/val_features.csv')
    val_target = pd.read_csv('data/splits/val_target.csv')
    
    # load test data
    test_features = pd.read_csv('data/splits/test_features.csv')
    test_target = pd.read_csv('data/splits/test_target.csv')

    model = prediction_model(train_features.shape[1], train_target.shape[1])
    
    # define callbacks
    callback = [
        callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.0001
        ),
        callbacks.ModelCheckpoint(
            'models/model.keras',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )
    ]
    
    history = model.fit(
        train_features,
        train_target,
        epochs=100,
        batch_size=64,
        validation_data=(val_features, val_target),
        callbacks=callback,
        verbose=1
    )
    
    # save history
    with open('history.json', 'w') as f:
        json.dump(history.history, f)
        
if __name__ == '__main__':
    train_model()