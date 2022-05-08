import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from perlin_noise import PerlinNoise

noise1 = PerlinNoise(octaves=3)
noise2 = PerlinNoise(octaves=6)
noise3 = PerlinNoise(octaves=12)
noise4 = PerlinNoise(octaves=24)

xpix, ypix = 135, 240
pic = []
for i in range(xpix):
    row = []
    for j in range(ypix):
        noise_val =         noise1([i/xpix, j/ypix])
        noise_val += 0.6  * noise2([i/xpix, j/ypix])
        noise_val += 0.3 * noise3([i/xpix, j/ypix])
        #noise_val += 0.125* noise4([i/xpix, j/ypix])
        row.append(round(noise_val, 1))
    pic.append(row)

#plt.imshow(pic, cmap='terrain')
plt.imshow(pic, cmap='binary')
plt.savefig('map.png', dpi='figure', format='png', metadata=None, bbox_inches='tight', pad_inches=0.0, facecolor='auto', edgecolor='auto', backend=None)
plt.show()