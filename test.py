import random

a = {"name":"a", "speed":4, "item":"Tricked Coin"}
b = {"name":"b", "speed":3, "item":"u"}
c = {"name":"c", "speed":4, "item":"a"}
d = {"name":"d", "speed":3, "item":"a"}
e = {"name":"e", "speed":5, "item":"a"}
f = {"name":"f", "speed":5, "item":"Tricked Coin"}
g = {"name":"g", "speed":5, "item":"Tricked Coin"}

vel = [a, b, c, d, e, f, g]
random.shuffle(vel)
vel = sorted(vel, key=lambda x: x["item"]=="Tricked Coin", reverse=True)
vel = sorted(vel, key=lambda x: x["speed"], reverse=True)
for i in vel:
    print(i)
