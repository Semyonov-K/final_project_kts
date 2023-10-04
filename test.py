# import time
# def start_timer(timer: int):
#     while timer != 0:
#         timer -= 1
#         print(timer)
#         time.sleep(1)

# start_timer(5)

SHOWBAR_COUNT_STOCK = '{"type": "show_snackbar", "text": "У вас 0 акции!"}'
x = 5

SHOWBAR_STOCK = SHOWBAR_COUNT_STOCK
SHOWBAR_STOCK.replace("У вас 0 акции!", f"У вас {x} акции")
print(SHOWBAR_COUNT_STOCK)
print(SHOWBAR_STOCK)