
import matplotlib.pyplot as plt


def print_graphics(data):
    plt.figure()
    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.show()


def save_graphics(data, path, name):
    fig = plt.figure(figsize=(20, 10))

    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.savefig(path+'/' + name + '.png')
    plt.close()
