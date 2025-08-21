from datetime import datetime, timedelta

before = datetime.now()
input(" Rezdy -> ")
time_difference: timedelta = datetime.now() - before

seconds: float = time_difference.total_seconds()
print(f"{seconds:.2f}s")
