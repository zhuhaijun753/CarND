import pickle
import tensorflow as tf
import numpy as np
import time
from scipy.misc import imread
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from alexnet import AlexNet

# TODO: Load traffic signs data.
with open('./train.p', mode='rb') as f:
    train = pickle.load(f)   
X_train, y_train = train['features'], train['labels']
nb_classes = len(np.unique(y_train))

# TODO: Split data into training and validation sets.
X_train, y_train = shuffle(X_train, y_train)
X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=0.33, random_state=0)

# TODO: Define placeholders and resize operation.
x = tf.placeholder(tf.float32, (None, 32, 32, 3))
y = tf.placeholder(tf.int64, (None))
resized = tf.image.resize_images(x, (227, 227))

# TODO: pass placeholder as first argument to `AlexNet`.
fc7 = AlexNet(resized, feature_extract=True)
# NOTE: `tf.stop_gradient` prevents the gradient from flowing backwards
# past this point, keeping the weights before and up to `fc7` frozen.
# This also makes training faster, less work to do!
fc7 = tf.stop_gradient(fc7)

# TODO: Add the final layer for traffic sign classification.
shape = (fc7.get_shape().as_list()[-1], nb_classes)  # use this shape for the weight matrix
fc8W = tf.Variable(tf.truncated_normal(shape, stddev=1e-2))
fc8b = tf.Variable(tf.zeros(nb_classes))
logits = tf.nn.xw_plus_b(fc7, fc8W, fc8b)

# TODO: Define loss, training, accuracy operations.
# HINT: Look back at your traffic signs project solution, you may
# be able to reuse some the code.
EPOCHS = 10
BATCH_SIZE = 128

cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits, y)
loss_operation = tf.reduce_mean(cross_entropy)
optimizer = tf.train.AdamOptimizer()
training_operation = optimizer.minimize(loss_operation, var_list=[fc8W, fc8b])

prediction = tf.arg_max(logits, 1)
accuracy_operation = tf.reduce_mean(tf.cast(tf.equal(prediction, y), tf.float32))

def evaluate(X_data, y_data):
    num_examples = len(X_data)
    total_accuracy = 0
    sess = tf.get_default_session()
    for offset in range(0, num_examples, BATCH_SIZE):
        batch_x, batch_y = X_data[offset:offset+BATCH_SIZE], y_data[offset:offset+BATCH_SIZE]
        accuracy = sess.run(accuracy_operation, feed_dict={x: batch_x, y: batch_y})
        total_accuracy += (accuracy * len(batch_x))
    return total_accuracy / num_examples


# TODO: Train and evaluate the feature extraction model.
with tf.Session() as sess:
	sess.run(tf.global_variables_initializer())
	num_examples = len(X_train)

	print("Training...")
	print()
	for i in range(EPOCHS):
		X_train, y_train = shuffle(X_train, y_train)
		for offset in range(0, num_examples, BATCH_SIZE):
			end = offset + BATCH_SIZE
			batch_x, batch_y = X_train[offset:end], y_train[offset:end]
			sess.run(training_operation, feed_dict={x: batch_x, y: batch_y})
	    
	validation_accuracy = evaluate(X_validation, y_validation)
	print("EPOCH {} ...".format(i+1))
	print("Validation Accuracy = {:.3f}".format(validation_accuracy))
	print()
