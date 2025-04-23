import keras
from keras import layers
import numpy as np

def prediction_model(n_features, n_classes):
    """
    Builds a prediction model using a neural network.
    """

    # create input layer
    inputs = keras.Input(shape=(n_features,))

    masked_inputs = layers.Masking(mask_value=np.nan)(inputs)

    # create a dense layer
    x = layers.Dense(128, activation='relu')(masked_inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(64, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)

    outputs = layers.Dense(n_classes, activation='softmax')(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    # compile model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model

