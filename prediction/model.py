import keras
from keras import layers
import numpy as np
from keras.src.backend import backend
import tensorflow as tf


def prediction_model(n_features, n_classes):
    """
    Builds a prediction model using a neural network.
    """

    # create input layer
    inputs = keras.Input(shape=(n_features,))

    x = layers.Lambda(lambda x: tf.where( tf.math.is_nan(x), tf.zeros_like(x), x))(inputs)

    # create dense layers
    x = layers.Dense(128, activation='relu',  kernel_initializer='he_normal', kernel_regularizer=keras.regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(64, activation='relu', kernel_initializer='he_normal', kernel_regularizer=keras.regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)

    outputs = layers.Dense(n_classes, activation='softmax', kernel_initializer='glorot_normal')(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    # compile model
    optimizer = keras.optimizers.Adam(learning_rate=0.0005)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model

