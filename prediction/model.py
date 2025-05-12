import keras
from keras import layers
import tensorflow as tf

def prediction_model(n_features, n_result_classes, n_win_method_classes):
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

    result_output = layers.Dense(n_result_classes, activation='softmax', kernel_initializer='glorot_normal', name='result')(x)
    win_method_output = layers.Dense(n_win_method_classes, activation='softmax', kernel_initializer='glorot_normal', name='win_method')(x)

    model = keras.Model(inputs=inputs, outputs=[result_output, win_method_output])

    # compile model
    optimizer = keras.optimizers.Adam(learning_rate=0.0005)
    model.compile(optimizer=optimizer,
                    loss={
                        'result': 'sparse_categorical_crossentropy',
                        'win_method': 'sparse_categorical_crossentropy'
                    },
                    loss_weights={'result': 1.0, 'win_method': 1.0},
                    metrics={'result': 'accuracy', 'win_method': 'accuracy'}
                )

    return model

