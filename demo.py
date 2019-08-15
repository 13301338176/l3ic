#!/usr/bin/python3
import os
import imageio
import argparse
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import matplotlib.pyplot as plt
from datetime import datetime
from skimage.measure import compare_ssim

from models.dcn import DCN
from helpers import afi


def quickshow(ax, image, title):
    ax.imshow(image.squeeze())
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])


parser = argparse.ArgumentParser(description='Show results from NIP & FAN optimization')
parser.add_argument('-i', '--image', default='./samples/md575e5a225f.png')
parser.add_argument('-m', '--model', dest='model', action='store', default='8k',
                    help='DCN model - corresponds to quality (4k, 8k, 16k)')
parser.add_argument('-s', '--stats', dest='stats', action='store_true', default=False,
                    help='Show detailed stats')

args = parser.parse_args()

image = imageio.imread(args.image).astype(np.float32) / 255
image = np.expand_dims(image, axis=0)

dcn = DCN(args.model)

t1 = datetime.now()
compressed, image_bytes = afi.simulate_compression(dcn, image)
t2 = datetime.now()
ssim = compare_ssim(image.squeeze(), compressed.squeeze(), multichannel=True, data_range=1.0)

print('Full compression + decompression time :', (t2 - t1).total_seconds(), 's')
print('Bitstream                             : {:,} bytes ({:.3f} bpp)'.format(image_bytes, 8 * image_bytes / image.shape[1] / image.shape[2]))
print('SSIM                                  : {:.3f}'.format(ssim))
fig, axes = plt.subplots(1, 2)
quickshow(axes[0], image, 'Input')
quickshow(axes[1], compressed, 'Simulated (DCN) ssim={:.2f}'.format(ssim))
fig.tight_layout()
plt.show()
