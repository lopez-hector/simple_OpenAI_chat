import numpy as np
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# load pre clipped

images = np.load('/Users/hectorlopezhernandez/PycharmProjects/chat/preclipped_1.npy')
print(images.shape, images.max(),
      images.min())

images_clip = np.clip(images / 2 + 0.5, 0, 1)

images_max_std = (images - images.min())
images_max_std = images_max_std / (images_max_std.max())

scaled_images = np.zeros_like(images)

for channel in range(images.shape[1]):
    channel_min = images[0, channel].min()
    channel_max = images[0, channel].max()
    scaled_images[0, channel] = (images[0, channel] - channel_min) / (channel_max - channel_min)

images = (images - images.min()) / (images.max() - images.min())

print('EQUAL: ', np.array_equal(images, images_clip))
print(images.shape)
print(images_clip.shape)

fig, ax = plt.subplots(1, 4, figsize=(20, 10), sharex=True, sharey=True)

ax[0].hist(images.flatten(), bins=1000)
ax[0].set_title('MinMax')

ax[1].hist(images_max_std.flatten(), bins=1000)
ax[1].set_title('MaxSTD')

ax[2].hist(images_clip.flatten(), bins=1000)
ax[2].set_title('Clipped')

ax[3].hist(scaled_images.flatten(), bins=1000)
ax[3].set_title('ScaledImage')

labels = ['range', 'max', 'clip', 'scaled']
fig, ax = plt.subplots(2, 2, figsize=(50, 25))
for i, imgs in enumerate([images, images_max_std, images_clip, scaled_images]):
    print('max', imgs.max(), 'min', imgs.min())
    imgs = imgs.transpose((0, 2, 3, 1))
    imgs = (imgs * 255).round().astype("uint8")

    plt.sca(ax[i//2, i%2])
    ax[i//2, i%2].set_title(labels[i])
    plt.imshow(imgs[0])

plt.show()
# print(images.shape, images.max(),
#       images.min())
# [print(i.shape) for i in images]
#
# pil_images = [Image.fromarray(image.squeeze()) for image in images]
#
# img = pil_images[0]
# img.show()
