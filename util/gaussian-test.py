#!/usr/bin/python

# Import the packages you need
import numpy as np
import matplotlib.pyplot as plt
#from scipy.misc import imsave

# Create the image data
image_data = np.zeros(512*512, dtype=np.float32).reshape(512,512)
random_data = np.random.randn(512,512)
image_data = image_data + 100.*random_data

print 'Size: ', image_data.size
print 'Shape: ', image_data.shape 
scaled_image_data = image_data / 255.

# Save and display the image 
#imsave('noise.png', scaled_image_data)
plt.imshow(scaled_image_data, cmap='gray')
plt.show()

exit()
