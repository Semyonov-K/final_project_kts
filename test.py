import time

real_timer = 5
for _ in range(real_timer):
    real_timer -= 1
    time.sleep(1)
    print(real_timer)
print("end")