import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Constants
test_dir = 'C:/Users/DELL/OneDrive/Desktop/clg projectarchive (1)/test'  # Update with your test directory path
img_height, img_width = 48, 48
batch_size = 32

# Data generator for testing
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    color_mode='grayscale',
    class_mode='categorical',
    shuffle=False  # Ensure data is not shuffled for evaluation
)

# Load the saved model
model = load_model('fer2013_cnn_model.h5')

# Evaluate the model on the test data
test_loss, test_accuracy = model.evaluate(test_generator, verbose=1)
print(f'Test accuracy: {test_accuracy:.4f}')
