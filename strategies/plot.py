import numpy as np
import pandas as pd
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from  yahoo_fin import stock_info as si
import base64
from io import BytesIO


plt.style.use('fivethirtyeight')
x_vals = []
n = 24 * 60 * 60
y1 = []
y2 = []
xmin = 0
xmax = 200

index = count()
def animate(i):
    x_vals.append(next(index))
    price = si.get_live_price("aapl")
    y1.append(price)
    plt.cla()
    axes = plt.gca()
    axes.set_xlim([xmin,xmax])
    axes.set_ylim([price-3,price+3])
    plt.tight_layout()
    plt.plot(x_vals, y1, label='aapl price')
    plt.legend(loc='upper left')
    plt.grid(True)

ani = FuncAnimation(plt.gcf(), animate, interval=60000)

plt.tight_layout()
plt.grid(True)
plt.show()