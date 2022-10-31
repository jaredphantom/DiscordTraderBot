import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
from discord import Webhook, File

def createGraph(values: list, name):
    array = numpy.array(values)
    if values[-1] > 0:
        plt.plot(array, color="green")
    else:
        plt.plot(array, color="red")
    plt.title(f"{name.upper()} Trade")
    plt.xlabel("Time (ticks)")
    plt.ylabel("P/L (%)")
    fname = f"graphs/{name}.png"
    plt.savefig(fname, bbox_inches="tight")
    plt.close()

def sendGraph(webhook: Webhook, name):
    fname = f"graphs/{name}.png"
    with open(fname, 'rb') as f:
        file = File(f)
    webhook.send(file=file)
    
def discGraph(values: list, name, webhook: Webhook):
    createGraph(values, name)
    sendGraph(webhook, name)
